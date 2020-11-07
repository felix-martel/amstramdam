from amstramdam import app, socketio, is_local
import os
from argparse import ArgumentParser


certfile = "extra/certif.crt"
keyfile ="extra/certif.key"

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", help="Enable live-reloading", action="store_true")
    args = parser.parse_args()

    port = os.environ.get("PORT", 80)
    kwargs = dict(host= '0.0.0.0', port=port)

    if is_local:
        kwargs["certfile"] = certfile
        kwargs["keyfile"] = keyfile
        kwargs["port"] = 443

    if args.debug:
        kwargs["debug"] = True
        print("Live-reloading enabled")

    socketio.run(app, **kwargs)