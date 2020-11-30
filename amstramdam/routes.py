from amstramdam import app, manager, dataloader, IS_LOCAL, CONF
from flask import render_template, jsonify, request, session, redirect, url_for
from amstramdam.game.params_handler import merge_params

@app.route("/")
def serve_main():
    return render_template("lobby.html",
                           datasets=dataloader.datasets, games=manager.get_public_games())

@app.route("/games")
def get_public_games():
    return jsonify(manager.get_public_games())

@app.route("/datasets")
def get_all_datasets():
    return jsonify(dataloader.datasets)

@app.route("/builder")
def serve_builder():
    if IS_LOCAL:
        return render_template("builder.html", datasets=dataloader.datasets)
    return redirect(url_for("serve_main"))


@app.route("/points/<dataset>")
def get_dataset_geometry(dataset):
    try:
        labels = request.args.get("labels") == "true"
        print(request.form.get("labels"))
        print(request.form)
        data = dataloader.load(dataset).get_geometry(labels=labels)
    except KeyError as e:
        print(f"ERROR: No dataset named '{dataset}' found.")
        print(e)
        data = {}
    return jsonify(data)


@app.route("/new", methods=["GET", "POST"])
def create_new_game():
    params = merge_params(request.form)
    print(params)

    name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     difficulty=params["difficulty"],
                                     is_public=params["public"],
                                     allow_zoom=params["zoom"],
                                     precision_mode=params["precision_mode"],
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
            precision_mode=game.precision_mode,
            duration=game.duration)
        return render_template("main.html", game_name=name, params=params, debug=IS_LOCAL)
