"""
Associated with conda env 'tdc'
# TODO add a 'Connect' button when connection is not automatic
# Add support for other countries/regions
# Add a chatc
# Use FA: <script src="https://kit.fontawesome.com/0b60c47224.js" crossorigin="anonymous"></script>
"""

import os
from collections import defaultdict
import argparse

from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
from flask_talisman import Talisman

from city_parser import GameMap, MAPS
import game_manager as manager
from security import csp

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="Use local server with debugger", action="store_true")
parser.add_argument("-t", "--threading", help="Use threading lib instead of eventlet", action="store_true")
args = parser.parse_args()
DEBUG = args.debug
async_mode = "threading" if args.threading else "eventlet"
print(f"Launching app with args debug={DEBUG}, async={async_mode}")


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECURE_KEY", "dummy_secure_key_for_local_debugging").split(",")[0]


Talisman(app, content_security_policy=csp,
    content_security_policy_nonce_in=['default-src'], force_https=True)

socketio = SocketIO(app, async_mode=async_mode)

DATASETS = manager.get_all_datasets()
DATASET_GEOMETRIES = dict()

@app.route("/")
def serve_main():
    return render_template("lobby.html", datasets=DATASETS, games=manager.get_public_games())


@app.route("/points/<dataset>")
def get_dataset_geometry(dataset):
    if dataset not in MAPS:
        data = {}
    else:
        data = GameMap.from_name(dataset).get_geometry()
    return jsonify(data)

@app.route("/new", methods=["GET", "POST"])
def create_new_game():
    params = {
        "map": "world",
        "duration": "10",
        "zoom": False,
        "runs": 10,
        "wait_time": 10,
        "difficulty": 100,
        "public": False,
        **request.form
    }
    ints = ["duration", "runs", "wait_time", "difficulty"]
    for k in ints:
        params[k] = int(params[k])
    params["public"] = bool(params["public"])
    params["difficulty"] /= 100
    name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     difficulty=params["difficulty"],
                                     is_public=params["public"],
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
        params = dict(
            map=game.map_name,
            wait_time=game.wait_time,
            bbox=game.bbox,
            duration=game.duration)
        return render_template("main.html", game_name=name, params=params)



timers = defaultdict(int)


@socketio.on('connection')
def init_game(data):
    game_name = session["game"]
    player = session.get("player", "unknown")
    print(f"Receive <event:connection[to={game_name}> from <player:{player}>")
    if not manager.exists(game_name):
        print(f"Game <game:{game_name}> doesnt exist")
        del session["game"]
        emit("redirect", dict(url=url_for("serve_main")), json=True)
        # return redirect(url_for("serve_main"))

    join_room(game_name)
    game = manager.get_game(game_name)
    if "player" in session:
        player = session["player"]
        print(f"Receive <event:connection> from existing player <player:{player}>")
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
        return
    print(f"\n--\nEnding run {game.curr_run_id+1}\n--\n")
    with app.test_request_context('/'):
        # 1: get current place
        (city_name, hint), (lon, lat) = game.current.place
        answer = dict(name=city_name, lon=lon, lat=lat)

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
    print(f"--\nLaunching run {game.curr_run_id+1} for game <{game_name}>\n--")
    with app.test_request_context('/'):
        hint = game.current.launch()

        print(f"Hint is '{hint}'")
        socketio.emit("run-start",
                      dict(hint=hint, current=game.curr_run_id, total=game.n_run),
                      json=True,
                      room=game_name,
                      broadcast=True)

        timers[game_name] = wait_and_run(game.current.duration, end_game, game_name, game.curr_run_id)

@socketio.on("launch")
def launch_game():
    game_name = session["game"]
    game = manager.get_game(game_name)
    print(game)
    game.launch() # GameRun(players)
    emit("game-launched", broadcast=True, room=game_name)

    launch_run(game_name, game.curr_run_id)

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

@socketio.on('guess')
def process_guess(data):
    # global duration_thread
    game_name = session["game"]
    game = manager.get_game(game_name)

    player = data["player"]
    lon, lat = data["lon"], data["lat"]
    res, done = game.current.process_answer((lon, lat), player)
    emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True, room=game_name)
    emit("new-guess", dict(player=player, dist=res["dist"], delta=res["delta"], score=res["score"]),
         broadcast=True, room=game_name)
    emit("score", res, json=True)
    if done:
        try:
            print(f"--\nInterrupting run {game.curr_run_id+1}\n--")
            safe_cancel(timers[game_name])
        except AttributeError:
            pass

        end_game(game_name, game.curr_run_id)


# DEBUG = False
if __name__ == '__main__':
    if DEBUG:
        # Prevent server from being visible from the outside
        kwargs = dict(debug=True)
    else:
        port = os.environ.get("PORT", 80)
        kwargs = dict(host= '0.0.0.0', port=port)
    socketio.run(app, **kwargs)