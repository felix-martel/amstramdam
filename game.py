import math
import random
import time
import pandas as pd
import threading

from collections import defaultdict, Counter
from geo import Point
import geo


def load_cities(fname="data/france_clean.csv", min_pop=25):
    df = pd.read_csv(fname)
    df = df[df.population > min_pop]
    return {((city, ""), Point(lon, lat)) for city, lon, lat in zip(df.name, df.lon, df.lat)}

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
    TIME_PARAMS = (2, 2)
    DIST_PARAMS = 500 # (2, 2)
    DURATION = 6

    def __init__(self, players, place=None, forbidden=None):
        self.players = set(players)
        self.scores =  defaultdict(float)
        self.messages = defaultdict(str)
        self.distances = defaultdict(float)
        self.durations = defaultdict(float)
        self.records = []

        if place is None:
            place = random_city(forbidden)
        self.place = place
        self.start = None
        self.dones = defaultdict(lambda:False)
        self.callback = None

    def add_player(self, player):
        self.players.add(player)

    def display(self):
        (city, hint), _ = self.place
        if hint:
            return f"{city} ({hint})"
        return city

    def launch(self, callback=None):
        self.on_run_start(callback)
        return self.display()

    @classmethod
    def time_score(cls, delta):
        return max(0, 1 - (delta / cls.DURATION))
        # a, b = cls.TIME_PARAMS
        # return cls.SCORE_MULTIPLIER * math.pi / 2 - math.atan((delta - a) / b)

    @classmethod
    def dist_score(cls, dist):
        return cls.SCORE_MULTIPLIER * max(0, 1 - (dist / cls.DIST_PARAMS))
        # a, b = cls.DIST_PARAMS
        # return cls.SCORE_MULTIPLIER * math.pi / 2 - math.atan((dist - a) / b)

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


class Game:
    def __init__(self, players, places=None):
        self.players = players
        self.id_ = generate_id()
        if places is None:
            self.places = random.shuffle(CITIES)


