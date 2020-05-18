import random
from collections import defaultdict, Counter

import pandas as pd

from game import GameRun, CITIES, load_cities

with open("data/player_names.txt", "r", encoding="utf8", errors="ignore") as f:
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

available_names = set(NAMES)
global_player_list = set()

MAPS = {
    "world": {
        "fname": "data/places.world.csv",
        "min-pop": 0,
        "distance": 1500,
        "time-bonus": 6,
    },
    "france": {
        "fname": "data/places.france.csv",
        "min-pop": 25,
        "distance": 300,
        "time-bonus": 5,
    },
    "default": {
        "min-pop": 0,
        "distance": 500,
        "time-bonus": 5
    }
}


def get_cities(map):
    return load_cities(map["fname"], map["min-pop"])

class Game:
    def __init__(self, players=None, n_run=20, time_param=None, dist_param=None, duration=None, wait_time=8, map="world", pseudos=None):
        self.map_name = map
        map = MAPS[self.map_name]
        if dist_param is None:
            dist_param = map["distance"]
        if time_param is None:
            time_param = map["time-bonus"]
        if duration is None:
            duration = 10
        self.map_info = map
        self.n_run = n_run
        self.dist_param = dist_param
        self.time_param = time_param
        self.curr_run_id = 0
        if players is None:
            players = set()
        self.players = set(players)
        self.places = random.sample(get_cities(map), self.n_run)
        self.duration = duration
        self.runs = [GameRun(self.players, place, dist_param=self.dist_param, time_param=self.time_param, duration=duration)
                     for place in self.places]
        names = list(NAMES - self.players)
        random.shuffle(names)
        self.global_player_list = global_player_list
        self.available_names = available_names # set(names)
        self.wait_time = wait_time
        self.records = [] # defaultdict(list)
        self.scores = defaultdict(int)
        if pseudos is None:
            pseudos = dict()
        pseudos = {k: v for k, v in pseudos.items() if k in self.players}
        self.pseudos = pseudos

        self.launched = False
        # self.run_in_progress = False

    def get_params(self):
        return dict(
            players=set(self.players),
            n_run=self.n_run,
            time_param=self.time_param,
            dist_param=self.dist_param,
            duration=self.duration,
            map=self.map_name,
            pseudos=self.pseudos,
            wait_time=self.wait_time
        )

    def __str__(self):
        return f"""---
Multigeo Game
Players: {', '.join(self.players)}
Places: {', '.join([p[0][0] for p in self.places])}
Run: {self.curr_run_id+1}/{self.n_run}
---"""

    def add_player(self, name=None):
        if name is not None:
            assert name not in self.global_player_list, f"Name '{name}' already exists"
            # assert name not in self.players, f"Name '{name}' already exists"
            if name in self.available_names:
                self.available_names.remove(name)
        else:
            name = self.available_names.pop()
        self.players.add(name)
        self.global_player_list.add(name)
        return name

    def add_pseudo(self, name, pseudo):
        if name not in self.players:
            print(f"Ignored unknown player '{name}'")
        self.pseudos[name] = pseudo

    def remove_pseudo(self, name):
        if name in self.pseudos:
            del self.pseudos[name]

    def get_pseudo(self, name):
        return self.pseudos.get(name, name)

    def remove_player(self, name):
        if name in self.global_player_list:
            self.global_player_list.remove(name)

        if name not in self.players:
            return
        if name in NAMES:
            self.available_names.add(name)
        self.players.remove(name)
        self.remove_pseudo(name)
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
