#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import argparse
import warnings
import numpy as np
import pandas as pd
import pingouin as pg
import scipy.stats as st
import matplotlib.pylab as plt
from adjustText import adjust_text
warnings.filterwarnings("ignore")


def parser_setting():
    """Set Parser."""
    parser = argparse.ArgumentParser(
        prog='volcano_plot.py',
        description='description')
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File path of matrix')
    parser.add_argument('path_in_metadata',
                        action='store',
                        type=str,
                        help='File path of metadata')
    parser.add_argument('-o', '--path_out_pdf',
                        action='store',
                        default='volcano_plot.pdf',
                        type=str,
                        help='File path of output')
    parser.add_argument('-o2', '--path_out_pdf2',
                        action='store',
                        default='volcano_plot.annotate.pdf',
                        type=str,
                        help='File path of output(annotate in sig diff)')
    parser.add_argument('-ot', '--path_out_txt',
                        action='store',
                        default='/dev/null',
                        type=str,
                        help='File path of output(coordinate)')
    parser.add_argument('-mk', '--metadata_key',
                        action='store',
                        type=str,
                        help='metadata key')
    parser.add_argument('-msk', '--metadata_subject_key',
                        action='store',
                        type=str,
                        help='metadata subject key')
    parser.add_argument('-mv1', '--metadata_value1',
                        action='store',
                        type=str,
                        help='metadata_values(Ctrl)')
    parser.add_argument('-mv2', '--metadata_value2',
                        action='store',
                        type=str,
                        help='metadata_values(Test)')
    parser.add_argument('--paired',
                        action='store_true',
                        help='metadata_values(Test)')
    parser.add_argument('--adjust_text',
                        action='store_true',
                        help='adjust_text')
    args = parser.parse_args()
    return vars(args)


def get_samesubject_sampleids(mdf, mkey, mvals, msk="subject_id", axis=1, return_subjectid=False):
    """
    import pandas as pd
    mdf = pd.DataFrame({
        "01_A": ["01", "A"],
        "01_B": ["01", "B"],
        "02_A": ["02", "A"],
        "02_B": ["02", "B"],
    }, index=["subject_id", "group"])
    >>> get_samesubject_sampleids(mdf, "group", ["A", "B"])
    [['01_A', '02_A'], ['01_B', '02_B']]
    >>> get_samesubject_sampleids(mdf, "group", ["A", "B"], axis=0)
    [['01_A', '01_B'], ['02_A', '02_B']]
    """
    def query_col(df, key, val):
        return df.loc[:, df.loc[key, :] == val]

    m = "metadata table is not unique by -mk and -msk"
    subject_ids = sorted(set(mdf.loc[msk, :]))
    sample_ids = []
    for mval in mvals:
        _sample_ids = []
        for subject_id in subject_ids:
            mdf_ext_step1 = query_col(mdf, msk, subject_id)
            mdf_ext_step2 = query_col(mdf_ext_step1, mkey, mval)
            if mdf_ext_step2.shape[1] != 1:
                raise ValueError(m)
            _sample_ids.append(mdf_ext_step2.columns[0])
        sample_ids.append(_sample_ids)

    if return_subjectid and axis == 1:
        return sample_ids, subject_ids
    elif not return_subjectid and axis == 1:
        return sample_ids
    elif return_subjectid and axis == 0:
        return [list(x) for x in zip(*sample_ids)], subject_ids
    elif not return_subjectid and axis == 0:
        return [list(x) for x in zip(*sample_ids)]


def plot_volcano(xs, ys, indexes, path_out_pdf, annotate=False, flag_adjust_text=False):
    plt.figure(figsize=(8, 7))
    xs_gray = []
    ys_gray = []
    xs_blue = []
    ys_blue = []
    for x, y, ind in zip(xs, ys, indexes):
        if y >= -np.log10(0.05):
            ys_blue.append(y)
            xs_blue.append(x)
        else:
            ys_gray.append(y)
            xs_gray.append(x)

    plt.scatter(xs_gray, ys_gray, marker="o", c="gray")
    plt.scatter(xs_blue, ys_blue, marker="o", c="blue")

    plt.tick_params(top=False, right=False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)

    list_plt_texts = []
    if annotate:
        for x, y, ind in zip(xs, ys, indexes):
            if abs(x) > 0.4 and y >= -np.log10(0.05):
                # plt.annotate(ind, xy=(x, y))
                list_plt_texts.append(plt.text(x, y, ind))

    if flag_adjust_text:
        adjust_text(list_plt_texts, arrowprops=dict(arrowstyle='->', color='gray'))
    ymin_old, ymax_old = plt.ylim()
    xmin_old, xmax_old = plt.xlim()

    if abs(xmax_old) >= abs(xmin_old):
        xmin_old = -1 * xmax_old
    if abs(xmax_old) <= abs(xmin_old):
        xmax_old = -1 * xmin_old

    plt.hlines(y=-np.log10(0.05), xmin=xmin_old, xmax=xmax_old, color="gray", linestyles='dashed')
    plt.vlines(x=0, ymin=-0.1, ymax=ymax_old, color="gray", linestyles='dashed')
    plt.gca().set_xlim([xmin_old, xmax_old])
    plt.gca().set_ylim([-0.1, ymax_old])

    # plt.tight_layout()
    plt.savefig(path_out_pdf)
    plt.clf()


def main(args):
    """Main function."""
    path_in_matrix = args["path_in_matrix"]
    path_in_metadata = args["path_in_metadata"]
    path_out_pdf = args["path_out_pdf"]
    path_out_pdf2 = args["path_out_pdf2"]
    path_out_txt = args["path_out_txt"]
    mkey = args["metadata_key"]
    mval1 = args["metadata_value1"]
    mval2 = args["metadata_value2"]
    paired = args["paired"]
    flag_adjust_text = args["adjust_text"]

    opts = {"sep": "\t", "index_col": 0, "comment": "#"}
    df = pd.read_csv(path_in_matrix, **opts)
    mdf = pd.read_csv(path_in_metadata, **opts)

    if paired:
        sample_ids_mv1, sample_ids_mv2 = get_samesubject_sampleids(mdf, mkey, [mval1, mval2])
    else:
        sample_ids_mv1 = mdf.T.query(f"{mkey} == '{mval1}'").index
        sample_ids_mv2 = mdf.T.query(f"{mkey} == '{mval2}'").index

    xs = []
    ys = []
    indexes = []
    for ind in df.index:
        v1 = df.loc[ind, sample_ids_mv1]
        v2 = df.loc[ind, sample_ids_mv2]
        x = pg.compute_effsize(v2, v1, paired=False, eftype='hedges')
        xs.append(x)
        indexes.append(ind)

        if paired:
            p = st.wilcoxon(v1, v2)[1]
        else:
            p = st.mannwhitneyu(v1, v2, alternative="two-sided")[1]
        if math.isnan(p):
            p = 1.00
        ys.append(-np.log10(p))

    df_out = pd.DataFrame({"x": xs, "y": ys})
    df_out.index = indexes
    df_out.to_csv(path_out_txt, sep="\t")

    plot_volcano(xs, ys, indexes, path_out_pdf, annotate=False, flag_adjust_text=flag_adjust_text)
    plot_volcano(xs, ys, indexes, path_out_pdf2, annotate=True, flag_adjust_text=flag_adjust_text)


if __name__ == '__main__':
    main(parser_setting())
