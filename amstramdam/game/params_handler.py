DEFAULT_PARAMS = {
    "map": "world",
    "duration": "10",
    "zoom": False,
    "runs": 10,
    "wait_time": 10,
    "difficulty": 100,
    "public": False,
}

def merge_params(params, defaults=None):
    """
    Merge a (potentially incomplete) params dict with a default params dict,
    and convert values into the right type
    """
    if defaults is None:
        defaults = DEFAULT_PARAMS
    params = {
        **defaults,
        **params
    }
    converts = [
        (int, ["duration", "runs", "wait_time", "difficulty"]),
        (bool, ["public", "zoom"])
    ]
    for convert, keys in converts:
        for key in keys:
            params[key] = convert(params[key])

    params["difficulty"] /= 100
    return params