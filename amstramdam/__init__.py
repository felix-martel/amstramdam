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

import amstramdam.game.manager as manager
from .datasets import Dataloader

import eventlet
eventlet.monkey_patch(socket=False)

# Read environment variables
IS_LOCAL = os.environ.get("IS_HEROKU") != "1"
NO_SSL = os.environ.get("NO_SSL") == "1"
SECRET_KEY = os.environ.get("SECURE_KEY", "dummy_secure_key_for_local_debugging").split(",")[0]

# Load configuration file
with open("config.json", "r", encoding="utf8") as fp:
    CONF = json.load(fp)
CONF["disableSSL"] = CONF["disableSSL"] or NO_SSL

# Load Content Security Policy
with open("csp.json", "r", encoding="utf8") as fp:
    csp = json.load(fp)

hosts = CONF["hosts"]
hosts += ["www." + name for name in hosts]
if IS_LOCAL:
    hosts +=  ["127.0.0.1", "localhost"]
valid_hosts = ["http://"+h for h in hosts] if CONF["disableSSL"] \
    else ["https://"+h for h in hosts]

# Init Flask app
print(f"Creating app... (local={IS_LOCAL}, SSL disabled={CONF['disableSSL']})")


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='[[',
        variable_end_string=']]',
    ))


app = CustomFlask(__name__)
#app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Init Talisman for HTTP headers
print("SSL disabled :", CONF["disableSSL"])

Talisman(app,
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src'],
         force_https=not CONF["disableSSL"]
         )

# Init SocketIO
logger = IS_LOCAL and CONF["verbose"]
socketio = SocketIO(app,
                    async_mode=CONF["async"],
                    cors_allowed_origins=valid_hosts,
                    engineio_logger=logger,
                    logger=logger,
                    )

# Load available datasets
dataloader = Dataloader(CONF["datasets"])

timers = defaultdict(int)

import amstramdam.routes
import amstramdam.events
