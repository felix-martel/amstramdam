import random
from collections import defaultdict

from game import GameRun, CITIES

with open("data/other_names.txt", "r") as f:
    NAMES = {line.rstrip() for line in f}

class Game:
    def __init__(self, players=None, n_run=20):
        self.n_run = n_run
        self.curr_run_id = 0
        self.players = set(players) if players is not None else set()
        self.places = random.sample(CITIES, self.n_run)
        self.runs = [GameRun(self.players, place) for place in self.places]
        self.available_names = set(random.shuffle(list(NAMES - self.players)))
        self.records = [] # defaultdict(list)
        self.scores = defaultdict(int)

        self.launched = False
        self.run_in_progress = False

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
        self.available_names.add(name)
        self.players.remove(name)
        if name in self.records:
            del self.records[name]
        if name in self.scores:
            del self.scores[name]

    @property
    def current_run(self):
        return self.runs[self.curr_run_id]

    def launch(self):
        return self.current_run #.launch()

    @property
    def done(self):
        return self.curr_run_id == self.n_run

    def on_game_end(self):
        print("Game ended!")

    def get_final_results(self):
        return dict(records=self.records, scores=self.scores, places=self.places)

    def next(self):
        rec = self.current_run.records
        self.records.append(rec)
        self.curr_run_id += 1
        if self.done:
            self.on_game_end()
            results = self.get_final_results()
            return results, self.done
        #self.current_run.launch()
        return self.current_run, self.done

    @property
    def n_players(self):
        return len(self.players)

    def get_current_leaderboard(self):
        """Players with their scores, ranked by decreasing scores"""
        return sorted([(player, self.scores[player]) for player in self.players], key=lambda t:-t[1])
