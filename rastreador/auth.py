import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
)
from werkzeug.security import check_password_hash, generate_password_hash

from rastreador.db import get_db
from rastreador.cargos import Cargo
import click


class User:
    def __init__(self,cargo,username,id):
        self.cargo = cargo
        self.username = username
        self.id = id

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        u = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        g.user = User(u['cargo'], u['username'], u['id'])

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


#Implementação de RBAC
@bp.cli.command('promote')
@click.argument('username')
def promote_user(username):
    """Muda o cargo do usuario `username` para GERENTE"""
    change_role_name(username, Cargo.MANAGER.value)
    click.echo(f'Promoveu {username} para gerente.')

def change_role_name(username, new_role):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE user SET cargo=(?) WHERE username=(?)", (new_role, username))
    db.commit()
#mais rapido, se você tem o ID
def change_role_id(id, new_role):
    db = get_db()
    cur = db.cursor()
    print(f"Atualizando usuario {id} para {new_role}")
    cur.execute("UPDATE user SET cargo=(?) WHERE id=(?)", (new_role, id))
    db.commit()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view