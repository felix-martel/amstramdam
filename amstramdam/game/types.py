
from typing import (
    Optional,
    Any,
    Callable,
    TypedDict,
    Mapping,
    NewType,
    Union,
    Literal,
)
from datetime import datetime

Hint = tuple[str, Optional[str]]
GameName = NewType("GameName", str)
Player = NewType("Player", str)
Pseudo = NewType("Pseudo", str)
PlayerList = set[Player]
CoordinatesTuple = tuple[float, float]
Callback = Callable[..., Any]
MetricSummary = Union[float, Literal["-"]]


class Coordinates(TypedDict):
    lon: float
    lat: float


class Answer(Coordinates):
    name: str


class Record(TypedDict):
    dist: float
    delta: float
    score: int
    msg: str
    guess: Coordinates
    answer: Answer
    player: Player
    st: float
    sd: float


class PlaceDict(Coordinates):
    location: str
    hint: str


class RunResults(TypedDict):
    scores: Mapping[Player, float]
    messages: Mapping[Player, str]
    distances: Mapping[Player, float]
    durations: Mapping[Player, float]


class PlayerFinalResult(TypedDict):
    player: Player
    dist: MetricSummary
    delta: MetricSummary
    score: float


class GameRunParams(TypedDict):
    players: set[Player]
    dist_param: int
    time_param: int
    duration: int


class GameMetrics(TypedDict):
    distance: Mapping[Player, list[float]]
    delay: Mapping[Player, list[float]]


class GameParams(GameRunParams):
    n_run: int
    map: str
    pseudos: dict[Player, Pseudo]
    wait_time: int
    difficulty: int
    is_public: bool
    is_permanent: bool
    creation_date: datetime
    allow_zoom: bool
    precision_mode: bool


class FullGameRunParams(GameRunParams):
    precision_mode: bool
    non_linear: bool


class GameFinalResults(TypedDict):
    records: list[list[dict[str, Any]]]
    places: list[PlaceDict]


class AvailableGames(TypedDict):
    name: GameName
    map: str
    players: int
    difficulty: float


class FilledGameParams(TypedDict):
    map: str
    duration: int
    zoom: bool
    runs: int
    wait_time: int
    difficulty: int
    public: bool
    precision_mode: bool


Leaderboard = list[PlayerFinalResult]
