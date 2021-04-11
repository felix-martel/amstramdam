from amstramdam import socketio, app
from lxml import etree


def parse_html(data: str):
    return etree.fromstring(data, etree.HTMLParser())


def connect_socketio(client):
    return socketio.test_client(app, flask_test_client=client)


def parse_events(received_events):
    parsed = {}
    for event in received_events:
        name = event.pop("name")
        args = event.get("args", [])
        parsed[name] = args[0] if len(args) else {}
    return parsed
