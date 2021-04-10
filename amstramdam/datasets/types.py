from typing import TypedDict, Optional, Union, Literal, Any, Iterable
import pandas as pd


class Filter(TypedDict, total=False):
    column: str
    method: str
    values: Union[list, tuple, set]

Mask = Optional[pd.DataFrame]
Rank = Union[int, Literal["all"]]

PointCreationRecord = dict[str, Any]
PointUpdateRecord = dict[str, Any]

GuessRecord = tuple[tuple[str, str], "Point"]

class PointChangeRecords(TypedDict, total=False):
    create: list[PointCreationRecord]
    update: dict[str, PointUpdateRecord]
    output: str


class DatasetDescriptor(TypedDict, total=True):
    pass

class DatasetDescriptorWithGroup(DatasetDescriptor):
    group: int

DatasetParams = dict[str, Any]

class LevelDescription(TypedDict):
    index: int
    name: str

class DatasetInformation(TypedDict):
    map_id: str
    name: str
    default_level: int
    levels: list[LevelDescription]

class DatasetGroup(TypedDict):
    maps: list[DatasetParams]
    group: str

class FilteredDatasetGroup(TypedDict):
    maps: list[DatasetInformation]
    group: str

GroupedDatasets = list[DatasetGroup] # list[dict[str, DatasetParams]]
FilteredGroupedDatasets = list[FilteredDatasetGroup]
FlattenedDatasets = dict[str, DatasetParams]
BoundingBoxArray = list[list[float]]

class PointData(TypedDict):
    rank: int
    group: int

class JsonifiedPoint(TypedDict):
    coords: tuple[float, float]
    data: PointData

class DatasetGeometry(TypedDict):
    dataset: str
    bbox: BoundingBoxArray
    points: list[JsonifiedPoint]
    stats: dict[Any, Any]

class JsonifiedDataset(TypedDict):
    dataset: str
    points: list[Any]
    bbox: BoundingBoxArray
    columns: list[str]
    converter: dict[str, str]

Weight = float
GroupWeights = list[Weight]
LevelWeights = list[GroupWeights]
MapWeights = list[LevelWeights]