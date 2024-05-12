from amstramdam import app, manager, socketio, IS_LOCAL, CONF, dataloader
import os
from argparse import ArgumentParser


certfile = "extra/certif.crt"
keyfile = "extra/certif.key"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--debug", help="Enable live-reloading", action="store_true"
    )
    args = parser.parse_args()

    kwargs = dict(host="0.0.0.0")

    if IS_LOCAL and not CONF["disableSSL"]:
        kwargs["certfile"] = certfile
        kwargs["keyfile"] = keyfile
        kwargs["port"] = int(os.environ.get("PORT", 8000))
    else:
        kwargs["port"] = int(os.environ.get("PORT", 80))

    if args.debug:
        kwargs["debug"] = True
        check_loading = False
        debug_game = True
        message = "Live-reloading enabled"
        if debug_game:
            name, game = manager.create_game(
                dataset_name="paris_subway",
                n_runs=3,
                is_permanent=True,
                duration=5,
                map="paris_subway",
                wait_duration=4,
                force_name="__debug__",
            )
            for _ in range(3):
                game.add_player(nickname=None)
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
                                _, game = manager.create_game(
                                    n_run=10, map=m["map_id"], difficulty=level["index"]
                                )
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
