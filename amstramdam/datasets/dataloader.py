import json
import glob

import bidict

from .game_map import GameMap


def read_codes(*filenames, check_unicity=True):
    """
    Read bidirectional mapping between codes (e.g country codes or region codes) and names
    from tab-separated text file(s)
    """
    _codes = bidict.bidict()
    _codes_a = set()
    _codes_b = set()

    for codefile in filenames:
        _codes_a = _codes_b
        _codes_b = set()
        with open(codefile, "r", encoding="utf8") as f:
            for line in f:
                name, code = line.rstrip().split("\t")
                _codes[code] = name
                _codes_b.add(code)
        non_unique_codes = _codes_a & _codes_b
        if non_unique_codes and check_unicity:
            print("WARNING: non-unique regional codes: ", *non_unique_codes)
    return _codes


codes = read_codes("data/country_codes.txt", "data/region_codes.txt")


def process_map(filename, map_, pref="", suff=""):
    code = filename.strip(pref).rstrip(suff)
    name = codes.get(code, code)
    processed = dict(file=filename)
    for k, v in map_.items():
        processed[k] = v.replace("<id>", code).replace("<name>", name) if isinstance(v, str) else v
    return processed


class Dataloader(object):
    def __init__(self, datasets):
        self.datasets = self.process_json(datasets)
        self.flattened = {item["map_id"]: dict(group=G["group"], **item)
                          for G in self.datasets
                          for item in G["maps"]}

    def load(self, name, **params):
        if name in self.flattened:
            map_params = self.flattened[name].copy()
            attr = map_params.pop("method", "from_file")
            return getattr(GameMap, attr)(**map_params, **params)
        #return GameMap(name, **params)
        raise KeyError(name)

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

    @classmethod
    def process_json(cls, obj):
        datasets = []
        for g in cls.open_json(obj):
            group = g.get("group")
            _maps = g.get("maps", [])
            maps = []
            for map_ in _maps:
                file_pattern = map_.pop("file")
                pref, suff = file_pattern.split("*") if "*" in file_pattern else ("", "")
                unsorted_maps = [process_map(fn, map_, pref, suff) for fn in glob.glob(file_pattern)]
                sorted_maps = sorted(unsorted_maps, key=lambda m: m["name"])
                maps.extend(sorted_maps)
            datasets.append(dict(group=group, maps=maps))
        return datasets
