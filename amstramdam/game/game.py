from typing import Iterable, Optional
import time
import pandas as pd

from collections import defaultdict
from .geo import Point, distance
from .types import (
    Hint,
    Player,
    PlayerList,
    Coordinates,
    CoordinatesTuple,
    Callback,
    Answer,
    Record,
    RunResults,
    GameRunParams,
)


PlaceToGuess = tuple[Hint, Point]


def capit(s: str) -> str:
    stopwords = {"en", "le", "la", "les", "d", "de", "du", "des", "sur"}
    if s.lower() in stopwords:
        return s
    return s[0].upper() + s[1:]


def reaccent(name: str) -> str:
    name = name.lower()
    seps = {" ", "-", "'"}
    for sep in seps:
        name = sep.join([capit(word) for word in name.split(sep)])
    return capit(name)


def clean_city(city: str) -> str:
    if city.isupper():
        return reaccent(city)
    return city


def load_cities(
    fname: str = "data/places.world.csv", min_pop: int = 0
) -> Iterable[PlaceToGuess]:
    df = pd.read_csv(fname)
    if "country" not in df.columns:
        df["country"] = ""
    if "dept" in df.columns:
        idf = {"75", "78", "91", "92", "93", "94", "95"}
        is_idf = df.dept.isin(idf)
        mask = (~is_idf & (df.population > min_pop)) | (
            is_idf & (df.population > 3 * min_pop)
        )
        df = df[mask]
    else:
        df = df[df.population > min_pop]
    return {
        ((clean_city(city), country), Point(lon, lat))
        for city, country, lon, lat in zip(df.name, df.country, df.lon, df.lat)
    }


MSG_TEMPLATE: str = """Distance: {dist:.1f}km (+{sd:.0f} pts)
Time: {delta:.2f}s (+{st:.0f} pts)

Score: +{score} pts
"""


class GameRun:
    SCORE_MULTIPLIER = 1000

    def __init__(
        self,
        players: PlayerList,
        place: PlaceToGuess,
        forbidden: Optional[bool] = None,
        dist_param: Optional[int] = None,
        time_param: Optional[int] = None,
        duration: Optional[int] = None,
        precision_mode: bool = False,
        non_linear: bool = False,
    ) -> None:
        self.players: PlayerList = players
        self.scores: defaultdict[Player, float] = defaultdict(float)
        self.messages: defaultdict[Player, str] = defaultdict(str)
        self.distances: defaultdict[Player, float] = defaultdict(float)
        self.durations: defaultdict[Player, float] = defaultdict(float)
        self.records: list[Record] = []

        self.time_param: int = 5 if time_param is None else time_param
        self.dist_param: int = 500 if dist_param is None else dist_param
        self.duration: int = 10 if duration is None else duration
        self.precision_mode = precision_mode

        self.place = place
        self.start: Optional[float] = None
        self.dones: defaultdict[Player, bool] = defaultdict(lambda: False)
        self.callback: Optional[Callback] = None
        self.non_linear = non_linear

    def display(self) -> str:
        (city, hint), _ = self.place
        if hint:
            return f"{city} ({hint})"
        return city

    def launch(self, callback: Optional[Callback] = None) -> str:
        self.on_run_start(callback)
        return self.display()

    def time_score(self, delta: float) -> float:
        if self.precision_mode:
            return 0
        return max(0, 1 - (delta / self.time_param))

    def non_linear_bonus(self, dist: float) -> float:
        # Max bonus as a fraction of the score multiplier (so +200 bonus for a 0km
        # distance with the standard 1000km)
        t = 0.2 * self.SCORE_MULTIPLIER
        # Last n kilometers for the non-linear bonus
        g = 0.2 * self.dist_param
        return (t / g**2) * max(0, g - dist) ** 2

    def dist_score(self, dist: float, non_linear: Optional[bool] = None) -> float:
        s = self.SCORE_MULTIPLIER * max(0, 1 - (dist / self.dist_param))
        if (non_linear is True) or self.non_linear:
            return s + self.non_linear_bonus(dist)
        return s

    @property
    def results(self) -> RunResults:
        return dict(
            scores=self.scores,
            messages=self.messages,
            distances=self.distances,
            durations=self.durations,
        )

    def on_run_start(self, callback: Optional[Callback] = None) -> None:
        print("\ngame.on_run_start()\n")
        self.start = time.time()
        self.callback = callback

    def on_run_end(self) -> Point:
        print(f"Game done, right answer was: {self.place[1]}")
        return self.place[1]

    def get_params(self) -> GameRunParams:
        """So you can re-create a new GameRun with
        game2 = GameRun(**game1.get_params())"""
        return dict(
            players=set(self.players),
            dist_param=self.dist_param,
            time_param=self.time_param,
            duration=self.duration,
        )

    def process_answer(
        self, guess: CoordinatesTuple, player: Player
    ) -> tuple[Record, bool]:
        if player not in self.players:
            raise KeyError(f"Unknown player: '{player}'")
        if self.start is None:
            raise ValueError(
                f"Can't process answer for player {player} until the game starts."
            )

        (main_name, hint), ref = self.place
        delta = time.time() - self.start
        dist = distance(ref, guess)

        sd = self.dist_score(dist)
        st = sd * self.time_score(delta)

        score = round(st + sd)
        msg = MSG_TEMPLATE.format(dist=dist, delta=delta, st=st, sd=sd, score=score)

        self.distances[player] = dist
        self.durations[player] = delta
        self.scores[player] = score
        self.messages[player] = msg

        res = Record(
            dist=dist,
            delta=delta,
            score=score,
            msg=msg,
            guess=Coordinates(lon=guess[0], lat=guess[1]),
            answer=Answer(lon=ref[0], lat=ref[1], name=main_name),
            player=player,
            st=st,
            sd=sd,
        )
        self.records.append(res)
        self.dones[player] = True

        game_done = all(self.dones[p] for p in self.players)
        if game_done:
            self.on_run_end()
        return res, game_done
