import pytest
import random
random.seed(0)

from amstramdam._game.player import PlayerList


def test_add_player():
    players = PlayerList("foo")

    assert not players

    pid_1, name_1 = players.add()
    pid_2, name_2 = players.add()

    assert pid_1.startswith("foo_")
    assert len(players) == 2
    assert players[pid_1] == name_1
    assert pid_2 in players
    assert name_1 not in players._available_names
    assert name_2 not in players._available_names

    players.set_name(pid_2, "alice")
    assert players[pid_2] == "alice"
    assert name_2 in players._available_names

    name_3 = players.request_name(pid_2)
    assert players[pid_2] == name_3

    players.remove(pid_1)
    assert name_1 in players._available_names
    assert len(players) == 1

    players_dict = players.as_dict()
    assert players_dict == {pid_2: name_3}

    assert "imaginary player" not in players
    with pytest.raises(KeyError):
        # Access non-existing player
        name_4 = players["other imaginary player"]
    with pytest.raises(AssertionError):
        # Add an already existing player
        players.add(pid_2)

