from collections import Counter

from game_full import Game
import random
from unidecode import unidecode

with open("data/filtered_ancient_places.txt", "r", encoding="utf8") as f:
    VALID_GAME_NAMES = {unidecode(line.rstrip()) for line in f}


disambig = Counter()
MANAGER = dict()

def create_game(*args, **kwargs):
    names = list(VALID_GAME_NAMES - MANAGER.keys())
    if names:
        name = random.choice(names)
    else:
        name = random.choice(list(VALID_GAME_NAMES))
        disambig[name] += 1
        name = f"{name}_{disambig[name]}"

    assert name not in MANAGER
    MANAGER[name] = Game(*args, **kwargs)

    return name, MANAGER[name]

def remove_game(name):
    del MANAGER[name]

def get_game(name):
    return MANAGER.get(name, None)

def relaunch_game(name, **kwargs):
    old_game = MANAGER[name]
    params = {**old_game.get_params(), **kwargs}
    MANAGER[name] = Game(**params)
    return MANAGER[name]

def exists(name):
    return name in MANAGER

def get_all_games():
    return list(MANAGER.keys())

def get_status():
    s = ""
    for game_id, (name, game) in enumerate(MANAGER.items()):
        s += f"\nGame {game_id+1}/{len(MANAGER)}: {name}\n" + str(game)
    return s