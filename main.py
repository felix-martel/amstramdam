import os
from amstramdam._server import app, socketio, IS_LOCAL

if __name__ == "__main__":
    port = os.environ.get("PORT", 80)
    params = dict(host="0.0.0.0", port=port)

    if IS_LOCAL:
        params["certfile"] = "extra/local-crt.pem"
        params["keyfile"] = "extra/local-key.pem"
        params["port"] = 443

    socketio.run(app, **params)
