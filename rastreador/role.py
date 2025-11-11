import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from rastreador.db import get_db
from rastreador.cargos import Cargo, cargos, pode_alterar_cargo
from rastreador.auth import User, change_role_id

bp = Blueprint('role', __name__,)

@bp.route('/users')
def users():
    if not g.user:
        return redirect(url_for('auth.login'))
    if not pode_alterar_cargo(g.user):
        return "Falha na autorização.", 403
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT cargo, username, id FROM user' )
    allrows = cur.fetchall()
    users = [User(row[0],row[1],row[2]) for row in allrows]
    return render_template("role/role.html", usuarios=users)


@bp.route('/alterar_cargo/<id>', methods=('GET', 'POST'))
def edit(id):
    if not g.user:
        return redirect(url_for('auth.login'))
    if not pode_alterar_cargo(g.user):
        return "Falha na autorização.", 403
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT cargo, username FROM user where id=(?)', id)
    row = cur.fetchone()
    cargo = row[0]
    username = row[1]
    if request.method == 'POST':
        cargonovo = request.form['cargoNovo'][1:-1] #remova "" em torno do string (strip e replace não funcionaram por alguma razão)
        try:
            cargonovo = Cargo(cargonovo)
            cargo = cargonovo.value
            change_role_id(id, cargonovo.value)
        except ValueError as e:
            flash(f"Erro na seleção do novo cargo: {e}")

    return render_template("role/edit.html", usename=username, cargo=cargo, cargos=cargos)