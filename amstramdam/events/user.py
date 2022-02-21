from typing import Optional

from amstramdam import socketio, manager
from flask import session, url_for
from flask_socketio import emit

from amstramdam.events.types import (
    ChatMessage,
    NameChangePayload,
    NewNameNotification,
    PartialGameParams,
    GameChangeNotification,
)
from amstramdam.game.params_handler import merge_params
from amstramdam.game.types import GameName, Pseudo, Player

MAX_LEN = 20


def is_valid_pseudo(name: str) -> bool:
    # TODO: implement checks?
    name = str(name)
    return len(name) > 0


def process_pseudo(name: str) -> Pseudo:
    if len(name) > MAX_LEN + 3:
        name = name[:MAX_LEN] + "..."
    return Pseudo(name)


@socketio.on("chat:send")
def process_chat_message(message: str) -> None:
    game_name: Optional[GameName] = session.get("game")
    author: Optional[Player] = session.get("player")
    if author is None or game_name is None:
        return
    emit(
        "chat:new",
        ChatMessage(author=author, message=message),
        json=True,
        broadcast=True,
        room=game_name,
    )


@socketio.on("name-change")
def update_nickname(data: NameChangePayload) -> None:
    game_name: GameName = session["game"]
    player: Optional[Player] = session.get("player")
    game = manager.get_game(game_name)
    if player is None or game is None:
        return

    nickname = data["name"]
    if is_valid_pseudo(nickname):
        nickname = process_pseudo(nickname)
        game.players.add_nickname(player, nickname)
    else:
        nickname = game.players.request_nickname(player)
    emit(
        "new-name",
        NewNameNotification(player=player, pseudo=nickname),
        room=game_name,
        broadcast=True,
        json=True,
    )


@socketio.on("request-game-change")
def change_game(data: PartialGameParams) -> None:
    game_name = session["game"]
    player = session.get("player")
    if player is None:
        return

    params = merge_params(data)
    print(*[f"{k}={v}" for k, v in params.items()], sep=", ")
    new_game_name, game = manager.create_game(
        n_run=params["runs"],
        duration=params["duration"],
        difficulty=params["difficulty"],
        is_public=params["public"],
        precision_mode=params["precision_mode"],
        allow_zoom=params["zoom"],
        map=params["map"],
        wait_time=params["wait_time"],
    )
    url = url_for("serve_game", name=new_game_name)
    print(url)
    print(manager.get_status())

    emit(
        "game-change",
        GameChangeNotification(
            name=new_game_name, url=url, map_name=params["map"], player=player
        ),
        room=game_name,
        broadcast=True,
        json=True,
    )
