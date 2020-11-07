import time
import pandas as pd

from collections import defaultdict
from .geo import Point, distance

def reaccent(name):
    name = name.lower()
    stopwords = {"en", "le", "la", "les", "d", "de", "du", "des", "sur"}
    def capit(s):
        if s.lower() in stopwords:
            return s
        return s[0].upper() + s[1:]
    seps = {" ", "-", "'"}
    for sep in seps:
        name = sep.join([capit(word) for word in name.split(sep)])
    return  capit(name)

def load_cities(fname="data/places.world.csv", min_pop=0):
    def clean_city(city):
        if city.isupper():
            return reaccent(city)
        return city
    df = pd.read_csv(fname)
    if "country" not in df.columns:
        df["country"] = ""
    if "dept" in df.columns:
        idf = {"75", "78", "91", "92", "93", "94", "95"}
        is_idf = df.dept.isin(idf)
        mask = (~is_idf & (df.population > min_pop)) | (is_idf & (df.population > 3 * min_pop))
        df = df[mask]
    else:
        df = df[df.population > min_pop]
    return {((clean_city(city), country), Point(lon, lat)) for city, country, lon, lat in zip(df.name, df.country, df.lon, df.lat)}


MSG_TEMPLATE = """Distance: {dist:.1f}km (+{sd:.0f} pts)
Time: {delta:.2f}s (+{st:.0f} pts)

Score: +{score} pts
"""

class GameRun:
    SCORE_MULTIPLIER = 1000

    def __init__(self, players, place, forbidden=None, dist_param=None, time_param=None, duration=None, non_linear=False):
        self.players = players
        self.scores =  defaultdict(float)
        self.messages = defaultdict(str)
        self.distances = defaultdict(float)
        self.durations = defaultdict(float)
        self.records = []


        self.time_param = 5 if time_param is None else time_param
        self.dist_param = 500 if dist_param is None else dist_param
        self.duration = 10 if duration is None else duration

        self.place = place
        self.start = None
        self.dones = defaultdict(lambda:False)
        self.callback = None
        self.non_linear = non_linear

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

    def non_linear_bonus(self, dist):
        # Max bonus as a fraction of the score multiplier (so +200 bonus for a 0km distance with the standard 1000km)
        t = 0.2 * self.SCORE_MULTIPLIER
        # Last n kilometers for the non-linear bonus
        g = 0.2 * self.dist_param
        return (t / g**2) * max(0, g - dist)**2

    def dist_score(self, dist, non_linear=None):
        s = self.SCORE_MULTIPLIER * max(0, 1 - (dist / self.dist_param))
        if (non_linear == True) or self.non_linear:
            return s + self.non_linear_bonus(dist)
        return s

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

        res = dict(dist=dist, delta=delta, score=score, msg=msg,
                   guess=dict(lon=guess[0], lat=guess[1]),
                   answer=dict(lon=ref[0], lat=ref[1], name=main_name),
                   player=player, st=st, sd=sd,
                   )
        self.records.append(res)
        self.dones[player] = True

        game_done = all(self.dones[p] for p in self.players)
        if game_done:
            self.on_run_end()
        return res, game_done


