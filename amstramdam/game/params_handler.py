DEFAULT_PARAMS = {
    "map": "world",
    "duration": 10,
    "zoom": False,
    "runs": 10,
    "wait_time": 10,
    "difficulty": 0,
    "public": False,
    "precision_mode": False,
}


def merge_params(params, defaults=None):
    """
    Merge a (potentially incomplete) params dict with a default params dict,
    and convert values into the right type
    """
    if defaults is None:
        defaults = DEFAULT_PARAMS
    merged = {**defaults, **params}  # type: ignore
    converts = [
        (int, {"duration", "runs", "wait_time", "difficulty"}),
        (bool, {"public", "zoom", "precision_mode"}),
    ]
    for convert, keys in converts:
        for key in keys & merged.keys():
            merged[key] = convert(merged[key])  # type: ignore

    return merged
