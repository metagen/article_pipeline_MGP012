#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import scipy.stats as st
import matplotlib.pyplot as plt
from collections import defaultdict


def parser_setting():
    """Setting parser."""
    parser = argparse.ArgumentParser(prog='calc_samesubject_diff_distance_matrix.py',
                                     description='description')
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File path of matrix')
    parser.add_argument('path_in_metadata',
                        action='store',
                        type=str,
                        help='File path of metadata')
    parser.add_argument('-ot', '--path_out_tsv',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output')
    parser.add_argument('-op', '--path_out_pdf',
                        action='store',
                        type=str,
                        default="output.pdf",
                        help='File path of output')
    # maybe timepoint
    parser.add_argument('-mk1', '--metadata_key1',
                        action='store',
                        type=str,
                        help='metadata key(to get distance)')
    parser.add_argument('-mv1', '--metadata_vals1',
                        action='store',
                        nargs='*',
                        type=str,
                        help='metadata value(to get distance)')
    # maybe group
    parser.add_argument('-mk2', '--metadata_key2',
                        action='store',
                        type=str,
                        help='metadata key(to get boxplot)')
    parser.add_argument('-mv2', '--metadata_vals2',
                        action='store',
                        nargs='*',
                        type=str,
                        help='metadata value(to get boxplot)')
    parser.add_argument('-c', '--colors',
                        action='store',
                        nargs='*',
                        type=str,
                        help='color codes')
    args = parser.parse_args()
    return vars(args)


def draw_boxplot(data, labels, colors=None, title=None, show_xlabel=None,
                 dict_plt_adjust=None):
    # main
    bp = plt.boxplot(data,
                     notch=0,
                     labels=labels,
                     sym='.',
                     widths=0.66,
                     vert=True, whis=1.5,
                     patch_artist=True,
                     flierprops={
                        "marker": "k",
                        "markerfacecolor": "k",
                        "markersize": 12,
                        "linestyle": "none",
                        "markeredgecolor": "k"
                     })

    # config - boxplot config
    # set boxplot line color
    lw = 1.5
    for box in bp['boxes']:
        box.set(color="black", linewidth=lw)
    for box in bp['medians']:
        plt.setp(box, color="black", linewidth=lw)
    for box in bp['caps']:
        plt.setp(box, color="black", linewidth=lw)
    for box in bp['whiskers']:
        plt.setp(box, ls="solid", color="black", linewidth=lw)

    # set boxplot color
    if colors is not None:
        for box, color in zip(bp["boxes"], colors):
            box.set_facecolor(color)
    else:
        for box in bp['boxes']:
            box.set_facecolor("white")

    # config - general plot config
    # set title
    if title is not None:
        plt.title(title)

    # set xlabel?
    # if not show_xlabel:
    plt.gca().tick_params(labelbottom=False, bottom=False)

    # set adjust?
    if dict_plt_adjust is not None:
        # default value is this
        # d = {"left": 0.125, "right": 0.9, "bottom": 0.1, "top": 0.9}
        plt.subplots_adjust(**dict_plt_adjust)

    # hidden migi and ue
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)

    # set about tick
    plt.tick_params(length=2, width=1.5, pad=0.5, top=False, right=False)


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


def main(args):
    # preprocess - read configs
    path_in_matrix = args["path_in_matrix"]
    path_in_metadata = args["path_in_metadata"]
    path_out_tsv = args["path_out_tsv"]
    path_out_pdf = args["path_out_pdf"]
    mk1 = args["metadata_key1"]
    mv1s = args["metadata_vals1"]
    mk2 = args["metadata_key2"]
    mv2s = args["metadata_vals2"]
    colors = args["colors"]

    # 一時変数
    dkey = "dist"

    # main - input
    df = pd.read_csv(path_in_matrix, sep="\t", index_col=0)
    me = pd.read_csv(path_in_metadata, sep="\t", index_col=0)

    if len(mv1s) != 2:
        assert ValueError("len(mv1s) == 2(Scriptが対応してない)")

    # main - mainprocess
    dd = defaultdict(lambda: defaultdict(int))
    sid_sets = get_samesubject_sampleids(me, mk1, mv1s, axis=0)
    sids_ctrl = []
    sids_test = []
    for sid_ctrl, sid_test in sid_sets:
        dd[sid_test][dkey] = df.loc[sid_ctrl, sid_test]
        if me.loc[mk2, sid_test] == mv2s[0]:
            sids_ctrl.append(sid_test)
        if me.loc[mk2, sid_test] == mv2s[1]:
            sids_test.append(sid_test)
    df = pd.DataFrame(dd)

    fig_width = 8
    fig_height = 6
    plt.subplots(figsize=(fig_width, fig_height))

    val_ctrl = df.loc[dkey, sids_ctrl]
    val_test = df.loc[dkey, sids_test]
    p = st.mannwhitneyu(val_ctrl, val_test, alternative="two-sided")[1]
    df_p = pd.DataFrame([f"# p-value of mannwhitneyu: {p}"])
    df_p.to_csv(path_out_tsv, index=False, header=False)
    df.to_csv(path_out_tsv, sep="\t", mode="a")

    vals = [val_ctrl, val_test]
    draw_boxplot(vals, mv2s, colors=colors)
    plt.yticks(fontsize=16)
    xmin, xmax = plt.xlim()
    plt.tight_layout()
    plt.savefig(path_out_pdf)


if __name__ == '__main__':
    main(parser_setting())
