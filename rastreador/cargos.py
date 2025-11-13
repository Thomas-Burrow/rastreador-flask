from enum import Enum


class Cargo(Enum):
    USER = "Usuario"
    SECRETARY = "Secretário"
    MECHANIC = "Mecânico"
    HR = "RH"
    MANAGER = "Gerente"


cargos = [member.value for member in Cargo]


def get_cargo_username(user):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT cargo FROM user where username=(?)", user)
    row = cur.fetchone()
    return row[0]


def get_cargo_id(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT cargo FROM user where id=(?)", id)
    row = cur.fetchone()
    return row[0]


def pode_alterar_status(u):
    if u is None:
        return False
    if u.cargo == Cargo.MECHANIC.value or u.cargo == Cargo.MANAGER.value:
        return True
    else:
        return False


def pode_criar_pedido(u):
    if u is None:
        return False
    if (
        u.cargo == Cargo.SECRETARY.value
        or u.cargo == Cargo.MECHANIC.value
        or u.cargo == Cargo.MANAGER.value
    ):
        return True
    else:
        return False


def pode_alterar_cargo(u):
    if u is None:
        return False
    if u.cargo == Cargo.HR.value or u.cargo == Cargo.MANAGER.value:
        return True
    else:
        return False
