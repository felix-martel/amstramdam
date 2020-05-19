from geo import Point
import geo
import random
import pandas as pd

COUNTRY_CODE_FILES = "data/country_codes.txt"


def read_countries():
    with open(COUNTRY_CODE_FILES, "r", encoding="utf8") as f:
        def read_line(l):
            country, code = l.rstrip().split("\t")
            return country, code

        countries = {country: code for country, code in map(read_line, f.read().split("\n"))}
    return countries


COUNTRY_CODES = read_countries()
SPECIALS = {
    "france_hard": dict(name="France (difficile)", file="data/places.france.csv"),
    "world": dict(name="Monde entier", file="data/places.world.csv", use_hint=True)
}
COUNTRIES = {code: dict(name=country, file=f"data/all/{code}.csv", limit_size=200, use_hint=True) for country, code in COUNTRY_CODES.items()}

# All available GameMaps
MAPS = {**SPECIALS, **COUNTRIES}


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
    def __init__(self, name, places, lons, lats, hints=None):
        self.name = name
        self.places = places
        self.lons = lons
        self.lats = lats
        self.hints = hints if hints is not None else [""] * len(self.places)
        self.bbox = None
        self.distance = self.get_distance()

    def __str__(self):
        return f"GameMap({self.name}, n_places={len(self.places)})"

    @property
    def full_name(self):
        return f"{self.name} ({len(self.places)} villes)"

    @classmethod
    def from_file(cls, name, file, use_hint=False, limit_size=None):
        df = pd.read_csv(file, nrows=limit_size)
        return cls(name, places=df.city, lons=df.lng, lats=df.lat, hints=df.admin if use_hint else None)

    @classmethod
    def from_country(cls, country, use_hint=False, limit_size=None):
        code = COUNTRY_CODES[country]
        return cls.from_file(country, f"data/all/{code}.csv", use_hint, limit_size)

    @classmethod
    def from_name(cls, name):
        if name in MAPS:
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
        points = [[lat, lon] for lat, lon in zip(self.lats, self.lons)]
        bbox = self.bounding_box()
        return dict(dataset=self.name, points=points, bbox=bbox)

    def get_distance(self):
        corner1, corner2 = self.bounding_box()

        p1 = Point.from_latlon(*corner1)
        p2 = Point.from_latlon(*corner2)
        dist = geo.distance(p1, p2)

        return round(dist**0.7)

    def build_list(self):
        return {((clean_city(city), hint), Point(lon, lat))
                for city, hint, lon, lat in zip(self.places, self.hints, self.lons, self.lats)}

    def sample(self, k):
        return random.sample(self.build_list(), k)
