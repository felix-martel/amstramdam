from amstramdam import app, socketio, manager
from flask import session
from flask_socketio import emit

def is_valid_pseudo(name):
    # TODO: implement checks?
    return True


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
    emit("new-name", dict(change=dict(player=player, pseudo=pseudo), pseudos=game.pseudos),
         room=game_name, broadcast=True, json=True)

