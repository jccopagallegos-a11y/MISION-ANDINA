import pytest
from app import create_app

@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret",
                      "DATABASE": str(tmp_path / "test.sqlite")})
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def register_and_login(client, email="juan@example.com"):
    client.post("/registro", data={"name":"Juan","email":email,"password":"clave123"})
    return client.post("/login", data={"email":email,"password":"clave123"}, follow_redirects=True)
