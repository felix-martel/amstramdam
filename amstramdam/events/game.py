from amstramdam import app, socketio, timers, manager
from flask import session
from flask_socketio import emit
from .utils import safe_cancel, wait_and_run

def terminate_game(game_name):
    game = manager.get_game(game_name)
    if game is None or not game.done:
        return
    game.terminate()
    payload = dict(
                      leaderboard=game.get_current_leaderboard(),
                      full=game.get_final_results(), # TODO: remove useless data
                  )
    socketio.emit("status-update",
                  dict(status=game.status, payload=payload), json=True, broadcast=True,
                  room=game_name)
    manager.relaunch_game(game_name)

def end_game(game_name, run_id):
    # global game
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id or game.done:
        return
    print(f"\n--\nEnding run {game.curr_run_id+1}\n--\n")
    with app.test_request_context('/'):
        # 1: get current place
        (city_name, hint), (lon, lat) = game.current.place
        answer = dict(name=city_name, lon=lon, lat=lat)

        # 2: end game
        records = game.current.records
        results, done = game.end()
        payload = dict(results=records, answer=answer, leaderboard=game.get_current_leaderboard(), done=done)
        socketio.emit("status-update",
                      dict(status=game.status, payload=payload),
                      json=True, broadcast=True, room=game_name
                      )

        # 3: continue?
        if done:
            timers[game_name] = wait_and_run(game.wait_time, terminate_game, game_name)
        else:
            timers[game_name] = wait_and_run(game.wait_time, launch_run, game_name, game.curr_run_id)

def launch_run(game_name, run_id):
    # global duration_thread
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id:
        return
    print(f"--\nLaunching run {game.curr_run_id+1} for game <{game_name}>\n--")
    with app.test_request_context('/'):
        hint = game.launch_run()
        payload = dict(hint=hint, current=game.curr_run_id, total=game.n_run)
        print(f"Hint is '{hint}'")
        socketio.emit("status-update",
                      dict(status=game.status, payload=payload),
                      json=True,
                      room=game_name,
                      broadcast=True)

        timers[game_name] = wait_and_run(game.current.duration, end_game, game_name, game.curr_run_id)

@socketio.on("launch")
def launch_game():
    game_name = session["game"]
    player = session.get("player")
    if player is None:
        return

    game = manager.get_game(game_name)
    game.launch() # GameRun(players)
    payload = dict(game=game.map_name, runs=game.n_run, diff=game.difficulty, by=player)
    emit("status-update",
         dict(status=game.status, payload=payload),
         json=True, broadcast=True, room=game_name)

    wait_and_run(3, launch_run, game_name, game.curr_run_id)


@socketio.on('guess')
def process_guess(data):
    # global duration_thread
    game_name = session["game"]
    game = manager.get_game(game_name)
    player = session.get("player")
    if player is None:
        return

    #player = data["player"]
    print("Receiving guess from", player)
    lon, lat = data["lon"], data["lat"]
    res, done = game.current.process_answer((lon, lat), player)
    res["total_score"] = game.scores[player] + res["score"] # We need to add res["score"] between game.scores isn't updated yet
    # emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True, room=game_name)
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