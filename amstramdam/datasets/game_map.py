import random
from typing import TypeVar, Any, Optional
from collections import Counter

from amstramdam.datasets.types import (
    BoundingBoxArray,
    DatasetGeometry,
    JsonifiedPoint,
    JsonifiedDataset,
)
from amstramdam.game.game import PlaceToGuess
from amstramdam.game.geo import Point, distance
from amstramdam.datasets.dataframe import UnifiedDataFrame

T = TypeVar("T")


def arg_or_default(value: Optional[T], default: T) -> T:
    if value is None:
        return default
    return value


class GameMap:
    def __init__(
        self,
        name: str,
        map_id: str,
        udf: UnifiedDataFrame,
        harshness: Optional[float] = None,
        weights: Optional[list[float]] = None,
        min_group: int = 0,
        max_group: Optional[int] = None,
        **extra_params: Any
    ) -> None:
        self.name = name
        self.map_id = map_id
        self.df = udf
        self.counts: Counter[int] = Counter(udf.group)
        self.min_group = min_group
        if max_group is None:
            max_group = self.df.group.max()
        self.max_group = max_group
        # Samping weights
        self._weights: list[float] = arg_or_default(weights, [1.0] * len(self.counts))
        self.weights = self.normalize_weights(self._weights)

        self.harshness = arg_or_default(harshness, 0.7)
        self.bbox = self.get_bounding_box()
        self.char_dist = self.get_characteristic_distance()

    def get_bounding_box(self) -> BoundingBoxArray:
        return [
            [self.df.lat.max(), self.df.lon.min()],
            [self.df.lat.min(), self.df.lon.max()],
        ]

    def get_characteristic_distance(self) -> float:
        north_west, south_east = self.bbox
        p1 = Point.from_latlon(*north_west)
        p2 = Point.from_latlon(*south_east)

        return distance(p1, p2)

    @property
    def distance(self) -> float:
        return self.char_dist ** self.harshness

    def get_geometry(self, max_points: int = 400) -> DatasetGeometry:
        data = self.df
        if max_points > 0:
            data = data.sample(min(max_points, len(data)))
        points = [self.jsonify_point(p) for p in data.to_dict("records")]
        return dict(
            dataset=self.name,
            bbox=self.bbox,
            points=points,
            stats=dict(),  # <- TODO
        )

    def normalize_weights(self, weights: list[float]) -> Counter[int]:
        # Crop weights above and below max group
        weights = weights[slice(self.min_group, self.max_group + 1)]
        weights = [w * self.counts[group] for group, w in enumerate(weights)]
        return Counter(
            {group: weight / sum(weights) for group, weight in enumerate(weights)}
        )

    def jsonify_dataset(self) -> JsonifiedDataset:
        records = list(self.df.to_records("records", renamed=False))
        return dict(
            dataset=self.name,
            points=records,
            bbox=self.bbox,
            columns=list(self.df.columns),
            converter=self.df.converter,
        )

    def jsonify_point(self, point: dict[str, Any]) -> JsonifiedPoint:
        return dict(
            coords=(point["lat"], point["lon"]),
            data=dict(rank=point["group"], group=point["group"]),
        )

    def guessify_point(self, point: dict[str, Any]) -> PlaceToGuess:
        return ((point["place"], point["hint"]), Point(point["lon"], point["lat"]))

    def sample(self, k: int, verbose: bool = True) -> list[PlaceToGuess]:
        mask = self.df.group >= self.min_group
        if self.max_group is not None:
            mask = mask & (self.df.group <= self.max_group)
        probabilities = [self.weights[group] for group in self.df[mask].group]
        points = (
            self.df[mask]
            .sample(k, replace=False, weights=probabilities)
            .to_dict("records")
        )
        random.shuffle(points)
        return [self.guessify_point(point) for point in points]
