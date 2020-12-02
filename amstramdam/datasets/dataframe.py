import pandas as pd
import numpy as np


def create_mask(df, filter):
    # Column to use for filtering
    col = filter["column"]
    assert col in df.columns, f"Unknown column '{col}'. Valid columns are {df.columns}"
    # Values to use for filtering
    values = filter.get("values", None)
    if filter.get("method", None) is not None:
        method = filter["method"]
    elif isinstance(values, (list, tuple, set)):
        method = "isin"
    else:
        method = "eq"
    return getattr(df[col], method)(values)

def create_masks(df, filters):
    masks = None
    for filter in filters:
        # TODO: support OR and AND masking with recursivity
        mask = create_mask(df, filter)
        if masks is None:
            masks = mask
        else:
            masks = masks & mask
    return masks

def mask_df(df, filters):
    masks = create_masks(df, filters)
    return df if masks is None else df.loc[masks]

def autorank(df, column, ranks, reverse=False):
    """Create G0, G1, Gi groups on-the-fly, from a list of group sizes"""
    if len(ranks) == 0:
        df.loc[:, "group"] = 0
        params = dict(available_levels=1)
        return df, params
    if ranks[-1] == "all":
        ranks[-1] = len(df)
    def get_rank(r):
        for i, threshold in enumerate(ranks):
            if r < threshold: return i
        return len(ranks)
    df.loc[:, "local_rank"] = np.argsort(-df[column].fillna(0))
    df.loc[:, "group"] = df["local_rank"].map(get_rank)

    params = dict(available_levels=len(ranks))
    return df, params

class DataFrameLoader(object):
    # List here the file that should be kept in memory
    persistent = {
        "data/places.world.csv"
    }

    def __init__(self, dataframes=None):
        if dataframes is None:
            dataframes = dict()
        self._dataframes = dataframes

    def __contains__(self, item):
        return item in self._dataframes

    def __len__(self):
        return len(self._dataframes)

    def load(self, filename, persist=False, **kwargs):
        df = pd.read_csv(filename, index_col=0, **kwargs)
        df = df.fillna(0)
        if "pid" not in df.columns:
            df["pid"] = df.index
        if persist:
            self.persistent.add(filename)
        if filename in self.persistent:
            self._dataframes[filename] = df
        return df

    def __getitem__(self, filename):
        if filename in self._dataframes:
            return self._dataframes[filename]
        return self.load(filename)

    def __delitem__(self, filename):
        del self._dataframes[filename]

    def edit(self, filename, created, updated):
        """
        filename: original DF filename
        inserted: list of inserted records. Each record is a dict whose keys are the columns of
        DF, and values are the corresponding values
        changed: a dictionnary from pids to changes. For each pid, changed[pid] is a dictionnary
        mapping changed columns to their new values
        """
        df = self.load(filename, persist=False)
        types = {col: df[col].dtype for col in df.columns}
        if created:
            added = pd.DataFrame.from_records(created, index=[o["pid"] for o in created])
            added = added.astype(types)
            df = df.append(added, verify_integrity=True)
        for pid, changes in updated.items():
            pid = int(pid)
            for col, value in changes.items():
                casted_value = np.array([value], dtype=types.get(col))
                df.loc[pid, col] = casted_value
        df = df.drop(columns=["pid"])
        return df


