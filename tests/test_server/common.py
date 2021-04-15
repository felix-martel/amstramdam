import os


def run_server(*args):
    joined_args = " ".join(map(str, args))
    if joined_args:
        joined_args = " " + joined_args
    return os.system("python main.py" + joined_args)
