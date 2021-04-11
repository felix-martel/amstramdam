import pytest
import flask

from amstramdam import app, manager
from tests.server_utils import parse_events, parse_html, connect_socketio

TEST_GAME = "_test_game_"


@pytest.fixture
def game():
    name, game = manager.create_game(force_name=TEST_GAME, is_permanent=True)
    yield game
    manager.remove_game(name)


@pytest.fixture
def client(game):
    with app.test_client() as flask_client:
        yield flask_client


def test_homepage(client):
    r = client.get("/", follow_redirects=True)
    print(r.mimetype)
    assert r.status_code == 200
    assert r.mimetype == "text/html"

    html = parse_html(r.data)
    assert html.find(".//title").text == "am·stram·dam"


def test_join_game(game, client):
    with app.test_request_context():
        r = client.get(f"/game/{game.name}", follow_redirects=True)
        assert r.status_code == 200
        assert flask.session["game"] == game.name
        # player1 = socketio.test_client(app, flask_test_client=client)
        player1 = connect_socketio(client)
        assert player1.is_connected()

        player1.emit("connection", {"pseudo": "gorgz"})
        received = player1.get_received()
        events = parse_events(received)

        assert "init" in events
        assert "new-player" in events

        id1 = events["init"]["player"]

        print(player1.get_received())

        assert events["new-player"]["player"] == id1
        assert events["new-player"]["pseudo"] == "gorgz"
