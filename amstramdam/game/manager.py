from collections import Counter

from .game import Game
import random
from typing import Any, Optional, Generator
from unidecode import unidecode
from amstramdam.game.types import GameName, AvailableGames
from amstramdam import utils
from .params import GameParams, GameMetadata
from ..settings import settings

with open("data/game_names.txt", "r", encoding="utf8", errors="ignore") as f:
    VALID_GAME_NAMES = {GameName(unidecode(line.rstrip())) for line in f}


disambig: Counter[GameName] = Counter()
MANAGER: dict[GameName, Game] = dict()


def create_game(
    dataset_name: str,
    level: int = 0,
    is_public: bool = True,
    precision_mode: bool = False,
    wait_duration: int = settings.game.wait_duration,
    force_name: str | None = None,
    **kwargs: Any,
) -> tuple[GameName, Game]:
    name = _assign_name(name=force_name, is_public=is_public)
    assert name not in MANAGER
    params = GameParams(
        dataset_name=dataset_name,
        level=level,
        is_public=is_public,
        precision_mode=precision_mode,
        wait_duration=wait_duration,
        **kwargs,
    )
    metadata = GameMetadata(name=name)
    MANAGER[name] = Game(metadata=metadata, params=params)
    return name, MANAGER[name]


def _assign_name(name: str, is_public: bool = True) -> GameName:
    if name is not None:
        name = GameName(name)
        if name in MANAGER:
            disambig[name] += 1
            name = GameName(f"{name}_{disambig[name]}")
        return name
    elif not is_public:
        return GameName(utils.random.generate_random_identifier(12))
    elif names := VALID_GAME_NAMES - MANAGER.keys():
        return random.choice(list(names))
    else:
        name = random.choice(list(VALID_GAME_NAMES))
        disambig[name] += 1
        return GameName(f"{name}_{disambig[name]}")


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
    #  The 'if' clause is a dirty fix for the case 'route to /game/xxx then socketio
    #  fails'
    return [
        dict(
            name=name,
            map=game.map_display_name,
            players=len(game.players),
            difficulty=game.params.level,
        )
        for name, game in iter_games()
        if game.params.is_public and (len(game.players) > 0 or game.params.is_permanent)
    ]


def relaunch_game(name: GameName) -> Game:
    old_game = MANAGER[name]
    MANAGER[name] = old_game.clone()  # type: ignore
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
