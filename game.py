import random
import time
import pandas as pd

from collections import defaultdict, Counter
from geo import Point
import geo


def load_cities(fname="data/world_filtered.csv", min_pop=0):
    def clean_city(city):
        if city.isupper():
            return city[0] + city[1:].lower()
        return city
    df = pd.read_csv(fname)
    if "country" not in df.columns:
        df["country"] = ""
    if "dept" in df.columns:
        idf = {"75", "91", "92", "93", "94"}
        is_idf = df.dept.isin(idf)
        mask = (~is_idf & (df.population > min_pop)) | (is_idf & (df.population > 3 * min_pop))
        df = df[mask]
    else:
        df = df[df.population > min_pop]
    return {((clean_city(city), country), Point(lon, lat)) for city, country, lon, lat in zip(df.name, df.country, df.lon, df.lat)}

CITIES = load_cities()

OLD_CITIES = {
    (("Paris", "France"), Point(2.3488, 48.8534)),
    (("Lyon", "France"), Point(4.85, 45.75))
}

MSG_TEMPLATE = """Distance: {dist:.1f}km (+{sd:.0f} pts)
Time: {delta:.2f}s (+{st:.0f} pts)

Score: +{score} pts
"""

class PlayerList:
    def __init__(self):
        self.players = ["charles", "georges", "valery", "francois", "jacques", "nicolas", "hollandouille", "emmanuel"]
        self.currents = Counter()

    def new(self):
        player = random.choice(self.players)
        self.currents[player] += 1
        return f"{player}_{self.currents[player]}"

def generate_id():
    return random.randint(1, 1000)

def random_city(forbidden=None):
    if forbidden is None:
        forbidden = set()
    city, loc = random.choice(list(CITIES - forbidden))
    return city, loc

class GameRun:
    SCORE_MULTIPLIER = 1000

    def __init__(self, players, place=None, forbidden=None, dist_param=None, time_param=None, duration=None):
        self.players = players
        self.scores =  defaultdict(float)
        self.messages = defaultdict(str)
        self.distances = defaultdict(float)
        self.durations = defaultdict(float)
        self.records = []


        self.time_param = 5 if time_param is None else time_param
        self.dist_param = 500 if dist_param is None else dist_param
        self.duration = 10 if duration is None else duration

        if place is None:
            place = random_city(forbidden)
        self.place = place
        self.start = None
        self.dones = defaultdict(lambda:False)
        self.callback = None

    def display(self):
        (city, hint), _ = self.place
        if hint:
            return f"{city} ({hint})"
        return city

    def launch(self, callback=None):
        self.on_run_start(callback)
        return self.display()

    def time_score(self, delta):
        return max(0, 1 - (delta / self.time_param))

    def dist_score(self, dist):
        return self.SCORE_MULTIPLIER * max(0, 1 - (dist / self.dist_param))

    @property
    def results(self):
        return dict(scores=self.scores, messages=self.messages, distances=self.distances, durations=self.durations)

    def on_run_start(self, callback=None):
        print("\ngame.on_run_start()\n")
        self.start = time.time()
        self.callback = callback

    def on_run_end(self):
        print(f"Game done, right answer was: {self.place[1]}")
        return self.place[1]

    def get_params(self):
        """So you can re-create a new GameRun with game2 = GameRun(**game1.get_params())"""
        return dict(
            players=set(self.players),
            dist_param=self.dist_param,
            time_param=self.time_param,
            duration=self.duration
        )

    def process_answer(self, guess, player):
        if player not in self.players:
            raise KeyError(f"Unknown player: '{player}'")

        refname, ref = self.place
        delta = time.time() - self.start
        dist = geo.distance(ref, guess)

        sd = self.dist_score(dist)
        st = sd * self.time_score(delta)

        score = round(st + sd)
        msg = MSG_TEMPLATE.format(dist=dist, delta=delta, st=st, sd=sd, score=score)

        self.distances[player] = dist
        self.durations[player] = delta
        self.scores[player] = score
        self.messages[player] = msg

        res = dict(dist=dist, delta=delta, score=score, msg=msg,
                   guess=dict(lon=guess[0], lat=guess[1]),
                   answer=dict(lon=ref[0], lat=ref[1], name=refname),
                   player=player, st=st, sd=sd
                   )
        self.records.append(res)
        self.dones[player] = True

        game_done = all(self.dones[p] for p in self.players)
        if game_done:
            self.on_run_end()
        return res, game_done


