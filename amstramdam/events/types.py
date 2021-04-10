from typing import TypedDict, Mapping, Optional

from amstramdam.game.types import Leaderboard, PlayerFinalResult, GameFinalResults


class ChatMessage(TypedDict):
    author: str
    message: str


class NameChangePayload(TypedDict):
    name: str

class ConnectionPayload(TypedDict, total=False):
    pseudo: str

class NewNameNotification(TypedDict):
    player: str
    pseudo: str

class GameChangeNotification(TypedDict):
    name: str
    url: str
    map_name: str
    player: str

class GameEndPayload(TypedDict):
    leaderboard: Leaderboard
    full: GameFinalResults

class GameEndNotification(TypedDict):
    status: str
    payload: GameEndPayload

class Guess(TypedDict):
    lon: float
    lat: float


class PlayerLeftNotification(TypedDict):
    player: str

class NewPlayerNotification(TypedDict):
    player: str
    pseudo: Optional[str]
    score: PlayerFinalResult

class InitNotification(TypedDict):
    player: str
    launched: bool
    pseudo: Optional[str]
    game: str
    current: int
    runs: int
    diff: int
    game_name: str
    leaderboard: Leaderboard
    pseudos: dict[str, str]

class RedirectNotification(TypedDict):
    url: str

class PartialGameParams(TypedDict, total=False):
    map: str
    duration: int
    zoom: bool
    runs: int
    wait_time: int
    difficulty: int
    public: bool
    precision_mode: bool