from collections import defaultdict
from parser import ParserError

from geo import Point
import geo
import random
import pandas as pd
import numpy as np


COUNTRY_CODE_FILES = "data/country_codes.txt"
REGION_CODE_FILES = "data/region_codes.txt"


def read_codes(fname):
    with open(fname, "r", encoding="utf8") as f:
        def read_line(l):
            country, code = l.rstrip().split("\t")
            return country, code

        countries = {country: code for country, code in map(read_line, f.read().split("\n"))}
    return countries, {code: country for country, code in countries.items()}

def read_region(name):
    with open(f"data/{name}_codes.txt", "r", encoding="utf8") as f:
        return f.read().split("\n")

REGION_NAMES = {
    "europe": "Europe",
    "noram": "Amérique du Nord"
}

COUNTRY_CODES, REV_COUNTRY_CODES = read_codes(COUNTRY_CODE_FILES)
REGION_CODES, REV_REGION_CODES = read_codes(REGION_CODE_FILES)

OLD_REGIONS = {
    region_id: dict(name=region_name, codes=read_region(region_id), limit_size=500, method="from_country_codes") for region_id, region_name in REGION_NAMES.items()
}
REGIONS = {}


for code, region in REV_REGION_CODES.items():
    for difficulty, name in zip(["easy", "normal", "hard"], ["facile", "normal", "difficile"]):
        region_name = f"{region} ({name})"
        region_id = f"{code}_{difficulty}"
        if region_id == "NA_hard":
            limit_size = 1500
        else:
            limit_size = None
        REGIONS[region_id] = dict(name=region_name, file=f"data/regions/{region_id}.csv", use_hint=True, limit_size=limit_size)


GROUP_EASY = "Facile"
GROUP_HARD = "Difficile"
GROUP_GOD = "Impitoyable"
GROUP_HISTORIC = "Historique"
GROUP_COUNTRIES = "Par pays"

historic_names = {
    # "Tout": "all_filtered",
    # "XXème siècle": "1900_handpicked",
    # "Depuis 1900": "1900_filtered",
    "Seconde guerre mondiale": "ww2_filtered",
    "Première guerre mondiale": "ww1_sorted",
    "Guerres napoléoniennes": "napoleonic_wars_sorted",
    # "Rome antique": "rome_sorted",
}

def make_params(map_id, map_name, file, use_hint=True, limit_size=None, **params):
    return dict(map_id=map_id, params=dict(name=map_name, file=file, use_hint=use_hint, limit_size=limit_size, **params))

def make_historic_params(name):
    map_id = historic_names[name]
    return make_params(map_id, name, f"data/historic/{map_id}.csv", method="from_historic")

def make_region_params(code, level):
    return make_params(f"{code}_{level}", REV_REGION_CODES[code], f"data/regions/{code}_{level}.csv")

def make_country_params(code):
    return make_params(code, REV_COUNTRY_CODES[code], f"data/all/{code}.csv", limit_size=1000)

GROUPED = [
    dict(group=None, maps=[
        make_params("world", "Monde entier", "data/places.world.csv"),
        make_params("world_capitals", "Capitales", "data/world_capitals.csv"),
        make_params("world_capitals-no-hint", "Capitales (sans pays)", "data/world_capitals.csv", use_hint=False),
        make_params("XX", "Evénements du XXème siècle", "data/historic/1900_handpicked.csv", use_hint=False),
    ]),
    dict(group=GROUP_EASY, maps=[
        make_params("france_easy", "France", "data/all/FR.csv"),
        *(make_region_params(code, "easy") for code in REV_REGION_CODES)
    ]),
    dict(group=GROUP_HARD, maps=[
        make_params("france_hard", "France", "data/places.france.csv"),
        *(make_region_params(code, "normal") for code in REV_REGION_CODES)
    ]),
    dict(group=GROUP_GOD, maps=[make_region_params(code, "hard") for code in REV_REGION_CODES]),
    # dict(group=GROUP_HISTORIC, maps=[
    #     make_params("XX", "XXème siècle", "data/historic/1900_handpicked.csv", use_hint=False),
    #     *(make_historic_params(name) for name in historic_names)]),
    dict(group=GROUP_COUNTRIES, maps=[make_country_params(code) for code in REV_COUNTRY_CODES])
]

MAPS = {item["map_id"]: dict(group=G["group"], **item["params"])  for G in GROUPED for item in G["maps"]}


# SPECIALS = {
#     "world": dict(name="Monde entier", file="data/places.world.csv", use_hint=True),
#     "france_easy": dict(name="France (facile)", file="data/all/FR.csv", use_hint=True, ),
#     "france_hard": dict(name="France (difficile)", file="data/places.france.csv",),
#     **REGIONS,
# }
#
# COUNTRIES = {code: dict(name=country, file=f"data/all/{code}.csv", limit_size=1000, use_hint=True) for country, code in COUNTRY_CODES.items()}
#
# # All available GameMaps
# MAPS = {**SPECIALS, **COUNTRIES}


def reaccent(name):
    name = name.lower()
    stopwords = {"en", "le", "la", "les", "d", "de", "du", "des", "sur"}

    def capit(s):
        if s.lower() in stopwords:
            return s
        return s[0].upper() + s[1:]

    seps = {" ", "-", "'"}
    for sep in seps:
        name = sep.join([capit(word) for word in name.split(sep)])
    return capit(name)


def clean_city(city):
    if city.isupper():
        return reaccent(city)
    return city


class GameMap:
    def __init__(self, name, places, lons, lats, hints=None, ranks=None, group=None):
        self.name = name
        self.places = places
        self.lons = lons
        self.lats = lats
        self.hints = hints if hints is not None else [""] * len(self.places)
        self.ranks = ranks if ranks is not None else [0] * len(self.places)
        self.bbox = None
        self.distance = self.get_distance()
        if group is None:
            group = "__default__"
        self.group = group

    def ranking_available(self):
        return len(set(self.ranks)) > 1

    def __str__(self):
        return f"GameMap({self.name}, n_places={len(self.places)})"

    @property
    def full_name(self):
        return f"{self.name} ({len(self.places)} villes)"

    @classmethod
    def from_file(cls, name, file, use_hint=False, limit_size=None, group=None):
        df = pd.read_csv(file, nrows=limit_size)
        ranks = None
        if "population" in df.columns:
            ranks = np.argsort(-df.population.fillna(0))
        return cls(name, places=df.city, lons=df.lng, lats=df.lat,
                   ranks=ranks,
                   hints=df.admin if use_hint else None, group=group)

    @classmethod
    def from_historic(cls, name, file, limit_size=None, group=None, use_hint=True, sep=None):
        try:
            df = pd.read_csv(file, nrows=limit_size)
        except Exception:
            df = pd.read_csv(file, nrows=limit_size, sep=";")

        ranks = None
        if "popularity" in df.columns:
            if "keep" in df.columns:
                ranks = [int(x) for x in np.lexsort((-df.keep, -df.popularity))]
            else:
                ranks = np.argsort(-df.popularity)
            print(ranks[:10])
            # ranks = np.argsort(how)
        def get_name(name, date):
            if not date or not isinstance(date, str):
                return str(name)
            if "-" in date:
                year = date.split("-")[0]
            elif "/" in date:
                year = date.split("/")[-1]
            else:
                return str(name)
            if year in name:
                return str(name)
            return f"{name} ({year})"
        if "date" in df:
            places = [get_name(name, date) for name, date in zip(df.label, df.date)]
        else:
            places = df.label.astype(str)
        return cls(name, places=places, lons=df.lon.astype(float), lats=df.lat.astype(float), ranks=ranks, group=group)

    @classmethod
    def from_files(cls, name, files, use_hint=True, limit_size=None, group=None):
        df = None
        for country, file in files:
            pdf = pd.read_csv(file, nrows=limit_size)
            if use_hint:
                pdf["admin"] = country
            if df is None:
                df = pdf
            else:
                df = pd.concat([df, pdf])
        df.population = df.population.fillna(0)
        if limit_size:
            df = df.sort_values("population", ascending=False).head(limit_size)
        ranks = np.argsort(-df.population)
        return cls(name, places=df.city, lons=df.lng, lats=df.lat,
                   ranks=ranks,
                   hints=df.admin if use_hint else None, group=group)

    @classmethod
    def from_country_codes(cls, name, codes, **params):
        files = [(REV_COUNTRY_CODES[code], f"data/all/{code}.csv") for code in codes if code in REV_COUNTRY_CODES]
        return cls.from_files(name, files, **params)

    @classmethod
    def from_country(cls, country, use_hint=False, limit_size=None, group=None):
        code = COUNTRY_CODES[country]
        return cls.from_file(country, f"data/all/{code}.csv", use_hint, limit_size, group=group)

    @classmethod
    def from_name(cls, name):
        if name in MAPS:
            if "method" in MAPS[name]:
                params = MAPS[name].copy()
                attr =  params.pop("method")
                return getattr(cls, attr)(**params)
            return cls.from_file(**MAPS[name])
        elif name in COUNTRY_CODES:
            return cls.from_country(name)
        else:
            raise ValueError(f"Invalid GameMap name '{name}'")

    def bounding_box(self):
        if self.bbox is None:
            minlon = min(self.lons)
            maxlon = max(self.lons)
            minlat = min(self.lats)
            maxlat = max(self.lats)
            self.bbox = dict(
                minlon=minlon,
                maxlon=maxlon,
                minlat=minlat,
                maxlat=maxlat,
            )
            self.bbox = [
                [maxlat, minlon],
                [minlat, maxlon],
            ]
        return self.bbox

    def get_geometry(self):
        points = [{"coords": [lat, lon], "data": dict(rank=p)} for lat, lon, p in zip(self.lats, self.lons, self.ranks)]
        min_rank = min(self.ranks)
        max_rank = max(self.ranks)
        bbox = self.bounding_box()
        return dict(dataset=self.name, points=points, bbox=bbox,
                    stats=dict(
                        min_rank=min_rank,
                        max_rank=max_rank)
                    )

    def get_distance(self):
        corner1, corner2 = self.bounding_box()

        p1 = Point.from_latlon(*corner1)
        p2 = Point.from_latlon(*corner2)
        dist = geo.distance(p1, p2)

        return round(dist**0.7)

    def build_list(self, difficulty=1):
        if not self.ranking_available():
            difficulty = 1.1
        min_rank= max(10, difficulty * max(self.ranks))
        return {((clean_city(city), hint), Point(lon, lat))
                for city, hint, lon, lat, rank in zip(self.places, self.hints, self.lons, self.lats, self.ranks)
                if rank <= min_rank}

    def sample(self, k, difficulty=1):
        options = self.build_list(difficulty)
        print(f"Sampling {k} places out of {len(options)}")
        if k > len(options):
            k = len(options)
        return random.sample(options, k)
