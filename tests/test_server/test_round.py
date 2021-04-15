import pytest
from unittest import mock
import time

from amstramdam._game.scorer import Scorer
from amstramdam._game.round import GameRound
from amstramdam._game.player import PlayerList, PlayerId
from amstramdam._game import geo


def test_scorer():
    scorer = Scorer(non_linear_bonus=False, multiplier=1_000)
    score = scorer.score(0, 2.5)

    expected_keys = {"distance", "duration", "distance_score", "time_score", "score"}
    for key in expected_keys:
        assert key in score

    assert score["distance_score"] == 1_000
    assert score["time_score"] == 500
    assert score["score"] == 1_500

    scorer = Scorer(non_linear_bonus=True, non_linear_bonus_amount=0.2, multiplier=1_000)
    score = scorer.score(0, 8)
    assert score["distance_score"] == 1_200
    assert score["time_score"] == 0

    scorer = Scorer(precision_mode=True)
    score = scorer.score(120.8, 2.56)
    assert score["time_score"] == 0


def test_round():
    true_coords = {"lon": 5, "lat": 42}
    pred_coords = {"lon": 5.2, "lat": 43.8}
    place = {"name": "foo", "hint": "bar", "coords": true_coords}
    alice = PlayerId("alice")
    bob = PlayerId("bob")

    players = PlayerList("test_game")
    players.add(alice)
    players.add(bob)

    scorer = Scorer()

    game = GameRound(place=place, players=players, scorer=scorer)

    geo.distance = mock.Mock(return_value=100)
    game.launch()
    time.sleep(1)
    rec, done = game.process_answer(alice, {"lon": 5.2, "lat": 43.8})

    # Assert the game does not end too early
    assert not done

    # Assert time and distance are computed correctly
    assert rec["score"]["duration"] == pytest.approx(1, abs=1e-2)
    assert rec["score"]["distance"] == 100
    assert game.records[alice] == rec

    # Assert remaining players are valid
    assert alice not in game._remaining_players
    assert bob in game._remaining_players

    # Assert unknown player raises an exception
    with pytest.raises(Exception):
        game.process_answer(PlayerId("carlos"), {"lon": 4.3, "lat": 45.8})

    # Assert the round ends properly
    rec, done = game.process_answer(bob, {"lon": 4.3, "lat": 45.8})
    assert done
