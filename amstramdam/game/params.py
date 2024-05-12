import datetime

from pydantic import BaseModel, Field

from amstramdam.game.types import Player, Pseudo, GameName
from amstramdam.settings import settings


class GameParams(BaseModel):
    """Represents user-defined parameters about a game.

    Attributes:
        dataset_name: unique identifier of the dataset
        level: difficulty level (usually ranging from 0 to 2). Valid levels depends on the chosen dataset
        is_public: if True, the game will be visible in the _Existing games_ tab. Otherwise, it will be assigned a
            12-character random identifier and won't appear on the lobby page
        is_permanent: if True, the game will be marked as _permanent_ and won't be deleted when all players exit. For
            now, this is only used for debugging
        precision_mode: if True, time won't be used for scoring
        wait_duration: duration between two runs. Reducing it can be useful in single-player mode or when debugging
        n_runs: number of runs in a game
        run_duration: duration of a run
    """
    dataset_name: str
    level: int = 0
    is_public: bool = True
    is_permanent: bool = False
    precision_mode: bool = False
    wait_duration: int = settings.game.wait_duration
    n_runs: int = settings.game.n_runs
    run_duration: int = settings.game.run_duration


class GameMetadata(BaseModel):
    """Internal metadata about a game.

    Attributes:
        name: unique name of the game. Will appear in the URL
        players: unique player names
        nicknames: mapping from player names to their nicknames (or display names)
        creation_date: date and time when the game was created
    """
    name: GameName
    players: set[Player] = Field(default_factory=set)
    nicknames: dict[Player, Pseudo] = Field(default_factory=dict)
    creation_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
