from amstramdam.game import players as pl
import pytest


def test_player_list():
    players = pl.PlayerList("test")
    p1, n1 = players.add_player()
    player_id = pl.Player("foo")
    nickname = pl.Pseudo("foobar")
    p2, n2 = players.add_player(player=player_id)
    p3, n3 = players.add_player(nickname=nickname)
    assert player_id in players
    assert players.get_nickname(p2) == n2
    with pytest.raises(Exception):
        # Adding existing player should not be allowed
        players.add_player(player=player_id)

    alt_players = pl.PlayerList("alt")
    with pytest.raises(Exception):
        # Adding a player that exists in another list should not be allowed either
        alt_players.add_player(player=p1)

    assert n2 not in players._available_names
    players.remove_player(p2)
    assert n2 in players._available_names
    players.remove_player(p3)
    assert n3 not in players._available_names
    new_n1 = players.request_nickname(p1)
    assert new_n1 != n1
    assert players.get_nickname(p1) == new_n1
    assert not pl.PlayerList("test", nicknames={p1: n1}).nicknames
    assert p1 in pl.PlayerList("foo", players={p1, p2})
    assert p3 not in pl.PlayerList("foo", players={p1, p2})
    assert n2 == pl.PlayerList("foo", players={p1}, nicknames={p1: n2}).get_nickname(p1)
