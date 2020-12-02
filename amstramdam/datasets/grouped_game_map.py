import random
from collections import Counter
from functools import partial

from amstramdam.game.geo import Point, distance
import pandas as pd

class GroupBasedGameMap:
    scales = ["world", "continent", "country"]
    _weights = [
        [  # world normal / advanced / expert
            [1],
            [2, 1, 0.1],
            [3, 2, 0.5]
        ],
        [  # continent normal / advanced / expert
            [1.5, 1],
            [1, 1, 1, 0.1],
            [1, 1, 1, 0.5]
        ],  # country normal / advanced / expert
        [
            [1.2, 1.1, 1],
            [1, 1, 1, 0.5],
            [1, 1, 1, 1, 0.6]
        ]
    ]

    def __init__(self, name, df, scale=0, weights=None,
                available_levels=None, default_level=0,
                 group=None, harshness=0.7, map_id=None, use_hint=True,
                 col_place="city", col_hint="admin", col_lon="lng", col_lat="lat", col_group="group",
                 col_rank="population", **kwargs):
        # Map information
        self.name = name
        self.id = map_id if map_id is not None else f"map<{name.replace(' ', '_')}>"
        self.group = group
        self.use_hint = use_hint and col_hint in df.columns

        # Map data
        if col_group not in df.columns:
            # When no group is provided, automatically activate single group mode
            #df[col_group] = 0
            available_levels = 1
            default_level = 0
        self.single_group = available_levels == 1
        self.col_place = col_place
        self.col_hint = col_hint
        self.col_lon = col_lon
        self.col_lat = col_lat
        self.col_group = col_group
        self.df = df

        if self.single_group:
            self.counts = {0: len(self.df)}
        else:
            self.counts = self.df.groupby(by=col_group)[col_place].count()

        # Difficulty settings
        self.scale_index = scale
        if weights is None:
            weights = self._weights[self.scale_index]
        self.weights = weights
        if available_levels is None:
            available_levels = len(self.weights)
        self.available_levels = available_levels
        assert default_level < self.available_levels, (f"Can't set default_level={default_level} when "
                                                       f"only {available_levels} levels are available")
        self.default_level = default_level

        # Geometric information
        self.bbox = None
        self.harshness = harshness
        self.distance = self.get_distance()

    def ranking_available(self):
        raise NotImplementedError()  # return len(set(self.ranks)) > 1

    def __str__(self):
        return f"GameMap({self.name}, n_places={len(self.df)})"

    @property
    def full_name(self):
        return f"{self.name} ({len(self.df)} villes)"

    def bounding_box(self):
        if self.bbox is None:
            # Compute once, then cache
            self.bbox = [
                [self.df[self.col_lat].max(), self.df[self.col_lon].min()],
                [self.df[self.col_lat].min(), self.df[self.col_lon].max()],
            ]
        return self.bbox

    def _extract_attr(self, attr, point=None):
        if point is None:
            return self.df[attr]
        return getattr(point, attr)

    def extract_place(self, point=None):
        return self._extract_attr(self.col_place, point)

    def extract_hint(self, point=None):
        if not self.use_hint:
            if point is None:
                return pd.Series("", index=self.df.index)
            return ""
        return self._extract_attr(self.col_hint, point)

    def extract_lon(self, point=None):
        return self._extract_attr(self.col_lon, point)

    def extract_lat(self, point=None):
        return self._extract_attr(self.col_lat, point)

    def extract_group(self, point=None):
        if self.single_group:
            if point is None:
                return pd.Series(0, index=self.df.index)
            return 0
        return self._extract_attr(self.col_group, point)

    def jsonify_point(self, point, label=False, hint=False, columns=None):
        """
        Convert a `point`, represented as a NamedTuple, to a JSON-ifiable format, ready to be sent over HTTP to the
        client. The JSON-like outpout contains two keys:
        - `coords`, a `[lat, lon]` array of geographic coordinates
        - `data`, extra data attached to the point (e.g its name, rank, group)
        """
        if columns is None:
            columns = []
        valid_fields = set(columns) & set(point._fields)
        additional_data = {f"col_{k}": self._extract_attr(point, k) for k in valid_fields}
        if label:
            additional_data["name"] = self.extract_place(point)
        if hint:
            additional_data["hint"] = self.extract_hint(point)

        jsonified = dict(
            coords=[self.extract_lat(point), self.extract_lon(point)],
            data=dict(
                rank=self.extract_group(point),
                group=max(0, self.extract_group(point) - self.scale_index),
                **additional_data
            ),
        )
        return jsonified

    def get_geometry(self, max_points=400, **kwargs):
        samples = self.df.sample(min(max_points, len(self.df))) if max_points > 0 else self.df
        points = [self.jsonify_point(p, **kwargs) for p in samples.itertuples()]
        groups = self.extract_group()
        min_rank = min(groups)
        max_rank = max(groups)
        bbox = self.bounding_box()
        return dict(dataset=self.name, points=points, bbox=bbox,
                    stats=dict(
                        min_rank=min_rank,
                        max_rank=max_rank,
                        level=dict(
                            min=self.scale_index,
                            max=self.available_levels-1,
                            current=self.default_level
                        )
                    )
                    )

    def get_dataframe_as_json(self):
        records = list(self.df.to_dict("records"))
        columns = list(self.df.columns)
        converter = {k: getattr(self, "col_" + k)
                     for k in ["lon", "lat", "group", "hint", "place"]}
        bbox = self.bounding_box()
        return dict(dataset=self.name, points=records, bbox=bbox, columns=columns, converter=converter)

    def get_distance(self):
        corner1, corner2 = self.bounding_box()
        p1 = Point.from_latlon(*corner1)
        p2 = Point.from_latlon(*corner2)
        dist = distance(p1, p2)

        dist_param = dist ** self.harshness
        print(self.name, dist_param)
        return dist_param

    def sample_from_group(self, group):
        return self.df[self.extract_group() == group].sample(1).iloc[0]

    def sample_many_from_group(self, group, k):
        return list(self.df[self.extract_group() == group].sample(k).itertuples())

    def point_to_places(self, point):
        displayed_hint = (self.extract_place(point), self.extract_hint(point))
        ground_truth = Point(self.extract_lon(point), self.extract_lat(point))
        return displayed_hint, ground_truth

    def sample(self, k, level=None, verbose=False):
        if level is None:
            level = self.default_level
        level = round(level)
        if level >= self.available_levels:
            if verbose: print(f"Changed level from {level} to {self.available_levels-1}")
            level = self.available_levels - 1
        if level < 0: level = 0
        if verbose: print(f"{self.name} : level = {level}")
        if verbose: print("Weights :", *self.weights)
        if verbose: print("Counts :", *self.counts)

        weights = [w * self.counts[g] for g, w in enumerate(self.weights[level])]
        normalized_weights = [w / sum(weights) for w in weights]
        if verbose: print("Weights", ", ".join([f"P(G{g}) = {w:.4f}" for g, w in enumerate(normalized_weights)]))

        groups = random.choices(range(len(weights)), weights=weights, k=k)

        report = 0
        places = []
        for group, sample_size in Counter(groups).items():
            if verbose: print(f"{self.name} : {sample_size} places to sample from group G{group}, "
                              f"out of {self.counts[group]}, "
                              f"plus {report} places reported from previous group")
            sample_size += report
            if self.counts[group] < sample_size:
                report = sample_size - self.counts[group]
                sample_size = self.counts[group]
            else:
                report = 0
            places += self.sample_many_from_group(group, sample_size)
        random.shuffle(places)
        return [self.point_to_places(p) for p in places]

