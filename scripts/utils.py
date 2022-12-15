def query_col(df, key, val):
    return df.loc[:, df.loc[key, :] == val]


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
                from IPython.core.debugger import Pdb; Pdb().set_trace()
                print(subject_id, mval, mdf_ext_step1, mdf_ext_step2)
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
