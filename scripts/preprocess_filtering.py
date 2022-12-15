#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd


def parser_setting():
    """Setting parser."""
    parser = argparse.ArgumentParser(prog='filtering.py',
                                     description='description')
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File path of matrix')
    parser.add_argument('-o', '--path_out_tsv',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output')
    parser.add_argument('-m', '--method',
                        action='store',
                        type=str,
                        choices=['mean', 'freq'],
                        help='filtering method')
    parser.add_argument('-c', '--cutoff',
                        action='store',
                        type=float,
                        help='Cutoff of mean/freq')
    args = parser.parse_args()
    return vars(args)


def main(args):
    # preprocess - read configs
    path_in_matrix = args["path_in_matrix"]
    path_out_tsv = args["path_out_tsv"]
    method = args["method"]
    cutoff = args["cutoff"]

    # main - input
    df = pd.read_csv(path_in_matrix, sep="\t", index_col=0, comment="#")

    # main - mainprocess
    if method == "mean":
        df = df.loc[df.mean(axis=1) >= cutoff, :]
    if method == "freq":
        df = df.loc[(df == 0.0).sum(axis=1) < (1 - cutoff) * len(df.columns), :]

    # main - output
    df.to_csv(path_out_tsv, sep="\t")


if __name__ == '__main__':
    main(parser_setting())
