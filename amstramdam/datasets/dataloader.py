import json
import glob
import os
import warnings
from datetime import datetime

import bidict

from .game_map import GameMap
from .grouped_game_map import GroupBasedGameMap
from .dataframe import DataFrameLoader, mask_df, autorank
import io

def read_code(filename, sep="\t"):
    bidirectional_codes = bidict.bidict()
    with open(filename, "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            if line.startswith("#"):
                continue
            try:
                name, code = line.rstrip().split(sep)
                bidirectional_codes[code] = name
            except ValueError:
                print(f"Error on line {i}: {line.rstrip()}")
                continue
    return bidirectional_codes


codes = read_code("data/codes.txt")


def process_map(filename, map_, pref="", suff=""):
    code = filename[len(pref):-len(suff)]
    name = codes.get(code, code)
    processed = dict(file=filename)
    for k, v in map_.items():
        processed[k] = v.replace("<id>", code).replace("<name>", name) if isinstance(v, str) else v
    return processed



def analyze_country(df, code, col="population"):
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


class Dataloader(object):
    GSYSTEM = "__gsystem__"
    GCOUNTRIES = "__countries__"
    LEGACY_SYSTEM = "__legacy__"

    SCALE_WORLD = 0
    SCALE_CONTINENT = 1
    SCALE_COUNTRY = 2

    processing_methods = {
        GSYSTEM: "_process_grouped_map",
        GCOUNTRIES: "_build_country_maps",
        LEGACY_SYSTEM: "_process_standard_map"
    }

    def __init__(self, datasets):
        self.dataframes = DataFrameLoader()
        self.datasets = self.process_json(datasets)
        self.flattened = {item["map_id"]: dict(group=G["group"], **item)
                          for G in self.datasets
                          for item in G["maps"]}

    def load(self, name, **params):
        if name in self.flattened:
            map_params = self.flattened[name].copy()
            try:
                if map_params.pop("mtype", None) == self.LEGACY_SYSTEM:
                    attr = map_params.pop("method", "from_file")
                    return getattr(GameMap, attr)(**map_params, **params)
                return self.load_from_group(map_params)
            except Exception as e:
                print(map_params)
                raise e
        raise KeyError(name)

    def load_from_group(self, params):
        df_file = params.pop("base_file")
        df = self.dataframes[df_file]
        df = mask_df(df, params.pop("filters", []))

        if "autorank" in params:
            df, extra_params = autorank(df, **params.pop("autorank"))
            params.update(extra_params)

        params["df"] = df
        return GroupBasedGameMap(**params)

    def commit_changes(self, name, changes):
        if name not in self.flattened:
            raise KeyError(name)
        created = changes.get("create", [])
        updated = changes.get("update", {})
        output = changes.get("output", "save")

        filename = self.flattened[name].get("base_file")
        if filename is None:
            warnings.warn(f"Dataset '{name} can't be edited because it doesn't have"
                          "a registered 'base_file'. Please change 'datasets.json' and"
                          "add a 'base_file' key.")
            return

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
    def n_groups(self):
        return len(self.datasets)

    @property
    def n_datasets(self):
        return len(self.flattened)

    def __len__(self):
        return self.n_datasets

    def __repr__(self):
        return f"{self.__class__}(groups={self.n_groups}, datasets={self.n_datasets})"

    def summary(self):
        s = [repr(self)+":"]
        for group in self.datasets:
            name = group.get("group")
            n = len(group["maps"])
            s.append(f"  Group <{name}>: {n} maps")
        return "\n".join(s)

    @classmethod
    def open_json(cls, file_or_object):
        if isinstance(file_or_object, str):
            with open(file_or_object, "r", encoding="utf8") as f:
                file_or_object = json.load(f)
        return file_or_object

    def process_json(self, obj):
        datasets = []
        for g in self.open_json(obj):
            group = g.get("group")
            _maps = g.get("maps", [])
            maps = []
            for map_ in _maps:
                unsorted_maps = self.process_one(map_)
                sorted_maps = sorted(unsorted_maps, key=lambda m: m["name"])
                maps.extend(sorted_maps)
            datasets.append(dict(group=group, maps=maps))
        return datasets


    def _build_country_maps(self, base_params):
        maps = []
        base_file = base_params.get("base_file")
        map_id = base_params.pop("map_id")
        col = base_params.pop("country_col", "iso2")
        suggested = set(base_params.pop("suggested", []))
        del base_params["mtype"]
        df = self.dataframes[base_file]

        for country_code in df[col].unique():
            sugg = "⭐" if country_code in suggested else ""
            if "autorank" not in base_params:
                autorank_params = analyze_country(df, country_code, col="population")
                if autorank_params:
                    autorank_params["available_levels"] -= self.SCALE_COUNTRY
            else:
                autorank_params = dict()

            maps.append({
                **base_params,
                **autorank_params,
                "map_id": map_id.replace("<id>", country_code),
                "name": codes.get(country_code, country_code) + sugg,
                "scale": self.SCALE_COUNTRY,
                "mtype": "__gsystem__",
                "filters": [dict(column="iso2", values=country_code)]
            })
        return maps

    def process_one(self, map_):
        """Dispatch the processing depending on the format (legacy, G-system, or special cases)"""
        map_system = map_.get("mtype", self.GSYSTEM)
        processing_method = self.processing_methods[map_system]
        return getattr(self, processing_method)(map_)

    def _process_legacy_map(self, map_):
        """Process standard, file-based specification dict"""
        warnings.warn("The legacy map format is deprecated, and should be replaced by the G-system", DeprecationWarning)

        file_pattern = map_.pop("file")
        pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
        unsorted_maps = [process_map(fn, map_, pref, suff) for fn in glob.glob(file_pattern)]
        return unsorted_maps

    def _process_grouped_map(self, map_):
        """Process new, group-based specification dict (nicknamed 'G-system')"""
        if "spec_file" in map_:
            file_pattern = map_.pop("spec_file")
            pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
            to_process = [(fn, {**map_, **self.open_json(fn)}) for fn in glob.glob(file_pattern)]
        else:
            file_pattern = map_["base_file"]
            pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
            to_process = [(fn, {**map_, "base_file": fn}) for fn in glob.glob(file_pattern)]
        maps = []
        for fn, params in to_process:
            # params = {**map_, **self.open_json(fn)}
            code = fn[len(pref):-len(suff)]
            name = codes.get(code, code)
            for k, v in params.items():
                params[k] = v.replace("<id>", code).replace("<name>", name) if isinstance(v, str) else v
            if "autorank" in params and not "available_levels" in params:
                params["available_levels"] = len(params["autorank"]["ranks"]) - params.get("scale", 0)
            maps.append(params)
        return maps
