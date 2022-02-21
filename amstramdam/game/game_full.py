from typing import Any, Iterable, Optional, Union
import string
from collections import defaultdict, Counter
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from .game import GameRun, load_cities, PlaceToGuess
from ..datasets import dataloader
import random
import amstramdam.game.status as status
from amstramdam.datasets.game_map import GameMap
from amstramdam import utils
from .types import (
    Player,
    Pseudo,
    GameParams,
    PlaceDict,
    Record,
    GameMetrics,
    FullGameRunParams,
    GameFinalResults,
    MetricSummary,
    PlayerFinalResult,
    Leaderboard,
    GameName,
)

with open("data/player_names.txt", "r", encoding="utf8", errors="ignore") as f:
    NAMES: set[Pseudo] = {Pseudo(line.rstrip()) for line in f}


def choose_countries(
    df: pd.DataFrame, max_per_country: int = 10, max_rank: int = 1000
) -> pd.DataFrame:
    countries: Counter[str] = Counter()
    cities = []
    for i, row in df.iterrows():
        country = row["country"]
        if country not in countries or (
            i < max_rank and countries[country] < max_per_country
        ):
            countries[country] += 1
            cities.append(
                {k: row[k] for k in ["name", "country", "lat", "lon", "population"]}
            )
    return pd.DataFrame(cities)


def choose_depts(
    df: pd.DataFrame, max_per_country: int = 10, min_pop: int = 15
) -> pd.DataFrame:
    data = df.to_dict("records")
    countries: Counter[str] = Counter()
    cities = []
    for row in sorted(data, key=lambda p: -p["population"]):
        country = row["dept"]
        if country not in countries or (
            min_pop < row["population"] and countries[country] < max_per_country
        ):
            countries[country] += 1
            cities.append(
                {k: row[k] for k in ["name", "dept", "lat", "lon", "population"]}
            )
    return pd.DataFrame(cities)


available_names: set[Pseudo] = set(NAMES)
global_player_list: set[Player] = set()


def get_cities(map: dict[str, Any]) -> Iterable[PlaceToGuess]:
    return load_cities(map["fname"], map["min-pop"])


class Game:
    def __init__(
        self,
        name: GameName,
        players: Optional[set[Player]] = None,
        n_run: int = 20,
        time_param: int = 5,
        dist_param: Optional[int] = None,
        is_permanent: bool = False,
        precision_mode: bool = False,
        difficulty: int = 0,
        is_public: bool = False,
        creation_date: Optional[datetime] = None,
        allow_zoom: bool = False,
        duration: int = 10,
        wait_time: int = 8,
        map: str = "world",
        pseudos: Optional[dict[Player, Pseudo]] = None,
        # **kwargs,
    ) -> None:
        self.name = name
        self.map_name = map
        game_map: GameMap = dataloader.load(
            self.map_name, difficulty
        )  # GameMap.from_name(self.map_name)
        self.map_display_name = game_map.name
        self.is_permanent = is_permanent
        if dist_param is None:
            dist_param = game_map.distance
        self.bbox = game_map.bbox
        # self.map_info = map
        self.difficulty = difficulty
        self.n_run = n_run
        self.dist_param = dist_param
        self.time_param = time_param
        self.precision_mode = precision_mode
        self.small_scale = (
            dist_param < 15
        )  # When the characteristic distance is below 15km
        self.__curr_run_id = 0
        self.allow_zoom = allow_zoom
        if players is None:
            players = set()
        self.players = set(players)
        self.places = game_map.sample(
            self.n_run
        )  # random.sample(get_cities(map), self.n_run)
        self.duration = duration
        self.runs = [
            GameRun(place=place, **self.get_run_params()) for place in self.places
        ]
        # names = list(NAMES - self.players)
        # random.shuffle(names)
        self.global_player_list = global_player_list
        self.available_names = available_names.copy()  # set(names)
        self.wait_time = wait_time
        self.records: list[list[Record]] = []  # defaultdict(list)
        self.scores: defaultdict[Player, int] = defaultdict(int)
        self.is_public = is_public
        if pseudos is None:
            pseudos = dict()
        pseudos = {k: v for k, v in pseudos.items() if k in self.players}
        self.done = False
        self.pseudos = pseudos
        self.metrics: GameMetrics = dict(
            distance=defaultdict(list), delay=defaultdict(list)
        )

        if creation_date is None:
            creation_date = datetime.now()
        self.date_created: datetime = creation_date
        self.launched: bool = False
        self.status = status.NOT_LAUNCHED
        self.__id_counter = len(self.players)
        # self.run_in_progress = False

    def get_new_id(self) -> str:
        return utils.random.generate_random_identifier(length=16)

    def generate_player_name(self) -> Player:
        return Player(f"{self.name}_{self.get_new_id()}")

    def get_run_params(self) -> FullGameRunParams:
        return FullGameRunParams(
            players=self.players,
            dist_param=self.dist_param,
            time_param=self.time_param,
            precision_mode=self.precision_mode,
            duration=self.duration,
            non_linear=not self.allow_zoom,
        )

    def get_params(self) -> GameParams:
        return GameParams(
            players=set(self.players),
            n_run=self.n_run,
            time_param=self.time_param,
            dist_param=self.dist_param,
            duration=self.duration,
            map=self.map_name,
            # map_display=self.map_display_name,
            pseudos=self.pseudos,
            wait_time=self.wait_time,
            difficulty=self.difficulty,
            is_public=self.is_public,
            is_permanent=self.is_permanent,
            creation_date=self.date_created,
            allow_zoom=self.allow_zoom,
            precision_mode=self.precision_mode,
        )

    @property
    def curr_run_id(self) -> int:
        return self.__curr_run_id

    @curr_run_id.setter
    def curr_run_id(self, value: int) -> None:
        if value >= len(self.runs):
            value = len(self.runs) - 1
            self.done = True
        self.__curr_run_id = value

    def __str__(self) -> str:
        return f"""---
Amstramdam {'Public' if self.is_public else 'Private'} Game
Map: {self.map_display_name}
Difficulty: {100. * self.difficulty:.0f}%
Players: {self.print_pseudos()}
Places: {', '.join([p[0][0] for p in self.places])}
Run: {self.curr_run_id + 1}/{self.n_run}
---"""

    def generate_new_pseudo(self) -> Pseudo:
        if self.available_names:
            pseudo = self.available_names.pop()
        else:
            pseudo = random.choice(list(NAMES))
        return Pseudo(pseudo)

    def print_pseudos(self) -> str:
        pseudos = []
        for player in self.players:
            pseudo = self.get_pseudo(player)
            if pseudo and str(pseudo) != str(player):
                pseudos.append(f"{player} ({pseudo})")
            else:
                pseudos.append(player)
        return ", ".join(pseudos)

    def add_player(
        self, name: Optional[Player] = None, pseudo: Optional[Pseudo] = None
    ) -> tuple[Player, Pseudo]:
        if name is not None:
            assert (
                name not in self.global_player_list and name not in self.players
            ), f"Name '{name}' already exists"
            # assert name not in self.players, f"Name '{name}' already exists"
        else:
            name = self.generate_player_name()
            while name in self.players:
                name = self.generate_player_name()  # self.available_names.pop()
        self.players.add(name)
        self.global_player_list.add(name)
        if pseudo is None:
            pseudo = self.generate_new_pseudo()
        self.add_pseudo(name, pseudo)

        return name, pseudo

    def add_pseudo(self, name: Player, pseudo: Pseudo) -> None:
        if name not in self.players:
            print(f"Ignored unknown player '{name}'")
        self.pseudos[name] = pseudo

    def request_pseudo(self, name: Player) -> Pseudo:
        pseudo = self.generate_new_pseudo()
        self.add_pseudo(name, pseudo)
        return pseudo

    def remove_pseudo(self, name: Player) -> None:
        if name in self.pseudos:
            del self.pseudos[name]

    def get_pseudo(self, name: Player) -> Pseudo:
        return self.pseudos.get(name, Pseudo(name))

    def remove_player(self, name: Player) -> None:
        if name in self.global_player_list:
            self.global_player_list.remove(name)

        if name not in self.players:
            return
        # if name in NAMES:
        #     self.available_names.add(name)
        self.players.remove(name)
        self.remove_pseudo(name)
        # if name in self.records:
        #     del self.records[name]
        if name in self.scores:
            del self.scores[name]

    @property
    def current(self) -> GameRun:
        # if self.done:
        #     return self.runs[-1]
        return self.runs[self.curr_run_id]

    def launch(self) -> GameRun:
        self.launched = True
        self.status = status.LAUNCHING
        return self.current  # .launch()

    def launch_run(self, *args: Any, **kwargs: Any) -> str:
        self.status = status.RUNNING
        return self.current.launch(*args, **kwargs)

    def is_expired(self, hours: int = 6) -> bool:
        """Kwargs must be valid arguments for timedelta"""
        if self.is_permanent:
            return False
        expiration_date = self.date_created + timedelta(seconds=3600 * hours)
        return len(self.players) == 0 and expiration_date < datetime.now()

    @property
    def old_done(self) -> bool:
        return self.curr_run_id >= self.n_run

    def on_game_end(self) -> None:
        print("Game ended!")

    def places_as_json(self) -> list[PlaceDict]:
        return [
            PlaceDict(location=place[0], hint=place[1], lon=point.lon, lat=point.lat)
            for place, point in self.places
        ]

    def get_final_results(self) -> GameFinalResults:
        distances = defaultdict(list)
        durations = defaultdict(list)
        for recs in self.records:
            for rec in recs:
                player = rec["player"]
                distances[player].append(rec["dist"])
                durations[player].append(rec["delta"])

        final_results = GameFinalResults(
            records=self.get_filtered_records(),
            # scores=self.scores,
            places=self.places_as_json(),
            # summary=results
        )
        return final_results

    def get_filtered_records(
        self, keys: Optional[list[str]] = None
    ) -> list[list[dict[str, Any]]]:
        """
        `self.records` contains a lot of information. This function filters it by
        keeping only the keys specified in `keys`. If not provided, `keys = ["guess",
        "player"]`, which are necessary for the final summary display.
        `self.records` contains, per each run, one record dict per player with the
        following keys:
        - guess (guess.lon, guess.lat): coordinates of the player's guess for this run
        - answer (answer.lon, answer.lat, answer.name): coordinates of the ground truth
        for this run
        - dist: distance between guess and ground truth
        - delta: player's answering time
        - score: points awarded to the player for this run
        - msg: a human-readable message describing the player's result for this run
        - player: player id
        - st: time bonus
        - sd: distance bonus (time bonus + distance bonus = score)
        See output of `GameRun.process_answer` for details.
        """
        if keys is None:
            keys = ["guess", "player"]
        records = [[{k: rec[k] for k in keys} for rec in recs] for recs in self.records]
        return records

    def add_run_records(self, recs: list[Record]) -> None:
        self.records.append(recs)
        for rec in recs:
            player = rec["player"]
            self.metrics["distance"][player].append(rec["dist"])
            self.metrics["delay"][player].append(rec["delta"])

    def end(self) -> tuple[Union[GameRun, GameFinalResults], bool]:
        self.status = status.CORRECTION

        recs = self.current.records
        self.add_run_records(recs)

        for player in self.players:
            self.scores[player] += self.current.scores[player]
        self.curr_run_id += 1
        if self.done:
            self.on_game_end()
            results = self.get_final_results()
            return results, self.done
        return self.current, self.done

    def terminate(self) -> None:
        self.status = status.FINISHED

    def safe_median(self, values: Iterable[float]) -> MetricSummary:
        if not values:
            return "-"
        median: float = np.median(values)
        return median

    def avg_distance(self, player: Player) -> MetricSummary:
        return self.safe_median(self.metrics["distance"].get(player, []))

    def avg_delta(self, player: Player) -> MetricSummary:
        return self.safe_median(self.metrics["delay"].get(player, []))

    @property
    def n_players(self) -> int:
        return len(self.players)

    def get_player_score(self, player: Player) -> PlayerFinalResult:
        return PlayerFinalResult(
            player=player,
            score=self.scores[player],
            dist=self.avg_distance(player),
            delta=self.avg_delta(player),
        )

    def get_current_leaderboard(self) -> Leaderboard:
        """Players with their scores, ranked by decreasing scores"""
        return list(
            sorted(
                [self.get_player_score(player) for player in self.players],
                key=lambda t: -t["score"],
            )
        )
