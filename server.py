"""
Associated with conda env 'tdc'
"""
import threading
import atexit

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, send, emit

from game import GameRun, PlayerList
from game_full import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = "this is intended to be secret"
socketio = SocketIO(app)

@app.route("/")
def serve_main():
    return render_template("main.html")

N_RUNS = 10
TIME_BETWEEN_RUNS = 5

player_names = PlayerList()
players = set()
game = Game(n_run=N_RUNS)
duration_thread = threading.Thread()

def interrupt():
    global duration_thread
    duration_thread.cancel()

@socketio.on('connection')
def init_game(data):
    if "player" in session:
        player = session["player"]
        if player not in game.players:
            game.add_player(player)
    else:
        player = game.add_player()
        session["player"] = player

    print(f"Player <{player}> connected...", end=" ")
    emit("init", dict(player=player))
    emit("new-player", dict(player=player, leaderboard=game.get_current_leaderboard()), broadcast=True)

def safe_cancel(timer):
    try:
        timer.cancel()
    except AttributeError:
        pass

@socketio.on('disconnection')
def remove_from_game():
    player = session["player"]
    game.remove_player(player)
    emit("player-left", dict(player=player, leaderboard=game.get_current_leaderboard()), broadcast=True)

def end_game():
    global game
    print(f"\n--\nEnding run {game.curr_run_id+1}\n--\n")
    with app.test_request_context('/'):
        print("Entering end callback")
        # 1: get current place
        refname, (lon, lat) = game.current.place
        answer = dict(name=refname, lon=lon, lat=lat)

        # 2: end game
        records = game.current.records
        results, done = game.end()
        socketio.emit("run-end", dict(
            results=records,
            answer=answer,
            leaderboard=game.get_current_leaderboard()),
        json=True, broadcast=True)
        print("Run done")

        # 3: continue?
        if done:
            # Do something, e.g display final results
            socketio.emit("game-end", dict(leaderboard=game.get_current_leaderboard()), json=True, broadcast=True)

            game = Game(players=set(game.players), n_run=N_RUNS)
            return
        else:
            global duration_thread
            duration_thread = threading.Timer(TIME_BETWEEN_RUNS, launch_run)
            duration_thread.start()

def launch_run():
    global duration_thread
    print(f"\n--\nLaunching run {game.curr_run_id+1}\n--\n")
    with app.test_request_context('/'):
        hint = game.current.launch()
        duration_thread = threading.Timer(game.current.DURATION, end_game)
        duration_thread.start()
        print(f"Hint is '{hint}")
        socketio.emit("run-start", dict(hint=hint, current=game.curr_run_id, total=game.n_run), json=True, broadcast=True)


@socketio.on("launch")
def launch_game():
    print(game)
    game.launch() # GameRun(players)
    print("Game created...launching game")
    emit("game-launched", broadcast=True)

    launch_run()

@socketio.on('guess')
def process_guess(data):
    global duration_thread
    print(data)
    player = data["player"]
    lon, lat = data["lon"], data["lat"]

    res, done = game.current.process_answer((lon, lat), player)
    emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True)
    emit("score", res, json=True)
    if done:
        try:
            print(f"\n--\nInterrupting run {game.curr_run_id+1}\n--\n")
            safe_cancel(duration_thread)
        except AttributeError:
            pass
        end_game()
        # emit("run-end", dict(results=game.records, answer=res["answer"]), json=True, broadcast=True)
        # print("Game done")

atexit.register(interrupt)



if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0', port=80)