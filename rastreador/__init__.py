import os
from flask import Flask, render_template


def create_app(test_config=False):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is False:
        if os.path.exists(
            "/run/secret/config.py"
        ):  # TODO: puxe esses valores do /run/secret/ e nome de arquivo para variaveis
            app.config.from_pyfile(
                "/run/secret/config.py", silent=True
            )  # quando em podman/docker
        else:
            app.config.from_pyfile(
                "config.py", silent=True
            )  # quando desenvolvendo fora do container
    else:
        if os.path.exists("/run/secret/config-test.py"):
            app.config.from_pyfile("/run/secret/config-test.py")
        else:
            app.config.from_pyfile("config-test.py")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    from . import ordem

    app.register_blueprint(ordem.bp)

    from . import scan

    app.register_blueprint(scan.bp)

    from . import role

    app.register_blueprint(role.bp)

    from . import api

    app.register_blueprint(api.bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
