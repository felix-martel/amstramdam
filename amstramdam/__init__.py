"""
Associated with conda env 'tdc'
# TODO add a 'Connect' button when connection is not automatic
# TODO add a refresh button on 'public games' or auto-refresh
# TODO add the number of people connected on the lobby screen
"""
import os
import json
from collections import defaultdict
import argparse

from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
from flask_talisman import Talisman

from .city_parser import GameMap, MAPS
import amstramdam.game_manager as manager



import eventlet
eventlet.monkey_patch(socket=False)

VERBOSE = os.environ.get("FLASK_VERBOSE") == "1"
is_local = os.environ.get("IS_HEROKU") != "1"

hosts = ["multigeo.herokuapp.com", "amstramdam.com"]
hosts += ["www." + name for name in hosts]
if is_local:
    hosts.extend(["127.0.0.1", "localhost"])
valid_hosts = ["http://"+h for h in hosts] + ["https://"+h for h in hosts]

async_mode = "eventlet" # "threading"

print(f"Creating app with parameters async={async_mode}, local={is_local}")

debug_params = dict(engineio_logger=True, logger=True) if is_local and VERBOSE else {}
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECURE_KEY", "dummy_secure_key_for_local_debugging").split(",")[0]

with open("csp.json", "r", encoding="utf8") as fp:
    csp = json.load(fp)

Talisman(app, content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'], force_https=True)



socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=valid_hosts, **debug_params)

DATASETS = manager.get_all_datasets()
DATASET_GEOMETRIES = dict()

timers = defaultdict(int)


import amstramdam.routes
import amstramdam.events







