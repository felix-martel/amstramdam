from typing import Literal

Status = Literal[
    "not-launched",
    "before-start",
    "running",
    "correction",
    "finished",
]

NOT_LAUNCHED: Status = "not-launched"
LAUNCHING: Status = "before-start"
RUNNING: Status = "running"
CORRECTION: Status = "correction"
FINISHED: Status = "finished"
