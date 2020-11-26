from amstramdam import app, manager, dataloader, IS_LOCAL, CONF
from flask import render_template, jsonify, request, session, redirect, url_for


@app.route("/")
def serve_main():
    return render_template("lobby.html",
                           datasets=dataloader.datasets,
                           games=manager.get_public_games())


@app.route("/points/<dataset>")
def get_dataset_geometry(dataset):
    try:
        data = dataloader.load(dataset).get_geometry()
    except KeyError as e:
        print(f"ERROR: No dataset named '{dataset}' found.")
        print(e)
        data = {}
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
    converts = [
        (int, ["duration", "runs", "wait_time", "difficulty"]),
        (bool, ["public", "zoom"])
    ]
    for convert, keys in converts:
        for key in keys:
            params[key] = convert(params[key])

    params["difficulty"] /= 100
    print(params)
    name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     difficulty=params["difficulty"],
                                     is_public=params["public"],
                                     allow_zoom=params["zoom"],
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
            ssl_disabled=CONF["disableSSL"],
            allow_zoom=game.allow_zoom,
            duration=game.duration)
        return render_template("main.html", game_name=name, params=params, debug=IS_LOCAL)
