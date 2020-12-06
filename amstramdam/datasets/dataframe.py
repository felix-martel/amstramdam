import pandas as pd
import numpy as np

from amstramdam.game.geo import Point


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
        df = pd.read_csv(filename, **kwargs)
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

class UnifiedDataFrame:
    def __init__(self, df, mask=None, col_place="city", col_hint="admin", col_lon="lng", col_lat="lat", col_group="group",
                 col_rank="population", use_hint=True, single_group=False, special_char="!"):
        self.df = df
        self.mask = mask if mask is not None else pd.Series(True, index=self.df.index)
        self.converter = {k: v for k, v in zip(
            ["place", "hint", "lon", "lat", "group", "rank"],
            [col_place, col_hint, col_lon, col_lat, col_group, col_rank]
        )}
        self.use_hint = use_hint and col_hint in self.df.columns
        self.single_group = single_group or col_group not in self.df.columns

        self.SPE = special_char

    def unify_df(self, df):
        new_mask = self.mask.reindex_like(df) # & pd.Series(True, index=self.df.index)
        return UnifiedDataFrame(df, mask=new_mask,
                                col_place=self.col("place"),
                                col_hint=self.col("hint"),
                                col_lon=self.col("lon"),
                                col_lat=self.col("lat"),
                                col_group=self.col("group"),
                                col_rank=self.col("rank"),
                                use_hint=self.use_hint,
                                single_group=self.single_group,
                                special_char=self.SPE
                                )

    def _col(self, key):
        if key.startswith(self.SPE):
            return key[len(self.SPE):]
        return self.converter.get(key, key)

    def col(self, *keys):
        converted = [self._col(key) for key in keys]
        if len(keys) == 1:
            return converted[0]
        return converted

    @property
    def reversed_converter(self):
        return {v: k for k, v in self.converter.items()}

    def __len__(self):
        return len(self.df.loc[self.mask])

    def __getitem__(self, key):
        if isinstance(key, list):
            keys = self.col(*key)
            return self.df.loc[self.mask, keys]
        elif isinstance(key, pd.Series):
            return self.unify_df(self.df.loc[self.mask & key])
        return self.df[self.mask, self.col(key)]

    def __getattr__(self, attr):
        own_attr = set(dir(self))
        df_attr = set(dir(self.df))
        if attr in df_attr - own_attr:
            return getattr(self.df.loc[self.mask], attr)
        # Raise an error
        raise AttributeError(f"Unknown method '{attr}' for UnifiedGameMap")

    def sample(self, *args, **kwargs):
        sampled = self.df.loc[self.mask].sample(*args, **kwargs)
        return self.unify_df(sampled)

    def to_dict(self, *args, renamed=True, **kwargs):
        if not renamed:
            return self.df.loc[self.mask].to_dict(*args, **kwargs)
        renamed = self.df.loc[self.mask].rename(columns=self.reversed_converter)
        if "hint" not in renamed.columns:
            renamed = pd.concat([renamed, pd.Series("", index=renamed.index, name="hint")], axis="columns")
        if "group" not in renamed.columns:
            renamed = pd.concat([renamed, pd.Series(0, index=renamed.index, name="group")], axis="columns")
        return renamed.to_dict(*args, **kwargs)

    @property
    def place(self):
        return self.df.loc[self.mask, self.col("place")]

    @property
    def hint(self):
        if not self.use_hint:
            return pd.Series("", index=self.df.index)
        return self.df.loc[self.mask, self.col("hint")]

    @property
    def group(self):
        if self.single_group:
            return pd.Series(0, index=self.df.index)
        return self.df.loc[self.mask, self.col("group")]

    @property
    def lon(self):
        return self.df.loc[self.mask, self.col("lon")]

    @property
    def lat(self):
        return self.df.loc[self.mask, self.col("lat")]

    @property
    def rank(self):
        return self.df.loc[self.mask, self.col("rank")]

    def jsonify_record(self, record):
        return {self.col(k): v for k, v in record.items()}

    def guessify_record(self, record):
        if not self.use_hint:
            hint = ""
        else:
            hint = record[self.col("hint")]
        place, lon, lat = (record[key] for key in self.col("place", "lon", "lat"))
        return ((place, hint), Point(lon, lat))
