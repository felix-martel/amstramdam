from amstramdam import socketio, timers, manager
from flask import session, url_for
from flask_socketio import emit, join_room, leave_room, close_room
from .utils import safe_cancel


@socketio.on('connection')
def init_game(data):
    game_name = session["game"]
    player = session.get("player", "unknown")
    print(f"Receive <event:connection[to={game_name}]> from <player:{player}>")
    if not manager.exists(game_name):
        print(f"Game <game:{game_name}> does not exist")
        del session["game"]
        emit("redirect", dict(url=url_for("serve_main")), json=True)
        # return redirect(url_for("serve_main"))

    join_room(game_name)
    game = manager.get_game(game_name)
    if "pseudo" in data and data["pseudo"]:
        pseudo = data["pseudo"]
    else:
        pseudo = None
    if "player" in session:
        player = session["player"]
        print(f"Receive <event:connection> from existing player <player:{player}>")
        if player not in game.players:
            game.add_player(player, pseudo)
    else:
        player, pseudo = game.add_player(pseudo=pseudo)
        session["player"] = player

    print(f"Player <{player}> connected to game <{game_name}> with pseudo <{pseudo}>")
    leaderboard = game.get_current_leaderboard()
    emit("init", dict(player=player, launched=game.launched, pseudo=pseudo,
            game=game.map_name, current=game.curr_run_id, runs=game.n_run, diff=game.difficulty,
                      #precision=game.precision_mode,
                      game_name=game.map_display_name,
                      leaderboard=leaderboard,
                      pseudos=game.pseudos))
    emit("new-player", dict(
        player=player,
        pseudo=pseudo,
        score=game.get_player_score(player)
    ), broadcast=True, room=game_name)




@socketio.on('disconnect')
def leave_game():
    if "player" not in session:
        return
    player = session["player"]
    game_name = session["game"]
    game = manager.get_game(game_name)
    game.remove_player(player)
    leave_room(game_name)
    emit("player-left", dict(player=player), broadcast=True, room=game_name)

    print(f"<{player}> disconnected!")

    if not game.players and not game.is_permanent:
        manager.remove_game(game_name)
        close_room(game_name)
        safe_cancel(timers[game_name])
        del timers[game_name]
        print(f"Game <{game_name}> was removed!")
