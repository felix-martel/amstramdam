import io
import os
import glob
import warnings
from datetime import datetime
from pprint import pprint
from copy import deepcopy
from typing import Any, Optional, Union, Iterable, Mapping

import pandas as pd
from bidict import bidict

from .game_map import GameMap
from .dataframe import (
    DataFrameLoader,
    mask_df,
    autorank,
    UnifiedDataFrame,
    create_masks,
)
from .codes import read_code
from ._loader import DEFAULTS, open_json, merge, process
from .types import DatasetParams, FlattenedDatasets, GroupedDatasets, PointChangeRecords, DatasetInformation, \
    DatasetGroup, FilteredGroupedDatasets

codes = read_code("data/codes.txt")


def analyze_country(df: pd.DataFrame, code: str, col: str="population") -> dict[str, Any]:
    sdf = df.loc[df.iso2 == code]
    if "group" in sdf.columns and len(sdf[sdf.group <= 2]) >= 10:
        # Places are already grouped, no re-ranking
        return dict()
    # Automatic auto-ranking
    n3 = len(sdf)
    if n3 <= 20:
        # Less than 20 places: only one difficulty level
        ranks = [1, 5, "all"]
    elif n3 <= 40:
        # Between 20 and 40 places: only two difficulty levels
        ranks = [2, 5, 15, "all"]
    else:
        # Above 40 places: three difficulty levels
        n0 = 15
        n2 = min(90, n3)
        n1 = round(2 / (1 / n0 + 1 / n2))
        ranks = [2, 5, n0, n1, n2]

    return dict(autorank=dict(column=col, ranks=ranks), available_levels=len(ranks))


DEFAULT_PARAMS: dict[str, Any] = dict(
    col_place="city",
    col_hint="admin",
    col_lon="lng",
    col_lat="lat",
    col_rank="population",
    default_level=0,
    harshness=0.7,
    use_hint=True,
    single_group=False,
    levels=[
        dict(label="Facile", weights=[1]),
        dict(label="Moyen", weights=[1, 1]),
        dict(label="Difficile", weights=[1, 1, 0.5]),
    ],
)


class Dataloader(object):
    GSYSTEM: str = "__gsystem__"
    GCOUNTRIES: str = "__countries__"
    LEGACY_SYSTEM: str = "__legacy__"

    SCALE_WORLD: int = 0
    SCALE_CONTINENT: int = 1
    SCALE_COUNTRY: int = 2

    DISTRIB_SYMBOL: str = "*"

    processing_methods: dict[str, str] = {
        GSYSTEM: "_process_grouped_map",
        GCOUNTRIES: "_build_country_maps",
        LEGACY_SYSTEM: "_process_standard_map",
    }

    def __init__(self, datasets: str):
        self.dataframes = DataFrameLoader()
        self.presets: Optional[DatasetParams] = None
        self.datasets: GroupedDatasets = self.process_json(datasets)
        self.flattened: FlattenedDatasets = {
            item["map_id"]: dict(group=G["group"], **item)
            for G in self.datasets
            for item in G["maps"]
        }

    def _distribute_to_levels(self, params: DatasetParams) -> DatasetParams:
        """
        Distribute values among levels. A params dict is supposed to look like this:
        params = {
            "use_hint": True,
            "harshness": 0.7,
            "levels": [
                {"label": "Easy", "weights": [1, 0.5]}, {"label": "Hard", "weights": [0.2, 0.5]}
            ]
        }
        The "levels" entry contains a list of difficulty levels (easiest -> hardest). Each level
        can define its own value for each possible parameter (use_hint, label, harshness...). But
        we also allow the following syntactic sugar:
        params = {
            ...
            "label*": ["Easy", "Hard"]
        }
        which is equivalent to declaring "levels"=[{"label": "Easy}, {"label": "Hard"}]. This
        distributivity is indicated by the trailing "*" symbol in the key. Here, we distribute
        such key, value pairs to the corresponding levels.
        """
        # print("DISTRIBUTING", params.get("name", "<unknown>"))
        params = params.copy()
        # pprint(params)
        distributed_cols = [k for k in params if k.endswith(self.DISTRIB_SYMBOL)]
        distributed_vals = [params[k] for k in distributed_cols]
        if distributed_cols:
            numbers_of_levels = set(map(len, distributed_vals))
            assert len(numbers_of_levels) == 1, (
                "All distributed parameters (indicated by the trailing '*' "
                "symbol) must have the same length in 'datasets.json'"
            )
            n_levels = numbers_of_levels.pop()
        if "levels" not in params:
            if not distributed_cols:
                # Nothing to distribute, return 'params' untouched
                # print("nothing to distribute")
                return params
            else:
                # print(n_levels, "levels found, filling with None")
                levels = [None] * n_levels
        else:
            levels = params["levels"]
        levels = [level if level is not None else dict() for level in levels] # type: ignore
        protected_columns = {"file", "name", "map_id", "levels"}

        for k in distributed_cols:
            values = params.pop(k)
            k = k[: -len(self.DISTRIB_SYMBOL)]
            for level, value in enumerate(values):
                levels[level][k] = value # type: ignore
        for k in params.keys() - protected_columns:
            for i in range(len(levels)):
                levels[i][k] = params[k] # type: ignore
        params["levels"] = levels

        # print("TO:")
        # pprint(params)
        return params

    def _merge(self, params: DatasetParams, defaults: DatasetParams) -> DatasetParams:
        # print(f"Merging <{params}> with <{defaults}>")
        # Here are the keys that should not be distributed to levels
        protected_keys = {"file", "name", "map_id"}
        if not params:
            return deepcopy(defaults)

        params = self._distribute_to_levels(params)
        defaults = self._distribute_to_levels(defaults)
        levels = params.pop("levels", None)
        default_levels = defaults.pop("levels", None)
        if levels is None and default_levels is None:
            return {**defaults, **params}
        new_levels = []
        if levels is None and default_levels is not None:
            for level in default_levels:
                new_level = {**level}
                for k in params.keys() - protected_keys:
                    new_level[k] = params[k]
                new_levels.append(new_level)
        else:
            for level in levels:
                if level is None:
                    level = dict()
                new_level = {**level}
                for k in (
                    defaults.keys() - params.keys() - level.keys() - protected_keys
                ):
                    new_level[k] = defaults[k]
                for k in params.keys() - level.keys() - protected_keys:
                    new_level[k] = params[k]
                new_levels.append(new_level)
        return {**defaults, **params, "levels": new_levels}

    def merge_params(self, common_params: DatasetParams, preset_params: DatasetParams, default_params: DatasetParams) -> DatasetParams:
        print(common_params["name"])
        presetted = self._merge(preset_params, default_params)
        print("--PRESETTED--")
        pprint(presetted)
        print("\n--INITIAL--")
        pprint(common_params)
        merged = self._merge(common_params, presetted)
        print("\n--MERGED--")
        pprint(merged)
        print("")
        return merged

    def load(self, name: str, level: Optional[int]=None, **params: Any) -> GameMap:
        map_params = self.flattened[name].copy()
        return self._load(map_params, level)

    def _load(self, map_params: DatasetParams, level: Optional[int]=None) -> GameMap:
        map_params = deepcopy(map_params)
        if level is None:
            # raise ValueError("Passing level=None to dataloader.load is not supported yet")
            # TODO: when level is None, return a mix of points for all levels in some way
            level = map_params.get("default_level", 0)
        try:
            datafile = map_params.pop("file")
            name = map_params.pop("name")
            map_id = map_params.pop("map_id")
            params = map_params["levels"][level].copy()
            # pprint(params)
            filters = params.pop("filters")
            columns = {
                col: params.pop(col)
                for col in [
                    "col_place",
                    "col_hint",
                    "col_rank",
                    "col_lon",
                    "col_lat",
                    "col_group",
                    "use_hint",
                    "single_group",
                ]
            }
            df = self.dataframes[datafile]
            mask = create_masks(df, filters)
            udf = UnifiedDataFrame(df, mask, **columns)
            return GameMap(name, map_id, udf, **params)
        except Exception as e:
            raise e

    def commit_changes(self, name: str, changes: PointChangeRecords) -> Optional[tuple[Union[pd.DataFrame, io.BytesIO], str]]:
        if name not in self.flattened:
            raise KeyError(name)
        created = changes.get("create", [])
        updated = changes.get("update", {})
        output = changes.get("output", "save")

        filename = self.flattened[name].get("file")
        if filename is None:
            warnings.warn(
                f"Dataset '{name} can't be edited because it doesn't have"
                "a registered 'file'. Please change 'datasets.json' and"
                "add a 'file' key."
            )
            return None

        df = self.dataframes.edit(filename, created, updated)

        root, ext = os.path.splitext(filename)
        timestamp = f"{datetime.now():%d-%m-%Y_%Hh%M}"
        new_filename = root + "_edited_" + timestamp + ext
        _, short_filename = os.path.split(new_filename)
        if output == "save":
            df.to_csv(new_filename)
            print("New df saved in", new_filename)
            return df, short_filename
        elif output == "download":
            raw = df.to_csv().encode("utf-8")
            file = io.BytesIO(raw)
            return file, short_filename
        else:
            raise ValueError(f"Unknwon output method '{output}'")

    @property
    def n_groups(self) -> int:
        return len(self.datasets)

    @property
    def n_datasets(self) -> int:
        return len(self.flattened)

    def __len__(self) -> int:
        return self.n_datasets

    def __repr__(self) -> str:
        return f"{self.__class__}(groups={self.n_groups}, datasets={self.n_datasets})"

    def summary(self) -> str:
        s = [repr(self) + ":"]
        for group in self.datasets:
            name = group.get("group")
            n = len(group["maps"])
            s.append(f"  Group <{name}>: {n} maps")
        return "\n".join(s)

    def process_json(self, obj: str) -> GroupedDatasets:
        dataset_file = open_json(obj)
        presets = {k: self._preprocess(v) for k, v in dataset_file["presets"].items()}
        presets["default"] = merge(presets["default"], DEFAULTS)
        self.presets = presets

        datasets = []
        for g in dataset_file["datasets"]:
            group = g.get("group")
            _maps = g.get("maps", [])
            maps: list[DatasetParams] = []
            for map_ in _maps:
                try:
                    unsorted_maps = self.process_one(map_)
                except Exception as e:
                    pprint(map_)
                    raise e
                sorted_maps = sorted(unsorted_maps, key=lambda m: m["name"]) # type: ignore
                maps.extend(sorted_maps)
            dataset_group: DatasetGroup = {"group": group, "maps": maps}
            datasets.append(dataset_group)
        return datasets

    def process_one(self, map_: DatasetParams) -> list[DatasetParams]:
        """Process one map description
        One map description = one JSON dict listed in a "maps" list in a datasets.json file
        It must have at least 1 id, 1 name, 1 file
        """
        raw_maps = self.unglobify(map_)
        merged_maps = []
        for raw_map in raw_maps:
            raw_map = self._preprocess(raw_map)
            merged = process(raw_map, self.presets)
            merged = self.detect(merged)
            if merged is not None:
                merged_maps.append(merged)

        return merged_maps

    def _preprocess(self, map_: DatasetParams) -> DatasetParams:
        if "single_group" in map_ and map_["single_group"] is True:
            map_["weights*"] = [[1]]
            map_["label*"] = ["Normal"]
        return map_

    def detect(self, map_: DatasetParams) -> Optional[DatasetParams]:
        levels = map_["levels"]
        valid_levels = []
        invalid_levels = []
        possible_levels = []
        for i, level in enumerate(levels):
            gm = self._load(map_, i)
            if len(gm.df) >= 10:
                possible_levels.append(i)
            # Count all points that have a non-zero probability to be sampled
            n_points = sum(
                gm.counts[group] for group in gm.counts if gm.weights[group] > 0
            )
            if n_points >= 10:
                valid_levels.append(level)
            else:
                invalid_levels.append(i)
        if not valid_levels:
            if possible_levels:
                # do someting
                print(f"Switching to single_group mode for map '{map_['name']}")
                map_["single_group"] = True
                level = levels[possible_levels[0]]
                level["single_group"] = True
                level["weights"] = [1]
                valid_levels = [level]
            else:
                print(f"Not enough points for map '{map_['name']}', removing it")
                return None
        elif invalid_levels:
            print(f"Remove levels from map '{map_['name']}' :", *invalid_levels)
        map_["levels"] = valid_levels
        return map_

    def generate_countries(self, base_file: str, column: str, preset: str) -> list[DatasetParams]:
        df = self.dataframes[base_file]
        maps = []
        for country_code in df[column].unique():
            maps.append(
                dict(
                    name=codes.get(country_code, country_code),
                    map_id=country_code,
                    preset=preset,
                    file=base_file,
                    filters=[dict(column=column, values=country_code)],
                )
            )
        return maps

    def unglobify(self, map_: DatasetParams) -> list[DatasetParams]:
        if "method" in map_:
            method = map_["method"]
            args = map_.get("args", {})
            return getattr(self, method)(**args) # type: ignore
        if "spec_file" in map_:
            file_pattern = map_.pop("spec_file")
            pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
            to_process = [
                (fn, {**map_, **open_json(fn)}) for fn in glob.glob(file_pattern)
            ]
        elif "file" in map_:
            file_pattern = map_["file"]
            pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
            to_process = [(fn, {**map_, "file": fn}) for fn in glob.glob(file_pattern)]
        else:
            return [map_]
        maps = []
        for fn, params in to_process:
            code = fn[len(pref) : -len(suff)]
            name = codes.get(code, code)
            for k, v in params.items():
                params[k] = (
                    v.replace("<id>", code).replace("<name>", name)
                    if isinstance(v, str)
                    else v
                )
            maps.append(params)
        return maps

    def get_dataset_information(self, map_: DatasetParams) -> DatasetInformation:
        # keys = ["map_id", "name", "default_level"]
        # params = {k: map_[k] for k in keys}
        levels = map_["levels"]
        # params["levels"] = [
        #     dict(index=i, name=level["label"]) for i, level in enumerate(levels)
        # ]
        params: DatasetInformation = {
            "map_id": map_["map_id"],
            "name": map_["name"],
            "default_level": map_["default_level"],
            "levels": [{"index": i, "name": level["label"]} for i, level in enumerate(levels)]
        }
        return params

    def get_datasets(self, full: bool=False) -> Union[GroupedDatasets, FilteredGroupedDatasets]:
        if full:
            return self.datasets
        datasets: FilteredGroupedDatasets = []
        for dataset_group in self.datasets:
            group = dataset_group["group"]
            maps = dataset_group["maps"]
            filtered_maps: list[DatasetInformation] = [self.get_dataset_information(m) for m in maps]
            datasets.append({
                "group": group,
                "maps": filtered_maps,
            })
        return datasets
