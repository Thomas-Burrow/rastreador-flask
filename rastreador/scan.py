import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from rastreador.db import get_db
from rastreador.ordem import Estado
from rastreador.cargos import pode_alterar_status
from datetime import datetime
bp = Blueprint('scan', __name__,)



@bp.route('/scan/<id>', methods=('GET', 'POST'))
def scan(id):
    if not g.user:
        return redirect(url_for('auth.login'))
    if not pode_alterar_status(g.user):
        return "Falha na autorização.", 403
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado FROM ordem_servico where id=(?)', id)
    row = cur.fetchone()
    placa = row[0]
    estado_atual = row[1]
    try:
        estado_enum = Estado(estado_atual)
    except:
        estado_enum = Estado.AGUARDANDO #Não deve acontecer com o banco de dados em boa condição, mas caso aconteça...
    oficina_completa = estado_enum > Estado.OFICINA
    teste_completo = estado_enum > Estado.TESTE
    lavagem_completa = estado_enum > Estado.LAVAGEM
    if request.method == 'POST': #mude o estado com base no estado atual e a operação solicitada
        operation = request.form['operation']
        if(operation is None):
            return redirect(get_url('scan.scan', id=id))
        match estado_enum:
            case Estado.AGUARDANDO:
                match operation:
                    case "checkin-oficina":
                        update_checkin(db, id, "oficina")
                    case _:
                        flash ("Erro na operação")
            case Estado.AGUARDANDO_TESTE:
                match operation:
                    case "corrigir-oficina":
                        update_unset(db, id, "oficina_completa")
                    case "checkin-teste":
                        update_checkin(db, id, "teste")
                    case _:
                        flash("Erro na operação")
            case Estado.AGUARDANDO_LAVAGEM:
                match operation:
                    case "corrigir-teste":
                        update_unset(db, id, "teste_completo")
                    case "checkin-lavagem":
                        update_checkin(db, id, "lavagem")
                    case _:
                        flash("Erro na operação")
            case Estado.OFICINA | Estado.TESTE | Estado.LAVAGEM: #TODO: Separar oficina dos demais para lidar com as subetapas da oficina
                match operation:
                    case "checkout":
                        update_checkout(db, id, estado_atual)
                    case _:
                        flash ("Erro na operação")
            case Estado.COMPLETO:
                match operation:
                    case "corrigir-lavagem":
                        update_unset(db, id, "lavagem_completa")
                    case "marcar-retirado":
                        update_retirado(db, id)
                    case _:
                        flash ("Erro na operação")
            case _:
                flash ("Erro na operação")
            #de refresh na pagina para atualizar display
        return redirect(url_for('scan.scan', id=id))

    #mostre a pagina certa para o estado atual
    match estado_enum:
        case Estado.AGUARDANDO | Estado.AGUARDANDO_TESTE | Estado.AGUARDANDO_LAVAGEM:
            return render_template("scan/checkin.html", placa=placa, estado=estado_enum.get_msg(), oficina_completa=oficina_completa, teste_completo=teste_completo, lavagem_completa=lavagem_completa)
        case Estado.OFICINA | Estado.TESTE | Estado.LAVAGEM:
            return render_template("scan/checkout.html", placa=placa, estado=estado_enum.get_msg())
        case Estado.COMPLETO:
            return render_template("scan/completo.html", placa=placa, estado=estado_enum.get_msg())
        case Estado.RETIRADO:
            return render_template("scan/retirado.html", placa=placa, estado=estado_enum.get_msg())

            

#TODO: adicionar logging para todas estas funções do banco de dados
def update_unset(dbcon, id, alvo): #Em teoria deve não deve permitir injeção porque alvo não é diretamente entrado pelo usuario
    cur = dbcon.cursor()
    query = "UPDATE ordem_servico SET estado=(?) WHERE id=(?)"
    match alvo:
        case "oficina_completa":
            novo_estado = Estado.AGUARDANDO.value
        case "teste_completo":
            novo_estado = Estado.AGUARDANDO_TESTE.value
        case "lavagem_completa":
            novo_estado = Estado.AGUARDANDO_LAVAGEM.value
        case _:
            novo_estado = Estado.AGUARDANDO.value
            
    cur.execute(query,(novo_estado, id))
    dbcon.commit()


def update_checkin(dbcon, id, alvo):
    cur = dbcon.cursor()
    match alvo:
        case "oficina":
            cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.OFICINA.value, id))
        case "teste":
            cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.TESTE.value, id))
        case "lavagem":
            cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.LAVAGEM.value, id))
    dbcon.commit()

def update_checkout(dbcon, id, alvo):
    cur = dbcon.cursor()
    match alvo:
        case Estado.OFICINA.value:
            cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.AGUARDANDO_TESTE.value, id))
        case Estado.TESTE.value:
            cur.execute("UPDATE ordem_servico SET estado=(?),teste_completo=1 WHERE id=(?)", (Estado.AGUARDANDO_LAVAGEM.value, id))
        case Estado.LAVAGEM.value:
            cur.execute("UPDATE ordem_servico SET estado=(?),lavagem_completa=1 WHERE id=(?)", (Estado.COMPLETO.value, id))
    dbcon.commit()


def update_completo(dbcon,id):
    cur = dbcon.cursor()
    cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.COMPLETO.value, id))
    dbcon.commit()

def update_retirado(dbcon,id):
    cur = dbcon.cursor()
    cur.execute("UPDATE ordem_servico SET estado=(?),retirado_em=(?) WHERE id=(?)", (Estado.RETIRADO.value, datetime.now(), id))
    dbcon.commit()


class Veiculo:
    def __init__(self,placa,status,id):
        self.placa = placa
        self.status = status
        self.id = id

    def get_class_for_status(self):
        match self.status:
            case Estado.AGUARDANDO.value:
                return "status-aguardando"
            case Estado.OFICINA.value:
                return "status-servico"
            case Estado.TESTE.value:
                return "status-teste"
            case Estado.LAVAGEM.value:
                return "status-lavagem"
            case Estado.COMPLETO.value:
                return "status-pronto"
            case _:
                return "status-chegada"
            

@bp.route('/dash')
def dash():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, id FROM ordem_servico WHERE estado <> "Retirado"' ) #TODO: mostrar retirados recentes, mas não aqueles retirados muito antes
    allrows = cur.fetchall()
    veiculos = [Veiculo(row[0],row[1],row[2]) for row in allrows]
    return render_template("dash.html", veiculos=veiculos)
