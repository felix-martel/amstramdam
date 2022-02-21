from amstramdam.game.types import Pseudo


MAX_LEN = 20


def is_valid(name: str | None) -> bool:
    """Return True if the candidate nickname is valid (i.e non-empty)"""
    # TODO: implement checks?
    return name is not None and len(str(name)) > 0


def clean(name: str) -> Pseudo:
    """Process the candidate nickname so that it meets our requirements"""
    if len(name) > MAX_LEN + 3:
        name = name[:MAX_LEN] + "..."
    return Pseudo(name)
