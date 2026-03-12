import pytest
from app import app

#
#             TESTS FOR THE FLASK APP
#   WRITE TESTS CASES FOR THE SERVER ENDPOINTS HERE
#

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_hello_world(client, capsys):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
