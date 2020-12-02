import os

from amstramdam import app, manager, dataloader, IS_LOCAL, CONF
from flask import render_template, jsonify, request, session, redirect, url_for, send_file
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

@app.route("/editor")
def serve_editor():
    CAN_EDIT = request.args.get("auth", "_") == os.environ.get("EDITOR_ACCESS_KEY")
    if IS_LOCAL or CAN_EDIT:
        return render_template("editor.html", datasets=dataloader.datasets)
    return redirect(url_for("serve_main"))


@app.route("/points/<dataset>")
def get_dataset_geometry(dataset):
    try:
        label=request.args.get("labels") == "true"
        data = dataloader.load(dataset).get_geometry(label=label)
    except KeyError as e:
        print(f"ERROR: No dataset named '{dataset}' found.")
        print(e)
        data = {}
    return jsonify(data)

@app.route("/edit/<dataset>")
def get_edit_information(dataset):
    CAN_COMMIT = request.args.get("auth", "_") == os.environ.get("EDITOR_COMMIT_KEY")
    if not (IS_LOCAL or CAN_COMMIT):
        return jsonify(message="Invalid access key") #redirect(url_for("serve_main"))
    data = dataloader.load(dataset).get_dataframe_as_json()
    return jsonify(data)

@app.route("/commit/<dataset>", methods=["POST"])
def commit_dataset_change(dataset):
    changes = request.json
    CAN_COMMIT = request.json.get("auth", "_") == os.environ.get("EDITOR_COMMIT_KEY")
    if not (IS_LOCAL or CAN_COMMIT):
        return jsonify(message="Invalid access key")
    out, fn = dataloader.commit_changes(dataset, changes)
    if changes.get("output") == "download":
        return send_file(out,
                         mimetype="text/csv",
                         as_attachment=True,
                         attachment_filename="file.csv")#fn)
    return jsonify(dict(message="Commit request received."))


@app.route("/new", methods=["GET", "POST"])
def create_new_game():
    if not IS_LOCAL:
        return redirect(url_for("serve_main"))
    params = merge_params(request.form)
    name, game = manager.create_game(n_run=params["runs"],
                                     duration=params["duration"],
                                     difficulty=params["difficulty"],
                                     is_public=params["public"],
                                     allow_zoom=False, #params["zoom"],
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
            difficulty=game.difficulty,
            allow_zoom=game.allow_zoom,
            precision_mode=game.precision_mode,
            duration=game.duration)
        return render_template("main.html", game_name=name, params=params, debug=IS_LOCAL)
