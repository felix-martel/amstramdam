"""
Associated with conda env 'tdc'
# TODO add a refresh button on 'public games' or auto-refresh
# TODO add the number of people connected on the lobby screen
"""
import os
import json
from collections import defaultdict

from flask import Flask
from flask_socketio import SocketIO
from flask_talisman import Talisman

from .city_parser import GameMap, MAPS
import amstramdam.game_manager as manager

import eventlet
eventlet.monkey_patch(socket=False)

# Read environment variables
IS_LOCAL = os.environ.get("IS_HEROKU") != "1"
SECRET_KEY = os.environ.get("SECURE_KEY", "dummy_secure_key_for_local_debugging").split(",")[0]

# Load configuration file
with open("config.json", "r", encoding="utf8") as fp:
    CONF = json.load(fp)

# Load Content Security Policy
with open("csp.json", "r", encoding="utf8") as fp:
    csp = json.load(fp)

hosts = CONF["hosts"]
hosts += ["www." + name for name in hosts]
if IS_LOCAL:
    hosts += ["127.0.0.1", "localhost"]
valid_hosts = ["https://"+h for h in hosts]

# Init Flask app
print(f"Creating app... (local={IS_LOCAL})")
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Init Talisman for HTTP headers
Talisman(app,
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src'],
         force_https=CONF["allowHTTP"]
         )

# Init SocketIO
debug_params = dict(engineio_logger=True, logger=True) if IS_LOCAL and CONF["verbose"] else {}
socketio = SocketIO(app,
                    async_mode=CONF["async"],
                    cors_allowed_origins=valid_hosts,
                    **debug_params
                    )

timers = defaultdict(int)

import amstramdam.routes
import amstramdam.events
