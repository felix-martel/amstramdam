from amstramdam._game.player import PlayerList, PlayerId, PlayerName
from typing import Union, Optional, Any, Callable, Iterable

from amstramdam._game.round_manager import RoundManager
from amstramdam._types.game import GameName, BoundingBoxArray, Coordinates, Place, RoundRecord
from amstramdam._game.scorer import ScoringParams, Scorer
from amstramdam._game.round import GameRound
from amstramdam._game import geo
from amstramdam._game.status import Status
from amstramdam._game import status
import datetime
from dataclasses import dataclass, field


class GameMap:
    def __init__(self):
        self.id = "foo_bar"
        self.name = "Foo Bar"
        self.bbox: BoundingBoxArray = ((0., 1.), (1., 0.))

    def get_characteristic_distance(self) -> float:
        (west, north), (east, south) = self.bbox
        north_west = {"lon": west, "lat": north}
        south_east = {"lon": east, "lat": south}
        return geo.distance(north_west, south_east)

    def sample(self, k: int) -> list[Place]:
        # TODO: implement sampling
        (west, north), (east, south) = self.bbox
        lon = (west + east) / 2
        lat = (north + south) / 2
        place = {"lon": lon, "lat": lat, "name": "Here", "hint": "or elsewhere"}
        return k * [place]


@dataclass
class GameParams:
    n_rounds: int = 10
    is_permanent: bool = False
    round_duration: int = 10
    wait_duration: int = 7
    level: int = 0
    scoring: ScoringParams = field(default_factory=dict)


GAME_SUMMARY_PATTERN = """
Game <{game}>, round {current_round}/{n_rounds}
- Map: {map_name}, level {level}
- Places: {places}
- Players: {players}
"""


class Game:
    """
    Represent a game, that is:
    - a list of game rounds
    - a list of players
    Since all rounds have the same params, it may be:
    - round params
    - a list of game rounds
    - a list of players
    """

    def __init__(
        self,
        name: GameName,
        game_map: GameMap,
        players: Optional[PlayerList] = None,
        creation_date: Optional[datetime.datetime] = None,
        params: Optional[GameParams] = None
    ) -> None:
        self.name = name
        self.map = game_map
        if params is None:
            params = GameParams()
        self.params = params
        self.scorer = Scorer(**self.params.scoring)

        if players is None:
            players = PlayerList(self.name)
        self.players = players

        if creation_date is None:
            creation_date = datetime.datetime.now()
        self.creation_date = creation_date
        self.places = self.map.sample(self.params.n_rounds)
        self.rounds = RoundManager(
            places=self.places,
            players=self.players,
            scoring_params=self.params.scoring,
        )

        self._current_round_id = 0
        self.done = False
        self.status: Status = status.NOT_LAUNCHED

    def summary(self) -> str:
        return GAME_SUMMARY_PATTERN.format(
            game=self.name,
            current_round=self.rounds.current_index + 1,
            n_rounds=self.params.n_rounds,
            map_name=self.map.name,
            level=self.params.level,
            players=", ".join(self.players.names),
            places=", ".join([place["name"] for place in self.places])
        )

    @property
    def done(self):
        return self.rounds.done

    def get_params(self):
        return {
            "name": self.name,
            "game_map": self.map,
            "players": self.players,
            "creation_date": self.creation_date,
            "params": self.params,
        }

    def launch(self) -> None:
        self.status = status.LAUNCHING

    def launch_round(self) -> str:
        self.status = status.RUNNING
        return self.rounds.launch_next()

    def is_expired(self, hours: int = 6) -> bool:
        if self.params.is_permanent:
            return False
        expiration_date = self.creation_date + datetime.timedelta(hours=hours)
        return len(self.players) == 0 and datetime.now() > expiration_date

    def on_game_end(self) -> None:
        pass

    def end(self):
        self.status = status.CORRECTION
        self.rounds.end_current()

        if self.done:
            self.on_game_end()
            results = self.rounds.get_results()
            return results, self.done

        return self.rounds.current, self.done
