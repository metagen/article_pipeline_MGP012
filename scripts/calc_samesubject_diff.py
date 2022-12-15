#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
from utils import get_samesubject_sampleids


def parser_setting():
    """Setting parser."""
    parser = argparse.ArgumentParser(prog='calc_samesubject_diff.py',
                                     description='description')
    parser.add_argument('path_in_matrix',
                        action='store',
                        type=str,
                        help='File path of matrix')
    parser.add_argument('path_in_metadata',
                        action='store',
                        type=str,
                        help='File path of metadata')
    parser.add_argument('-o1', '--path_out_matrix',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output matrix')
    parser.add_argument('-o2', '--path_out_metadata',
                        action='store',
                        type=str,
                        default="output.tsv",
                        help='File path of output metadata')
    parser.add_argument('-mk', '--metadata_key',
                        action='store',
                        type=str,
                        default="timepoint2",
                        help='metadata key 1')
    parser.add_argument('-msk', '--metadata_subject_key',
                        action='store',
                        type=str,
                        default="subject_id",
                        help='metadata key 2')
    parser.add_argument('-mv1', '--metadata_values1',
                        action='store',
                        nargs="*",
                        default=["C1", "T1"],
                        type=str,
                        help='metadata value')
    parser.add_argument('-mv2', '--metadata_values2',
                        action='store',
                        nargs='*',
                        default=["C3", "T3"],
                        type=str,
                        help='metadata value')
    args = parser.parse_args()
    return vars(args)


def main(args):
    path_in_matrix = args["path_in_matrix"]
    path_in_metadata = args["path_in_metadata"]
    path_out_matrix = args["path_out_matrix"]
    path_out_metadata = args["path_out_metadata"]
    mkey = args["metadata_key"]
    mskey = args["metadata_subject_key"]
    mv1s = args["metadata_values1"]
    mv2s = args["metadata_values2"]

    df = pd.read_csv(path_in_matrix, sep="\t", header=0, index_col=0)
    me = pd.read_csv(path_in_metadata, sep="\t", header=0, index_col=0)

    out_df = pd.DataFrame()
    out_me = pd.DataFrame()

    for mv1, mv2 in zip(mv1s, mv2s):
        (sid_ctrls, sid_tests), subject_ids = get_samesubject_sampleids(me, mkey, [mv1, mv2], msk=mskey, return_subjectid=True)
        for sid_ctrl, sid_test, subject_id in zip(sid_ctrls, sid_tests, subject_ids):
            new_sid = f"{subject_id}_{mv2}{mv1}"
            out_df[new_sid] = df[sid_test] - df[sid_ctrl]

            for ind in me.index:
                val_ctrl = me.loc[ind, sid_ctrl]
                val_test = me.loc[ind, sid_test]
                if val_ctrl == val_test:
                    out_me.loc[ind, new_sid] = val_ctrl
                else:
                    out_me.loc[ind, new_sid] = f"{val_test}{val_ctrl}"

    out_df.to_csv(path_out_matrix, sep="\t")
    out_me.to_csv(path_out_metadata, sep="\t")


if __name__ == '__main__':
    main(parser_setting())
