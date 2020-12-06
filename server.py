from amstramdam import app, manager, socketio, IS_LOCAL, CONF, dataloader
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

    if IS_LOCAL and not CONF["disableSSL"]:
        kwargs["certfile"] = certfile
        kwargs["keyfile"] = keyfile
        kwargs["port"] = 443

    if args.debug:
        kwargs["debug"] = True
        check_loading = True
        debug_game = False
        message = "Live-reloading enabled"
        if debug_game:
            name, game = manager.create_game(n_run=3,
                                             is_permanent=True, duration=5,
                                             map="paris_subway", wait_time=4,
                                             is_public=True,
                                             allow_zoom=True,
                                             force_name="__debug__")
            for _ in range(3):
                game.add_player(pseudo=None)
            message += ", debug game created at https://localhost/game/__debug__"

        if check_loading:
            with open("dataset.log", "w", encoding="utf8") as f:
                errors = set()
                for G in dataloader.get_datasets():
                    print("\n", G["group"], file=f)
                    for m in G["maps"]:
                        for level in m["levels"]:
                            print(m["name"], level["name"], file=f)
                            try:
                                _, game = manager.create_game(n_run=10, map=m["map_id"], difficulty=level["index"])
                                print(game, file=f)
                            except Exception as e:
                                print("ERROR", e, file=f)
                                errors.add(m["name"])
                print(len(errors), "errors", file=f)
                print(*errors, file=f)
            message += f", {len(errors)} error(s) found when loading datasets"

        print(message)
        print(manager.get_public_games())

    socketio.run(app, **kwargs)