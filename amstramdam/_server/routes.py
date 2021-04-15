import os

from amstramdam._server.main import app, IS_BETA
from flask import (
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    send_file,
)


@app.route("/")
def serve_main():
    return jsonify({"payload": "Hello world"})
    return render_template(
        "lobby.html",
        datasets=[],
        games=[],
        is_beta=IS_BETA,
    )


@app.route("/games")
def get_public_games():
    pass


@app.route("/datasets")
def get_all_datasets():
    pass


@app.route("/builder")
def serve_builder():
    pass


@app.route("/editor")
def serve_editor():
    pass


@app.route("/points/<dataset>")
def get_dataset_geometry(dataset):
    pass


@app.route("/dataset/<dataset>")
def get_edit_information(dataset):
    pass


@app.route("/commit/<dataset>", methods=["POST"])
def commit_dataset_change(dataset):
    pass


@app.route("/new", methods=["GET", "POST"])
def create_new_game():
    pass


@app.route("/game/<name>")
def serve_game(name):
    pass

