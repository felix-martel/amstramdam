from collections import Counter

from .game_full import Game
import random
from typing import Any, Optional, Generator
from unidecode import unidecode
from amstramdam.game.types import GameName, AvailableGames

with open("data/game_names.txt", "r", encoding="utf8", errors="ignore") as f:
    VALID_GAME_NAMES = {GameName(unidecode(line.rstrip())) for line in f}


disambig: Counter[GameName] = Counter()
MANAGER: dict[GameName, Game] = dict()


def create_game(
    *args: Any, force_name: Optional[str] = None, **kwargs: Any
) -> tuple[GameName, Game]:
    if force_name is not None:
        name = GameName(force_name)
        if name in MANAGER:
            disambig[name] += 1
            name = GameName(f"{name}_{disambig[name]}")
    else:
        names = list(VALID_GAME_NAMES - MANAGER.keys())
        if names:
            name = random.choice(names)
        else:
            name = random.choice(list(VALID_GAME_NAMES))
            disambig[name] += 1
            name = GameName(f"{name}_{disambig[name]}")

    assert name not in MANAGER
    MANAGER[name] = Game(name, *args, **kwargs)

    return name, MANAGER[name]


def remove_game(name: GameName) -> None:
    del MANAGER[name]


def get_game(name: GameName) -> Optional[Game]:
    return MANAGER.get(name, None)


def iter_games(purge: bool = True) -> Generator[tuple[GameName, Game], None, None]:
    to_purge = set()
    for name, game in MANAGER.items():
        if purge and game.is_expired():
            to_purge.add(name)
        else:
            yield name, game
    for name in to_purge:
        remove_game(name)


def get_public_games() -> list[AvailableGames]:
    #  The 'if' clause is a dirty fix for the case 'route to /game/xxx then socket io fails'
    return [
        dict(
            name=name,
            map=game.map_display_name,
            players=len(game.players),
            difficulty=game.difficulty,
        )
        for name, game in iter_games()
        if game.is_public and (len(game.players) > 0 or game.is_permanent)
    ]


def relaunch_game(name: GameName, **kwargs: Any) -> Game:
    old_game = MANAGER[name]
    params = {**old_game.get_params(), **kwargs}
    MANAGER[name] = Game(old_game.name, **params)  # type: ignore
    return MANAGER[name]


def exists(name: GameName) -> bool:
    return name in MANAGER


def get_all_games(include_expired_games: bool = False) -> list[GameName]:
    purge = not include_expired_games
    return [name for name, game in iter_games(purge)]


def get_status() -> str:
    s = ""
    for game_id, (name, game) in enumerate(MANAGER.items()):
        s += f"\nGame {game_id+1}/{len(MANAGER)}: {name}\n" + str(game)
    return s
