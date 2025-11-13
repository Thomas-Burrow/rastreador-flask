import os
import tempfile

import pytest
from rastreador import create_app
from rastreador.db import get_db, init_db

# TODO: criar um usuario de teste e veiculos de teste para inserir no contexto de teste
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")

# veja https://flask.palletsprojects.com/en/stable/testing/ e https://docs.pytest.org/en/stable/ para saber o que está acontecendo


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, username, password):
            return client.post(
                "/auth/login", data={"username": username, "password": password}
            )

        def logout(self):
            return client.get("/auth/logout")

    return AuthActions()
