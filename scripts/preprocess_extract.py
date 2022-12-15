#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd


def parser_setting():
    """Setting parser."""
    parser = argparse.ArgumentParser(prog='query.py',
                                     description='description')
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File path of matrix')
    parser.add_argument('path_in_metadata',
                        action='store',
                        type=str,
                        help='File path of metadata')
    parser.add_argument('-a', '--axis',
                        action='store',
                        type=int,
                        default=1,
                        choices=[0, 1, 2],
                        help='Extract axis(2 extract row and col in 1 time)')
    parser.add_argument('-o1', '--path_out_matrix',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output')
    parser.add_argument('-o2', '--path_out_metadata',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output')
    parser.add_argument('-mk', '--metadata_key',
                        action='store',
                        type=str,
                        help='metadata key')
    parser.add_argument('-mv', '--metadata_values',
                        action='store',
                        nargs='*',
                        type=str,
                        help='metadata value')
    args = parser.parse_args()
    return vars(args)


def extract_df(df, mdf, mkey, mvals, axis=1):
    if mkey not in mdf.index:
        raise ValueError("metadata key in not metadata")

    sample_ids = mdf.columns[mdf.loc[mkey, :].isin(mvals)]
    if len(sample_ids) == 0:
        raise ValueError("can't find sample_ids")

    if axis == 0:
        extracted_df = df.loc[sample_ids, :]
    if axis == 1:
        extracted_df = df.loc[:, sample_ids]
    if axis == 2:
        extracted_df = df.loc[sample_ids, sample_ids]
    extracted_mdf = mdf.loc[:, sample_ids]
    return extracted_df, extracted_mdf


def main(args):
    # preprocess - read configs
    path_in_matrix = args["path_in_matrix"]
    path_in_metadata = args["path_in_metadata"]
    path_out_matrix = args["path_out_matrix"]
    path_out_metadata = args["path_out_metadata"]
    mkey = args["metadata_key"]
    mvals = args["metadata_values"]
    axis = args["axis"]

    # main - input
    df = pd.read_csv(path_in_matrix, sep="\t", index_col=0, comment="#")
    mdf = pd.read_csv(path_in_metadata, sep="\t", index_col=0, comment="#")

    # main - mainprocess
    if len(df.columns) != len(mdf.columns):
        print(len(df.columns), len(mdf.columns))
        raise ValueError("in_matrix and in_metadata header length is not same")

    df_ext, mdf_ext = extract_df(df, mdf, mkey, mvals, axis=axis)

    df_ext.to_csv(path_out_matrix, sep="\t")
    mdf_ext.to_csv(path_out_metadata, sep="\t")


if __name__ == '__main__':
    main(parser_setting())
