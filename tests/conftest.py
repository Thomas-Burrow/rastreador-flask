import os
import tempfile

import pytest
from rastreador import create_app
from rastreador.db import get_db, init_db


# veja https://flask.palletsprojects.com/en/stable/testing/ e https://docs.pytest.org/en/stable/ para saber o que está acontecendo


@pytest.fixture(scope="session")
def app():
    app = create_app(True)

    with app.app_context():
        init_db()
        conn = get_db()
        cursor = conn.cursor()
        conn.begin()

        with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
            data = f.read().decode("utf8")
            for statement in data.split(
                ";"
            ):  # ao inves do sqlite, precisamos quebrar o schema em pedaços executaveis
                if statement.strip():  # evita executar vazios
                    cursor.execute(statement)
        conn.commit()

    yield app


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
