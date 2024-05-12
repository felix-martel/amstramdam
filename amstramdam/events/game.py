from amstramdam import app, socketio, timers, manager
from flask import session
from flask_socketio import emit

from .types import GameEndNotification, GameEndPayload
from .utils import safe_cancel, wait_and_run
from ..game.types import GameName, Coordinates


def terminate_game(game_name: GameName) -> None:
    game = manager.get_game(game_name)
    if game is None or not game.done:
        return
    game.terminate()
    payload = GameEndPayload(
        leaderboard=game.get_current_leaderboard(),
        full=game.get_final_results(),  # TODO: remove useless data
    )
    with app.test_request_context("/"):
        status = game.status
        print(
            f"Ending game <{game_name}> (emitting <event:status-update> "
            f"with status={status})"
        )
        socketio.emit(
            "status-update",
            GameEndNotification(status=status, payload=payload),
            room=game_name,
        )
        manager.relaunch_game(game_name)


def end_game(game_name: GameName, run_id: int) -> None:
    # global game
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id or game.done:
        return
    print(f"Ending run {game.curr_run_id+1}")
    with app.test_request_context("/"):
        # 1: get current place
        (city_name, hint), (lon, lat) = game.current.place
        answer = dict(name=city_name, lon=lon, lat=lat)

        # 2: end game
        records = game.current.records
        results, done = game.end()
        payload = dict(
            results=records,
            answer=answer,
            leaderboard=game.get_current_leaderboard(),
            done=done,
        )
        socketio.emit(
            "status-update",
            dict(status=game.status, payload=payload),
            room=game_name,
        )

        # 3: continue?
        if done:
            timers[game_name] = wait_and_run(game.params.wait_duration, terminate_game, game_name)
        else:
            timers[game_name] = wait_and_run(
                game.params.wait_duration, launch_run, game_name, game.curr_run_id
            )


def launch_run(game_name: GameName, run_id: int) -> None:
    # global duration_thread
    game = manager.get_game(game_name)
    if game is None or game.curr_run_id != run_id:
        return
    print(f"Launching run {game.curr_run_id+1} for game <{game_name}>")
    with app.test_request_context("/"):
        hint = game.launch_run()
        payload = dict(hint=hint, current=game.curr_run_id, total=game.params.n_runs)
        print(f"Hint is '{hint}'")
        socketio.emit(
            "status-update",
            dict(status=game.status, payload=payload),
            room=game_name,
        )

        timers[game_name] = wait_and_run(
            game.current.duration, end_game, game_name, game.curr_run_id
        )


@socketio.on("launch")
def launch_game() -> None:
    game_name = session["game"]
    player = session.get("player")
    if player is None:
        return

    game = manager.get_game(game_name)
    if game is None:
        return
    game.launch()  # GameRun(players)
    payload = dict(
        game=game.params.dataset_name,
        runs=game.params.n_runs,
        diff=game.params.level,
        by=player,
        small_scale=game.small_scale,
    )
    emit(
        "status-update",
        dict(status=game.status, payload=payload),
        broadcast=True,
        room=game_name,
    )

    wait_and_run(3, launch_run, game_name, game.curr_run_id)


@socketio.on("guess")
def process_guess(data: Coordinates) -> None:
    # global duration_thread
    game_name = session["game"]
    game = manager.get_game(game_name)
    player = session.get("player")
    if player is None or game is None:
        return

    # player = data["player"]
    print("Receiving guess from", player)
    lon, lat = data["lon"], data["lat"]
    res, done = game.current.process_answer((lon, lat), player)
    res["total_score"] = (
        game.scores[player] + res["score"]
    )  # We need to add res["score"] between game.scores isn't updated yet
    # emit("log", f"Player <{player}> has scored {res['score']} points", broadcast=True,
    # room=game_name)
    emit(
        "new-guess",
        dict(player=player, dist=res["dist"], delta=res["delta"], score=res["score"]),
        broadcast=True,
        room=game_name,
    )
    emit("score", res, json=True)
    if done:
        try:
            print(f"Interrupting run {game.curr_run_id+1}\n")
            safe_cancel(timers[game_name])
        except AttributeError:
            pass

        end_game(game_name, game.curr_run_id)
