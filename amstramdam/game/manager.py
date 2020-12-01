from collections import Counter

from .game_full import Game, get_all_datasets
import random
from unidecode import unidecode

with open("data/game_names.txt", "r", encoding="utf8", errors="ignore") as f:
    VALID_GAME_NAMES = {unidecode(line.rstrip()) for line in f}


disambig = Counter()
MANAGER = dict()

def create_game(*args, force_name=None, **kwargs):
    if force_name is not None:
        name = force_name
        if name in MANAGER:
            disambig[name] += 1
            name = f"{name}_{disambig[name]}"
    else:
        names = list(VALID_GAME_NAMES - MANAGER.keys())
        if names:
            name = random.choice(names)
        else:
            name = random.choice(list(VALID_GAME_NAMES))
            disambig[name] += 1
            name = f"{name}_{disambig[name]}"

    assert name not in MANAGER
    MANAGER[name] = Game(name, *args, **kwargs)

    return name, MANAGER[name]

def remove_game(name):
    del MANAGER[name]

def get_game(name):
    return MANAGER.get(name, None)

def iter_games(purge=True):
    to_purge = set()
    for name, game in MANAGER.items():
        if purge and game.is_expired():
            to_purge.add(name)
        else:
            yield name, game
    for name in to_purge:
        remove_game(name)


def get_public_games():
    return [dict(name=name, map=game.map_display_name, players=len(game.players), difficulty=game.difficulty) for name, game in iter_games()
            if game.is_public and (len(game.players) > 0 or game.is_permanent)] # Dirty fix for the case 'route to /game/xxx then socket io fails'

def relaunch_game(name, **kwargs):
    old_game = MANAGER[name]
    params = {**old_game.get_params(), **kwargs}
    MANAGER[name] = Game(old_game.name, **params)
    return MANAGER[name]

def exists(name):
    return name in MANAGER

def get_all_games(include_expired_games=False):
    purge = not include_expired_games
    return [name for name, game in iter_games(purge)]

def get_status():
    s = ""
    for game_id, (name, game) in enumerate(MANAGER.items()):
        s += f"\nGame {game_id+1}/{len(MANAGER)}: {name}\n" + str(game)
    return s