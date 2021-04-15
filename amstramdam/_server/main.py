import os
import sys
import json

import eventlet
from amstramdam._server._flask import Flask
from flask_talisman import Talisman
from flask_socketio import SocketIO


eventlet.monkey_patch(socket=True)

# Read environment variables
IS_LOCAL = os.environ.get("IS_HEROKU") != "1"
IS_BETA = os.environ.get("IS_BETA") == "1"
SECRET_KEY = os.environ.get("SECURE_KEY", "dummy_secure_key_for_local_debugging").split(
    ","
)[0]

if IS_LOCAL and sys.platform == "darwin":
    # Fix for https://github.com/eventlet/eventlet/issues/670
    eventlet.hubs.use_hub("poll")

# Load configuration file
with open("config.json", "r", encoding="utf8") as fp:
    CONF = json.load(fp)

# Load Content Security Policy
with open("csp.json", "r", encoding="utf8") as fp:
    csp = json.load(fp)

# Configure valid hosts
hosts = CONF["hosts"]
hosts += ["www." + name for name in hosts]
if IS_LOCAL:
    hosts += ["127.0.0.1", "localhost"]
valid_hosts = ["https://" + h for h in hosts]


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Initialize Talisman for HTTP headers
Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=["script-src"],
    force_https=True,
)

# Initialize SocketIO
logger = IS_LOCAL and CONF["verbose"]
socketio = SocketIO(
    app,
    async_mode="eventlet",
    cors_allowed_origins=valid_hosts,
    engineio_logger=logger,
    logger=logger,
)
