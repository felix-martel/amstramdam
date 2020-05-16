"""
Associated with conda env 'tdc'
"""
import threading
import atexit

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, send, emit

from game import GameRun, PlayerList

app = Flask(__name__)
app.config['SECRET_KEY'] = "this is intended to be secret"
socketio = SocketIO(app)

@app.route("/")
def serve_main():
    return render_template("main.html")


player_names = PlayerList()
players = set()
game = None
duration_thread = threading.Thread()

def interrupt():
    global duration_thread
    duration_thread.cancel()

@socketio.on('connection')
def init_game(data):
    if "player" in session:
        player = session["player"]
    else:
        player = player_names.new()
        session["player"] = player
    players.add(player)

    print(f"Player <{player}> connected...", end=" ")
    emit("init", dict(player=player, players=list(players)))
    emit("new-player", dict(player=player), broadcast=True)

@socketio.on('disconnection')
def remove_from_game():
    player = session["player"]
    players.remove(player)
    emit("player-left", dict(player=player), broadcast=True)



@socketio.on("launch")
def launch_game():
    global game
    global duration_thread

    def end_game():
        with app.test_request_context('/'):
            print("Entering end callback")
            refname, (lon, lat) = game.place
            answer = dict(name=refname, lon=lon, lat=lat)
            socketio.emit("run-end", dict(results=game.records, answer=answer), json=True, broadcast=True)
            print("Game done")

    game = GameRun(players)
    print("Game created...launching game")
    emit("game-launched", broadcast=True)

    hint = game.launch()

    duration_thread = threading.Timer(game.DURATION, end_game)
    duration_thread.start()
    print(f"Hint is '{hint}")
    emit("target", dict(hint=hint), json=True, broadcast=True)

@socketio.on('guess')
def process_guess(data):
    print(data)
    player = data["player"]
    lon, lat = data["lon"], data["lat"]

    res, done = game.process_answer((lon, lat), player)
    emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True)
    emit("score", res, json=True)
    if done:
        end_game()
        # emit("run-end", dict(results=game.records, answer=res["answer"]), json=True, broadcast=True)
        # print("Game done")

atexit.register(interrupt)



if __name__ == '__main__':
    socketio.run(app, host= '0.0.0.0')