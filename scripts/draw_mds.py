#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import numpy.linalg as la
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from matplotlib.font_manager import FontProperties

sns.set_style("whitegrid")
n_components = 2


def parser_setting():
    parser = argparse.ArgumentParser(
        prog='mds.py',
        description='multi-dimensional scaling'
    )
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File name of matrix')
    parser.add_argument('path_in_metadata',
                        action='store',
                        type=str,
                        help='File name of metadata')
    parser.add_argument('-o', '--path_out_pdf',
                        action='store',
                        default='/dev/null',
                        type=str,
                        help='pdf-output directory path')
    parser.add_argument('-ot', '--path_out_txt',
                        action='store',
                        type=str,
                        default="/dev/null",
                        help='tsv-output directory path')
    parser.add_argument('-mk', '--metadata_key',
                        action='store',
                        type=str,
                        default='all',
                        help='metadata key')
    parser.add_argument('-c', '--color_dict_path',
                        action='store',
                        type=str,
                        default=None,
                        help='color correspond dictionary"s path.')
    parser.add_argument('--del_label',
                        dest='del_label',
                        action='store_true',
                        default=False,
                        help='Add sample_label for plot.')
    parser.add_argument('-xmax', '--xmax',
                        action='store',
                        type=float,
                        default=None,
                        help='show x limit(max)')
    parser.add_argument('-xmin', '--xmin',
                        action='store',
                        type=float,
                        default=None,
                        help='show x limit(min)')
    parser.add_argument('-ymax', '--ymax',
                        action='store',
                        type=float,
                        default=None,
                        help='show y limit(max)')
    parser.add_argument('-ymin', '--ymin',
                        action='store',
                        type=float,
                        default=None,
                        help='show y limit(min)')
    parser.add_argument('--hidden_legend',
                        action='store_true',
                        default=False,
                        help='Hidden legend or not')
    args = parser.parse_args()
    return vars(args)


def _MDS(dist):
    mds = MDS(
        n_components=n_components,
        max_iter=3000,
        dissimilarity="precomputed",
        n_jobs=1,
        random_state=42
    )
    positions = mds.fit(dist).embedding_
    return positions


def explained_variance_ratio(dist):
    A = dist
    A = A**2
    n = A.shape[0]
    J_c = 1./n*(np.eye(n) - 1 + (n - 1) * np.eye(n))
    B = -0.5 * (J_c.dot(A)).dot(J_c)
    eigen_val = la.eig(B)[0]
    eigen_val_sorted = pd.Series(eigen_val).sort_values(ascending=False)
    eigen_val_sorted_rel = eigen_val_sorted / np.sum(eigen_val)
    return eigen_val_sorted_rel.values[0], eigen_val_sorted_rel.values[1]


def mardia(dist):
    A = dist
    A = A**2
    n = A.shape[0]
    J_c = 1./n*(np.eye(n) - 1 + (n - 1) * np.eye(n))
    B = -0.5 * (J_c.dot(A)).dot(J_c)

    eigen_val = la.eig(B)[0]
    # eigen_vec = la.eig(B)[1].T

    eigen_val_sorted = pd.Series(eigen_val).sort_values(ascending=False)
    eigen_val_sorted = eigen_val_sorted / np.sum(eigen_val)
    return eigen_val_sorted.values[0], eigen_val_sorted.values[1]

    eigen_val_positive = eigen_val[eigen_val > 0]
    eigen_val_double = np.power(eigen_val_positive, 2)
    mardia1 = np.sum(eigen_val_positive[:n_components]) / \
        np.sum(eigen_val_positive)
    mardia2 = np.sum(eigen_val_double[:n_components]) / \
        np.sum(eigen_val_double)

    return mardia1, mardia2


def set_xylim(xmin, xmax, ymin, ymax):
    if xmin is not None or xmax is not None:
        if xmin is None:
            xmin = plt.xlim()[0]
        if xmax is None:
            xmax = plt.xlim()[1]
        plt.gca().set_xlim([xmin, xmax])

    if ymin is not None or ymax is not None:
        if ymin is None:
            ymin = plt.ylim()[0]
        if ymax is None:
            ymax = plt.ylim()[1]
        plt.gca().set_ylim([ymin, ymax])


def metadata_coloring(mvals, colorset='hls'):
    """A mvals = metadata_value_set."""
    dict_keys = mvals
    dict_values = sns.color_palette("hls", len(mvals))
    return dict(zip(dict_keys, dict_values))


def main(args):
    path_in_matrix = args["path_in_matrix"]
    path_in_metadata = args["path_in_metadata"]
    path_out_pdf = args["path_out_pdf"]
    path_out_txt = args["path_out_txt"]
    mkey = args["metadata_key"]
    color_dict_path = args["color_dict_path"]
    del_label = args["del_label"]
    xmax, xmin = args["xmax"], args["xmin"]
    ymax, ymin = args["ymax"], args["ymin"]
    hidden_legend = args["hidden_legend"]

    # read table
    df = pd.read_csv(path_in_matrix, sep="\t", index_col=0, comment="#")
    mdf = pd.read_csv(path_in_metadata, sep="\t", index_col=0, comment="#")

    # execute PCoA
    positions = _MDS(df)
    # mardia1, mardia2 = mardia(df)
    pc1_exp_ratio, pc2_exp_ratio = explained_variance_ratio(df)
    pc1_exp_ratio = '{:.1f}'.format(pc1_exp_ratio*100)
    pc2_exp_ratio = '{:.1f}'.format(pc2_exp_ratio*100)

    # get color_dict
    mvals = mdf.loc[mkey, :]
    mval_set = list(sorted(set(mvals)))
    color_dict = metadata_coloring(mval_set)
    if color_dict_path:
        df_color = pd.read_csv(color_dict_path, sep="\t", index_col=0, header=None)
        color_dict = df_color[1].to_dict()

    # prepare vars to output and plot
    df_positions = pd.DataFrame(positions)
    df_positions.index = df.index
    df_positions.columns = ["PC1", "PC2"]
    df_positions[mkey] = [mdf.loc[mkey, ind] for ind in df.index]
    df_positions["color"] = [color_dict[mval] for mval in df_positions[mkey]]

    # output position
    df_positions.to_csv(path_out_txt, sep="\t")

    # plot prepare
    sns.set(style='whitegrid', color_codes=True)
    plt.figure(figsize=(8, 6))

    # plot scatter plot and label(label is option)
    for color in set(df_positions["color"]):
        df_pos_q = df_positions.loc[df_positions.loc[:, "color"] == color, :]
        x = df_pos_q["PC1"]
        y = df_pos_q["PC2"]
        mval = df_pos_q.loc[df_pos_q.index[0], mkey]
        plt.scatter(x, y, c=color, s=40, label=mval, ec="gray")
        # plt.plot(x, y, color="gray")

    if not del_label:
        for ind in df_positions.index:
            x = df_positions.loc[ind, "PC1"]
            y = df_positions.loc[ind, "PC2"]
            plt.text(x, y, ind, fontsize="small") # , size=6

    # plot legend
    # ref: https://symfoware.blog.fc2.com/blog-entry-1418.html
    # if not hidden_legend:
    fp = FontProperties(size=8)
    plt.legend(
        prop=fp,
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        borderaxespad=0
    )

    if hidden_legend:
        plt.gca().get_legend().remove()

    plt.title('')
    plt.xlabel(f"PC 1 ({pc1_exp_ratio} %)")
    plt.ylabel(f"PC 2 ({pc2_exp_ratio} %)")

    # set x/y min/max
    set_xylim(xmin, xmax, ymin, ymax)

    # comment: need adjust?
    plt.subplots_adjust(right=0.80)
    plt.tight_layout()
    plt.savefig(path_out_pdf)
    plt.clf()


if __name__ == '__main__':
    main(parser_setting())
