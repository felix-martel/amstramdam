"""
Associated with conda env 'tdc'
"""
import threading
import atexit
from collections import defaultdict

from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room, close_room


from game import GameRun, PlayerList
from game_full import Game
import game_manager as manager

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x93\xd6j63\xffoP\x1c\xa8\x82\xca\x92\xfd\xf9\xc8'
socketio = SocketIO(app) # For some reason, eventlet causes bugs (maybe because I use threading.Timer for callbcks




@app.route("/")
def serve_main():
    return render_template("lobby.html")
    #return render_template("main.html")

@app.route("/new", methods=["GET", "POST"])
def create_new_game():
    params = {
        "map": "world",
        "duration": "10",
        "zoom": False,
        "runs": 10,
        "wait_time": 10,
        **request.form
    }
    ints = ["duration", "runs", "wait_time"]
    for k in ints:
        params[k] = int(params[k])
    name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     map=params["map"], wait_time=params["wait_time"])
    print(manager.get_status())

    return redirect(url_for("serve_game", name=name))

@app.route("/game/<name>")
def serve_game(name):
    if not manager.exists(name):
        return redirect(url_for("serve_main"))
    else:
        session["game"] = name
        game_name = session["game"]
        game = manager.get_game(game_name)
        params = dict(map=game.map_name, wait_time=game.wait_time, duration=game.duration)
        return render_template("main.html", game_name=name, params=params)



timers = defaultdict(int)


@socketio.on('connection')
def init_game(data):
    game_name = session["game"]
    if not manager.exists(game_name):
        del session["game"]
        return redirect(url_for("serve_main"))

    join_room(game_name)
    game = manager.get_game(game_name)
    if "player" in session:
        player = session["player"]
        if player not in game.players:
            game.add_player(player)
    else:
        player = game.add_player()
        session["player"] = player

    print(f"Player <{player}> connected to game <{game_name}>", end=" ")
    emit("init", dict(player=player, launched=game.launched))
    emit("new-player", dict(player=player, leaderboard=game.get_current_leaderboard(), pseudos=game.pseudos), broadcast=True, room=game_name)

def safe_cancel(timer):
    if not timer:
        return
    try:
        timer.cancel()
    except AttributeError:
        pass

@socketio.on('disconnect')
def remove_from_game():
    if "player" not in session:
        return
    player = session["player"]
    game_name = session["game"]
    game = manager.get_game(game_name)
    game.remove_player(player)
    leave_room(game_name)
    emit("player-left", dict(player=player, leaderboard=game.get_current_leaderboard()), broadcast=True, room=game_name)

    print(f"<{player}> disconnected!")

    if not game.players:
        manager.remove_game(game_name)
        close_room(game_name)
        safe_cancel(timers[game_name])
        del timers[game_name]
        print(f"Game <{game_name}> was removed!")


def game_ender(game_name):
    def ender():
        return end_game(game_name)
    return ender

def terminate_game(game_name):
    game = manager.get_game(game_name)
    if game is None or not game.done:
        return
    socketio.emit("game-end",
                  dict(leaderboard=game.get_current_leaderboard()), json=True, broadcast=True,
                  room=game_name)

    # game = Game(players=set(game.players), n_run=N_RUNS, map=game.map_name)
    manager.relaunch_game(game_name)

def end_game(game_name, run_id):
    # global game
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id:
        print(f"end_game failed (current: {game.curr_run_id}, expected: {run_id})")
        return
    print(f"\n--\nEnding run {game.curr_run_id+1}\n--\n")
    with app.test_request_context('/'):
        # 1: get current place
        refname, (lon, lat) = game.current.place
        answer = dict(name=refname, lon=lon, lat=lat)

        # 2: end game
        records = game.current.records
        results, done = game.end()
        socketio.emit("run-end",
                      dict(results=records, answer=answer, leaderboard=game.get_current_leaderboard()),
                        json=True, broadcast=True, room=game_name
                      )

        # 3: continue?
        if done:
            #
            timers[game_name] = wait_and_run(game.wait_time, terminate_game, game_name)
            # timers[game_name] = threading.Timer(game.wait_time, terminate_game, [game_name])  # run_launcher(game_name))
            # timers[game_name].start()
        else:
            timers[game_name] = wait_and_run(game.wait_time, launch_run, game_name, game.curr_run_id)
            # timers[game_name] = threading.Timer(game.wait_time, launch_run, [game_name, game.curr_run_id]) # run_launcher(game_name))
            # timers[game_name].start()


def wait_and_run(seconds, func, *args, **kwargs):
    def waiter():
        socketio.sleep(seconds)
        func(*args, **kwargs)
    socketio.start_background_task(waiter)

def launch_run(game_name, run_id):
    # global duration_thread
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id:
        return
    print(f"\n--\nLaunching run {game.curr_run_id+1} for game <{game_name}>\n--\n")
    with app.test_request_context('/'):
        hint = game.current.launch()

        print(f"Hint is '{hint}'")
        print(f"Broadcasting <event:run-start> to <room:{game_name}>")
        socketio.emit("log", "Run launched [from line 164]", broadcast=True, room=game_name)
        socketio.emit("run-start",
                      dict(hint=hint, current=game.curr_run_id, total=game.n_run),
                      json=True,
                      room=game_name,
                      broadcast=True)

        timers[game_name] = wait_and_run(game.current.duration, end_game, game_name, game.curr_run_id)
        # timers[game_name] = threading.Timer(game.current.duration, end_game, [game_name, game.curr_run_id]) # game_ender(game_name))
        # timers[game_name].start()

@socketio.on("launch")
def launch_game():
    game_name = session["game"]
    game = manager.get_game(game_name)
    print(game)
    game.launch() # GameRun(players)
    print(f"Game <{game_name}> created...launching game")
    emit("game-launched", broadcast=True, room=game_name)

    launch_run(game_name, game.curr_run_id)

def is_valid_pseudo(name):
    # TODO: implement checks?
    return True


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

@socketio.on('guess')
def process_guess(data):
    # global duration_thread
    game_name = session["game"]
    game = manager.get_game(game_name)

    print(f"Received answer for game <{game_name}>:", data)
    player = data["player"]
    lon, lat = data["lon"], data["lat"]
    res, done = game.current.process_answer((lon, lat), player)
    emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True, room=game_name)
    emit("new-guess", dict(player=player, dist=res["dist"], delta=res["delta"], score=res["score"]),
         broadcast=True, room=game_name)
    emit("score", res, json=True)
    if done:
        try:
            print(f"\n--\nInterrupting run {game.curr_run_id+1}\n--\n")
            safe_cancel(timers[game_name])
        except AttributeError:
            pass

        end_game(game_name, game.curr_run_id)


DEBUG = False
PROD = True
if __name__ == '__main__':
    if DEBUG:
        # Prevent server from being visible from the outside
        assert not PROD, "Can't have both flags DEBUG and PROD"
        kwargs = dict(debug=True)
    elif PROD:
        kwargs = dict()
    else:
        kwargs = dict(host= '0.0.0.0', port=80)
    socketio.run(app, **kwargs)