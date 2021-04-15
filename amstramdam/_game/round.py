from typing import Optional
import time

from amstramdam._types.game import Place, Coordinates, RoundRecord
from amstramdam._game import geo
from amstramdam._game.player import PlayerList, PlayerId
from amstramdam._game.scorer import Scorer


class GameRound:
    """
    Represent a single game round, that is:
    - a place to guess
    - round params (e.g scoring constants)
    - a list of players
    - results for each player

    Input:
    - a place to guess
    - a scorer
    - a list of players?
    Output
    - results for each player

    TODO: add serialization/deserialization or a copy mechanism
    """
    def __init__(self, place: Place, players: PlayerList, scorer: Scorer) -> None:
        self.place = place
        self.players = players
        self.scorer = scorer

        self.records: dict[PlayerId, RoundRecord] = {}
        self._start: Optional[float] = None
        self._remaining_players = self.players.ids.copy()

    def display(self) -> str:
        # TODO: remove?
        if self.place["hint"]:
            return f"{self.place['name']} ({self.place['hint']})"
        return self.place["name"]

    def launch(self) -> str:
        self.on_run_start()
        return self.display()

    def on_run_start(self) -> None:
        # TODO: add logging
        self._start = time.time()

    def on_run_end(self) -> Place:
        return self.place

    @property
    def is_done(self) -> bool:
        game_done = len(self._remaining_players) == 0
        if game_done:
            self.on_run_end()
        return game_done

    def process_answer(self, player: PlayerId, answer: Coordinates) -> tuple[RoundRecord, bool]:
        if player not in self.players:
            raise KeyError(f"Unknown player: <{player}>")
        if self._start is None:
            raise ValueError("Game has not started, unable to process answers yet.")
        if player not in self._remaining_players:
            # TODO: raise Warning or Error
            return self.records[player], self.is_done
        self._remaining_players.remove(player)

        duration = time.time() - self._start
        distance = geo.distance(self.place["coords"], answer)
        scores = self.scorer.score(distance, duration)

        record = {
            "player": player,
            "answer": self.place,
            "guess": answer,
            "score": scores
        }
        self.records[player] = record

        return record, self.is_done

    def get_records(self) -> list[RoundRecord]:
        return list(self.records.values())

