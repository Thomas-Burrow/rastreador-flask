import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import qrcode
import base64
from enum import Enum
from io import BytesIO
from rastreador.db import get_db
from rastreador.cargos import pode_criar_pedido

bp = Blueprint('ordem', __name__, url_prefix='/ordem')

#TODO require auth

class Estado(Enum):
    AGUARDANDO = "Aguardando"
    OFICINA = "Oficina"
    TESTE = "Testagem"
    LAVAGEM = "Lavagem"
    COMPLETO = "Completo"
    RETIRADO = "Retirado"

    def get_msg(self):
        if self == self.AGUARDANDO:
            return "Aguardando."
        if self == self.OFICINA:
            return "Na oficina."
        if self == self.TESTE:
            return "Em teste."
        if self == self.LAVAGEM:
            return "Em lavagem."
        if self == self.COMPLETO:
            return "Aguardando retirada."
        if self == self.RETIRADO:
            return "Marcado como retirado pelo cliente."
        return "Desconhecido."





@bp.route('/criar', methods=('GET', 'POST'))
def criar():
    if not pode_criar_pedido(g.user):
        return "Falha na autorização.", 403
    if request.method == 'POST':
        placa = request.form['placa']
        db = get_db()
        cur = db.cursor()

        if not placa:
            flash("Sem placa.")



        try:
            cur.execute(
            "INSERT INTO ordem_servico (placa, estado) VALUES (?, ?)",
            (placa, Estado.AGUARDANDO.value) #nescessario usar .value para não dar erro
            )
            db.commit()
            novo_id = cur.lastrowid
            flash("Ordem de serviço criada")
            return redirect(url_for("ordem.imprimir_qrcode", id=novo_id))
        except OSError:
            flash("Erro na connexão com banco de dados")        

    return render_template('ordem.html')


@bp.route('/qrcode/<id>')
def imprimir_qrcode(id):
    if not pode_criar_pedido(g.user):
        return "Falha na autorização.", 403
    qrdata = None
    if id is not None:
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT placa FROM ordem_servico where id=(?)', id)
        placa = cur.fetchone()[0]
        buffer = BytesIO()
        img = qrcode.make(url_for("scan.scan", _external=True, id=id))
        img.save(buffer, format="PNG")
        image_bytes=buffer.getvalue()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        qrdata = f"data:image/png;base64,{base64_encoded}"
        #current_app.logger.debug("QRdata = %s", qrdata)
    else:
        flash("Erro no ID")

    return render_template('qr.html', qrdata=qrdata, placa=placa)
    