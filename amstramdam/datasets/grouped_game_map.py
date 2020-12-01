import random
from collections import Counter
from amstramdam.game.geo import Point, distance


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

        # Map data
        if col_group not in df.columns:
            # When no group is provided, automatically activate single group mode
            df[col_group] = 0
            available_levels = 1
            default_level = 0
        if col_hint not in df.columns or not use_hint:
            df[col_hint] = ""
        self.df = df.rename(columns={
            col_place: "place", col_hint: "hint",
            col_lon: "lon", col_lat: "lat", col_group: "group"})
        print(self.df.head())
        print(self.df[["group", "place"]].groupby(by="group").count())
        self.counts = self.df.groupby(by="group").place.count()

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
                [self.df.lat.max(), self.df.lon.min()],
                [self.df.lat.min(), self.df.lon.max()],
            ]
        return self.bbox

    def jsonify_point(self, point, label=False, hint=False):
        """
        Convert a `point`, represented as a NamedTuple, to a JSON-ifiable format, ready to be sent over HTTP to the
        client. The JSON-like outpout contains two keys:
        - `coords`, a `[lat, lon]` array of geographic coordinates
        - `data`, extra data attached to the point (e.g its name, rank, group)
        """
        jsonified = dict(
            coords=[point.lat, point.lon],
            data=dict(
                rank=point.group,
                group=max(0, point.group - self.scale_index))
        )
        if label: jsonified["data"]["name"] = point.place
        if hint: jsonified["data"]["name"] = point.admin
        return jsonified

    def get_geometry(self, labels=False, max_points=400):
        points = [self.jsonify_point(p, label=labels) for p in self.df.sample(min(max_points, len(self.df))).itertuples()]
        min_rank = min(self.df.group)
        max_rank = max(self.df.group)
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

    def get_distance(self):
        corner1, corner2 = self.bounding_box()
        print(corner1, corner2)
        p1 = Point.from_latlon(*corner1)
        p2 = Point.from_latlon(*corner2)
        dist = distance(p1, p2)

        dist_param = dist ** self.harshness
        print(self.name, dist_param)
        return dist_param

    def sample_from_group(self, group):
        return self.df[self.df.group == group].sample(1).iloc[0]

    def sample_many_from_group(self, group, k):
        return list(self.df[self.df.group == group].sample(k).itertuples())

    def sample(self, k, level=None, verbose=True):
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
        return [((p.place, p.hint), Point(p.lon, p.lat)) for p in places]

