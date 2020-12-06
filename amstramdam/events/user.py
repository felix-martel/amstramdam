from amstramdam import app, socketio, manager
from flask import session, url_for
from flask_socketio import emit
from amstramdam.game.params_handler import merge_params


def is_valid_pseudo(name):
    # TODO: implement checks?
    name = str(name)
    return len(name) > 0


@socketio.on("chat:send")
def process_chat_message(message):
    game_name = session.get("game")
    author = session.get("player")
    if author is None or game_name is None:
        return
    emit("chat:new", dict(author=author, message=message), json=True, broadcast=True, room=game_name)


@socketio.on("name-change")
def update_pseudo(data):
    game_name = session["game"]
    player = session.get("player")
    if player is None:
        return
    game = manager.get_game(game_name)
    pseudo = data["name"]
    if is_valid_pseudo(pseudo):
        game.add_pseudo(player, pseudo)
    else:
        pseudo = game.request_pseudo(player)
    emit("new-name", dict(player=player, pseudo=pseudo),
         room=game_name, broadcast=True, json=True)

@socketio.on("request-game-change")
def change_game(data):
    game_name = session["game"]
    player = session.get("player")
    if player is None:
        return

    params = merge_params(data)
    print(*[f"{k}={v}" for k, v in params.items()], sep=", ")
    new_game_name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     difficulty=params["difficulty"],
                                     is_public=params["public"],
                                     allow_zoom=params["zoom"],
                                     map=params["map"], wait_time=params["wait_time"])
    url = url_for("serve_game", name=new_game_name)
    print(url)
    print(manager.get_status())

    emit("game-change", dict(name=new_game_name, url=url, map_name=params["map"], player=player),
         room=game_name, broadcast=True, json=True)

