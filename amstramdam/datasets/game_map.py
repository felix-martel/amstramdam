from amstramdam.game.geo import Point, distance

import random
import pandas as pd
import numpy as np


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
    def __init__(self, name, places, lons, lats, hints=None, ranks=None, group=None, harshness=0.7, map_id=None):
        self.name = name
        self.id = map_id if map_id is not None else f"map<{name.replace(' ', '_')}>"
        self.places = places
        self.lons = lons
        self.lats = lats
        self.hints = hints if hints is not None else [""] * len(self.places)
        self.ranks = ranks if ranks is not None else [0] * len(self.places)
        self.bbox = None
        self.distance_harshness = harshness
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
    def from_file(cls, name, file, use_hint=False, limit_size=None, group=None,
                  col_place="city",
                  col_lon="lng",
                  col_lat="lat",
                  col_rank="population",
                  col_hint="admin",
                  reverse_rank=False,
                  **params):
        print("Loading", name, ". With hint ?", use_hint, col_hint)
        df = pd.read_csv(file, nrows=limit_size)
        ranks = None
        if col_rank in df.columns:
            fac = 1 if reverse_rank else -1
            ranks = np.argsort(fac * df[col_rank].fillna(0))
        return cls(name, places=df[col_place], lons=df[col_lon], lats=df[col_lat],
                   ranks=ranks,
                   hints=df[col_hint] if use_hint else None, group=group, **params)

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

    # @classmethod
    # def from_country_codes(cls, name, codes, **params):
    #     files = [(REV_COUNTRY_CODES[code], f"data/all/{code}.csv") for code in codes if code in REV_COUNTRY_CODES]
    #     return cls.from_files(name, files, **params)
    #
    # @classmethod
    # def from_country(cls, country, use_hint=False, limit_size=None, group=None):
    #     code = COUNTRY_CODES[country]
    #     return cls.from_file(country, f"data/all/{code}.csv", use_hint, limit_size, group=group)
    #
    # @classmethod
    # def from_name(cls, name):
    #     if name in MAPS:
    #         if "method" in MAPS[name]:
    #             params = MAPS[name].copy()
    #             attr =  params.pop("method")
    #             return getattr(cls, attr)(**params)
    #         return cls.from_file(**MAPS[name])
    #     elif name in COUNTRY_CODES:
    #         return cls.from_country(name)
    #     else:
    #         raise ValueError(f"Invalid GameMap name '{name}'")

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
        dist = distance(p1, p2)

        dist_param = dist**self.distance_harshness
        print(self.name, dist_param)
        return dist_param

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
