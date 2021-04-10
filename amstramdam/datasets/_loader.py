import json
from typing import Any, Union, Optional
from pprint import pprint
from copy import deepcopy

from amstramdam.datasets.types import DatasetParams

SYMBOL: str = "*"
PROTECTED: set[str] = {"file", "name", "map_id", "default_level", "preset"}
DEFAULTS: DatasetParams = {
    "col_group": "group",
    "col_hint": "admin",
    "col_lat": "lat",
    "col_lon": "lng",
    "col_place": "city",
    "col_rank": "population",
    "default_level": 0,
    "file": "data/places.world.csv",
    "filters": [],
    "harshness": 0.7,
    "levels": [
        {"label": "Facile", "weights": [1]},
        {"label": "Moyen", "weights": [1, 1]},
        {"label": "Difficile", "weights": [1, 1, 0.5]},
    ],
    "single_group": False,
    "use_hint": True,
}


def open_json(fp_or_obj: Union[dict[Any, Any], str]) -> dict[Any, Any]:
    if isinstance(fp_or_obj, str):
        with open(fp_or_obj, "r", encoding="utf8") as f:
            raw = json.load(f)
        return raw
    return fp_or_obj


def has_levels(descr):
    return any(k.endswith(SYMBOL) for k in descr) or "levels" in descr


def count_levels(descr):
    name = descr.get("name", "<unknown>")
    # First, count levels based on starred arguments
    lengths = {len(values) for key, values in descr.items() if key.endswith(SYMBOL)}
    if not lengths:
        n_starred = -1
    else:
        if len(lengths) != 1:
            raise ValueError(f"Length mismatch ({lengths}) in map {name}")
        n_starred = lengths.pop()

    # Second, count levels that are explicitly declared through the 'levels' key
    n_explicit = len(descr.get("levels", []))

    if n_starred <= 0 and n_explicit <= 0:
        # Number of levels can't be inferred
        return -1
    elif n_starred > 0 and n_explicit > 0 and n_starred != n_explicit:
        raise ValueError(f"Length mismatch in map {name}")
    else:
        return max(n_starred, n_explicit)


def distribute_starred(descr, n_levels):
    keys = [key for key in descr if key.endswith(SYMBOL)]
    levels = [dict() for _ in range(n_levels)]
    for key in keys:
        for i, value in enumerate(descr.pop(key)):
            levels[i][key[: -len(SYMBOL)]] = value
    return levels


def distribute_explicit(descr, n_levels):
    if "levels" not in descr:
        return [dict() for _ in range(n_levels)]
    levels = [level if level is not None else dict() for level in descr["levels"]]
    return levels


def distribute(descr, clean=True):
    n_levels = count_levels(descr)
    if n_levels == -1:
        return deepcopy(descr)
    levels_a = distribute_starred(descr, n_levels)
    levels_b = distribute_explicit(descr, n_levels)
    base = distributable_descr(descr)
    merged = [{**base, **lvla, **lvlb} for lvla, lvlb in zip(levels_a, levels_b)]
    keys = descr.keys() - {"levels"}
    distributed = {k: descr[k] for k in keys}
    distributed["levels"] = merged
    return distributed


def undistributable_keys(descr):
    return descr.keys() & PROTECTED


def undistributable_descr(descr):
    return {k: descr[k] for k in undistributable_keys(descr)}


def base_keys(descr):
    return descr.keys() - {"levels"}


def base_descr(descr):
    return {k: descr[k] for k in base_keys(descr)}


def distributable_keys(descr):
    return descr.keys() - {"levels"} - PROTECTED


def distributable_descr(descr):
    return {k: descr[k] for k in distributable_keys(descr)}


def merge(descr, default):
    # Here we assume default is already distributed
    default = distribute(default)
    if not has_levels(descr):
        common = distributable_descr(descr)
        base = {
            **base_descr(default),
            **base_descr(descr),
            "levels": [{**level, **common} for level in default["levels"]],
        }
        return base
    # Else
    # 1: distribute
    descr = distribute(descr)
    base = {**base_descr(default), **base_descr(descr)}
    common = distributable_descr(base)  # <- check if base or descr
    levels, default_levels = descr["levels"], default["levels"]
    if len(levels) != len(default_levels):
        default_levels = [dict() for _ in range(len(levels))]
    new_levels = [
        {**default_level, **common, **level}
        for default_level, level in zip(default_levels, levels)
    ]
    base["levels"] = new_levels
    return base


def process(descr, presets):
    descr = deepcopy(descr)
    preset_name = descr.pop("preset", None)
    preset = presets.get(preset_name, dict())
    preset_processed = merge(preset, presets["default"])
    merged = merge(descr, preset_processed)
    return merged
