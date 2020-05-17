import random
from collections import defaultdict, Counter

import pandas as pd

from game import GameRun, CITIES

with open("data/other_names.txt", "r") as f:
    NAMES = {line.rstrip() for line in f}

def choose_countries(df, max_per_country=10, max_rank=1000):
    countries = Counter()
    cities = []
    for i, row in df.iterrows():
        country = row["country"]
        if country not in countries or (i < max_rank and countries[country] < max_per_country):
            countries[country] += 1
            cities.append({k: row[k] for k in ["name", "country", "lat", "lon", "population"]})
    return pd.DataFrame(cities)




class Game:
    def __init__(self, players=None, n_run=20):
        self.n_run = n_run
        self.curr_run_id = 0
        if players is None:
            players = set()
        self.players = set(players)
        self.places = random.sample(CITIES, self.n_run)
        self.runs = [GameRun(self.players, place) for place in self.places]
        names = list(NAMES - self.players)
        random.shuffle(names)
        self.available_names = set(names)
        self.records = [] # defaultdict(list)
        self.scores = defaultdict(int)

        self.launched = False
        # self.run_in_progress = False

    def __str__(self):
        return f"""---
        Multigeo Game
        Players: {', '.join(self.players)}
        Places: {', '.join([p[0][0] for p in self.places])}
        Run: {self.curr_run_id+1}/{self.n_run}
        ---"""

    def add_player(self, name=None):
        if name is not None:
            assert name not in self.players, f"Name '{name}' already exists"
            if name in self.available_names:
                self.available_names.remove(name)
        else:
            name = self.available_names.pop()
        self.players.add(name)
        return name

    def remove_player(self, name):
        if name not in self.players:
            return
        if name in NAMES:
            self.available_names.add(name)
        self.players.remove(name)
        if name in self.records:
            del self.records[name]
        if name in self.scores:
            del self.scores[name]

    @property
    def current(self):
        if self.done:
            return self.runs[-1]
        return self.runs[self.curr_run_id]

    def launch(self):
        self.launched = True
        return self.current #.launch()

    @property
    def done(self):
        return self.curr_run_id == self.n_run

    def on_game_end(self):
        print("Game ended!")

    def get_final_results(self):
        return dict(records=self.records, scores=self.scores, places=self.places)

    def end(self):
        rec = self.current.records
        self.records.append(rec)
        for player in self.players:
            self.scores[player] += self.current.scores[player]
        self.curr_run_id += 1
        if self.done:
            self.on_game_end()
            results = self.get_final_results()
            return results, self.done
        #self.current_run.launch()
        return self.current, self.done

    @property
    def n_players(self):
        return len(self.players)

    def get_current_leaderboard(self):
        """Players with their scores, ranked by decreasing scores"""
        return list(sorted([dict(player=player, score=self.scores[player]) for player in self.players],
                           key=lambda t:-t["score"]))
