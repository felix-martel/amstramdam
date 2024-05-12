import pytest

from amstramdam import app as base_app, manager
from tests.server_utils import parse_events, parse_html, connect_socketio

TEST_GAME = "_test_game_"


@pytest.fixture
def game():
    name, game = manager.create_game(dataset_name="world_capitals", force_name=TEST_GAME, is_permanent=True)
    yield game
    manager.remove_game(name)


@pytest.fixture
def app():
    base_app.config["TESTING"] = True
    base_app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
    yield base_app


@pytest.fixture
def client(game, app):
    app.config["TESTING"] = True
    app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
    return app.test_client()


def test_homepage(client):
    r = client.get("/", follow_redirects=True)
    assert r.status_code == 200
    assert r.mimetype == "text/html"

    html = parse_html(r.data)
    assert html.find(".//title").text == "am·stram·dam"


def test_join_game(app, game, client):
    with client:
        r = client.get(f"/game/{game.name}", follow_redirects=True)
        assert r.status_code == 200
        # TODO: for some reason, `session` object is not updated during tests
        # assert session["game"] == game.name
    player1 = connect_socketio(client)
    assert player1.is_connected()

    player1.emit("connection", {"pseudo": "gorgz"})
    received = player1.get_received()
    events = parse_events(received)

    assert "init" in events
    assert "new-player" in events

    id1 = events["init"]["player"]

    assert events["new-player"]["player"] == id1
    assert events["new-player"]["pseudo"] == "gorgz"
