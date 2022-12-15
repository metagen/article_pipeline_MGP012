#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import pandas as pd
from scipy.spatial.distance import pdist, squareform


def parser_setting():
    parser = argparse.ArgumentParser(prog='distance_matrix.py',
                                     description='matrix to distance matrix')
    parser.add_argument('path_in_tsv',
                        action='store',
                        type=str,
                        help='File name of matrix')
    parser.add_argument('-o', '--path_out_tsv',
                        action='store',
                        type=str,
                        default='output.tsv',
                        help='output directory path')
    parser.add_argument('-m', '--metric',
                        action='store',
                        type=str,
                        default='spearman',
                        choices=[
                            'pearson',
                            'spearman',
                            'jensenshannon',
                            'euclidean',
                            'braycurtis'
                        ],
                        help='metric for distance calculation')
    args = parser.parse_args()
    return vars(args)


def main(args):
    # main - input
    path_in_matrix = args["path_in_tsv"]
    path_out_tsv = args["path_out_tsv"]
    metric = args["metric"]
    df = pd.read_csv(path_in_matrix, sep="\t", index_col=0)

    # main - mainprocess
    if metric in ["pearson", "spearman"]:
        df_dist = 1 - df.corr(metric)
    else:
        val_dist = squareform(pdist(df.T, metric))
        df_dist = pd.DataFrame(val_dist, index=df.columns, columns=df.columns)

    # main - output
    df_dist.to_csv(path_out_tsv, sep="\t")


if __name__ == '__main__':
    main(parser_setting())
