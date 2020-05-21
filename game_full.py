import random
from collections import defaultdict, Counter

import pandas as pd

from game import GameRun, load_cities
from city_parser import GameMap, SPECIALS, COUNTRIES
from datetime import datetime, timedelta

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

def choose_depts(df, max_per_country=10, min_pop=15):
    data = df.to_dict("records")
    countries = Counter()
    cities = []
    for row in sorted(data, key=lambda p:-p["population"]):
        country = row["dept"]
        if country not in countries or (min_pop < row["population"] and countries[country] < max_per_country):
            countries[country] += 1
            cities.append({k: row[k] for k in ["name", "dept", "lat", "lon", "population"]})
    return pd.DataFrame(cities)


available_names = set(NAMES)
global_player_list = set()

def get_all_datasets():
    data = []
    for map_id, special in SPECIALS.items():
        data.append(dict(
            name=map_id,
            display=special["name"],
            points=[]
        ))
    data.append(dict(is_sep=True))
    for map_id, special in COUNTRIES.items():
        data.append(dict(
            name=map_id,
            display=special["name"],
            points=[]
        ))
    return data
   # data = []
   # for name, dataset in MAPS.items():
   #     data.append(dict(
   #         name=name,
   #         points=[[lat, lon] for _, (lon, lat) in get_cities(dataset)],
   #     ))
   # return data

def get_cities(map):
    return load_cities(map["fname"], map["min-pop"])

class Game:
    def __init__(self, players=None, n_run=20, time_param=5, dist_param=None,
                 difficulty=1, is_public=False, creation_date=None,
                 duration=10, wait_time=8, map="world", pseudos=None, **kwargs):
        self.map_name = map
        map = GameMap.from_name(self.map_name)
        self.map_display_name = map.name
        if dist_param is None:
            dist_param = map.get_distance()
        self.bbox = map.bounding_box()
        # self.map_info = map
        self.difficulty = difficulty
        self.n_run = n_run
        self.dist_param = dist_param
        self.time_param = time_param
        self.__curr_run_id = 0
        if players is None:
            players = set()
        self.players = set(players)
        self.places = map.sample(self.n_run, self.difficulty) # random.sample(get_cities(map), self.n_run)
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
        self.is_public = is_public
        if pseudos is None:
            pseudos = dict()
        pseudos = {k: v for k, v in pseudos.items() if k in self.players}
        self.done = False
        self.pseudos = pseudos

        if creation_date is None:
            creation_date = datetime.now()
        self.date_created = creation_date
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
            # map_display=self.map_display_name,
            pseudos=self.pseudos,
            wait_time=self.wait_time,
            difficulty=self.difficulty,
            is_public=self.is_public,
            creation_date=self.date_created
        )



    @property
    def curr_run_id(self):
        return self.__curr_run_id

    @curr_run_id.setter
    def curr_run_id(self, value):
        if value >= len(self.runs):
            value = len(self.runs) - 1
            self.done = True
        self.__curr_run_id = value

    def __str__(self):
        return f"""---
Multigeo {'Public' if self.is_public else 'Private'} Game
Map: {self.map_display_name}
Difficulty: {100.*self.difficulty:.0f}%
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
        # if self.done:
        #     return self.runs[-1]
        return self.runs[self.curr_run_id]

    def launch(self):
        self.launched = True
        return self.current #.launch()

    def is_expired(self, hours=6):
        """Kwargs must be valid arguments for timedelta"""
        expiration_date = self.date_created + timedelta(seconds=3600*hours)
        return len(self.players) == 0 and expiration_date < datetime.now()

    @property
    def old_done(self):
        return self.curr_run_id >= self.n_run

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
