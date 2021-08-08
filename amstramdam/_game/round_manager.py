from amstramdam._game.player import PlayerList, PlayerId, PlayerName
from typing import Union, Optional, Any, Callable, Iterable
from amstramdam._types.game import (
    GameName,
    BoundingBoxArray,
    Coordinates,
    Place,
    RoundRecord,
)
from amstramdam._game.scorer import ScoringParams, Scorer
from amstramdam._game.round import GameRound
from amstramdam._game import geo
from amstramdam._game.status import Status
from amstramdam._game import status
import datetime
from dataclasses import dataclass, field


class RoundManager:
    """
    Represent a sequence of rounds, built from:
    - a list of places
    - a list of players
    - a scorer
    - parameters
    """

    def __init__(
        self,
        places: list[Place],
        players: PlayerList,
        scoring_params: Optional[ScoringParams] = None,
    ) -> None:
        self.places = places
        self.players = players
        if scoring_params is None:
            scoring_params = dict()
        self.scorer = Scorer(**scoring_params)
        self.rounds = self._init_rounds()
        self._current_round_id = 0
        self.done = False

    def _init_rounds(self) -> list[GameRound]:
        return [GameRound(place=place, players=self.players, scorer=self.scorer) for place in self.places]

    @property
    def records(self) -> list[list[RoundRecord]]:
        return [round_.get_records() for round_ in self.rounds]

    @property
    def current_index(self) -> int:
        return self._current_round_id

    @current_index.setter
    def current_index(self, value: int) -> None:
        if value >= len(self.rounds):
            value = len(self.rounds) - 1
            self.done = True
        self._current_round_id = value

    @property
    def current(self) -> GameRound:
        return self.rounds[self.current_index]

    def launch_next(self):
        return self.current.launch()

    def __len__(self) -> int:
        return len(self.rounds)

    def __iter__(self) -> Iterable[GameRound]:
        return iter(self.rounds)

    def __getitem__(self, item: int) -> GameRound:
        return self.rounds[item]

    def end_current(self):
        self.current_index += 1

    def get_results(self):
        pass