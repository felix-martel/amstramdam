import time
import multiprocessing

import pytest
import requests

from tests.server.common import run_server


@pytest.fixture
def server():
    p = multiprocessing.Process(target=run_server)
    p.start()
    time.sleep(1)
    yield p
    p.kill()


def test_server_launch(server):
    response = requests.get("https://localhost:443")
    assert response.status_code == 200
