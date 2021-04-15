from typing import NewType, TypedDict

PlayerId = NewType("PlayerId", str)
PlayerName = NewType("PlayerName", str)


class Coordinates(TypedDict):
    lon: float
    lat: float


class Place(TypedDict):
    name: str
    hint: str
    coords: Coordinates


class RoundScore(TypedDict):
    distance: float
    duration: float
    distance_score: float
    time_score: float
    score: int


class RoundRecord(TypedDict):
    player: PlayerId
    answer: Place
    guess: Coordinates
    score: RoundScore
