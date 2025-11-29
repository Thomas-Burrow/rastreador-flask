import mariadb
from datetime import datetime

import rastreador.cargos
from rastreador.models import Veiculo, Estado
import click
from flask import current_app, g

conn_params = None  # Nos vamos inicializar estes dados depois, quando o aplicativo estiver andando (para o comando init_db funcionar)

# Sempre deve ter comunicação com o banco de dados
pool = None


def get_db() -> mariadb.Connection:
    global pool  # uma ideia duvidosa, mas já que somente é modificado nesta funcão e só é inicializado quando nulo não deve apresentar problemas sérios
    global conn_params
    if conn_params is None:
        conn_params = {
            "user": current_app.config["MARIADB_USER"],
            "password": current_app.config["MARIADB_PASSWORD"],
            "host": current_app.config["MARIADB_HOST"],
            "database": current_app.config["MARIADB_DBNAME"],
        }
    if pool is None:
        pool = mariadb.ConnectionPool(pool_name="Walrus", pool_size=30, **conn_params)
    # get connection from our connection pool
    return pool.get_connection()


def close_db(e=None):
    global pool
    if pool is not None:
        pool.close()
        pool = None


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    conn.begin()

    with current_app.open_resource("schema.sql") as f:
        schema = f.read().decode("utf8")
        for statement in schema.split(
            ";"
        ):  # ao inves do sqlite, precisamos quebrar o schema em pedaços executaveis
            if statement.strip():  # evita executar vazios
                cursor.execute(statement)
    conn.commit()
    print("Schema loaded successfully.")


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def placa_e_estado(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT placa, estado FROM ordem_servico where id=(?)", (id,))
    row = cur.fetchone()
    placa = row[0]
    estado_atual = row[1]
    try:
        estado_enum = Estado(estado_atual)
    except:
        estado_enum = Estado.AGUARDANDO
    return (placa, estado_enum)


def veiculos_pendentes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'SELECT placa, estado, id FROM ordem_servico WHERE estado <> "Retirado"'
    )  # TODO: mostrar retirados recentes, mas não aqueles retirados muito antes
    allrows = cur.fetchall()
    veiculos = [Veiculo(row[0], row[1], row[2]) for row in allrows]
    return veiculos
