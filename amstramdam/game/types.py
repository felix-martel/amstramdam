from typing import Iterable, Optional, Any, Callable, TypedDict, Mapping


Hint = tuple[str, Optional[str]]

Player = str
PlayerList = list[Player]
CoordinatesTuple = tuple[float, float]
Callback = Callable[..., Any]


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


class RunResults(TypedDict):
    scores: Mapping[Player, float]
    messages: Mapping[Player, str]
    distances: Mapping[Player, float]
    durations: Mapping[Player, float]


class GameRunParams(TypedDict):
    players: set[Player]
    dist_param: float
    time_param: float
    duration: int
