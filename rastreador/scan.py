import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from rastreador.db import get_db
from rastreador.ordem import Estado
#TODO: require auth
bp = Blueprint('scan', __name__,)

@bp.route('/scan/<id>', methods=('GET', 'POST'))
def scan(id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, oficina_completa, teste_completo, lavagem_completa FROM ordem_servico where id=(?)', id)
    row = cur.fetchone()
    placa = row[0]
    estado_atual = row[1]
    oficina_completa = row[2]
    teste_completo = row[3]
    lavagem_completa = row[4]
    estado_enum = Estado(estado_atual)
    pode_completar = oficina_completa and teste_completo and lavagem_completa
    if request.method == 'POST': #mude o estado com base no estado atual e a operação solicitada
        operation = request.form['operation']
        if(operation is None):
            return redirect(get_url('scan.scan', id=id))
        match estado_atual:
            case Estado.AGUARDANDO.value: #TODO: Determinar se veiculo pode ser consertado, testado e lavado em qualquer order ou se tem uma ordem fixa para essas operações para refinar os estados
                match operation: #TODO: mover estes strings para um enum, para prevenir erros de digitação
                    case "corrigir-lavagem": #teoricamente esses 3 comandos não fazem nada se o bool não está setado então não checamos com um if
                        update_unset(db, id, "lavagem_completa")
                    case "corrigir-teste":
                        update_unset(db, id, "teste_completo")
                    case "corrigir-oficina":
                        update_unset(db, id, "oficina_completa")
                    case "checkin-oficina":
                        update_checkin(db, id, "oficina")
                    case "checkin-teste":
                        update_checkin(db, id, "teste")
                    case "checkin-lavagem":
                        update_checkin(db, id, "lavagem")
                    case "marcar-completo":
                        if pode_completar: #esse sim precisa de checagem
                            update_completo(db, id)
                    case _:
                        flash ("Erro na operação")
            case Estado.OFICINA.value | Estado.TESTE.value | Estado.LAVAGEM.value:
                match operation:
                    case "checkout":
                        update_checkout(db, id, estado_atual)
                    case _:
                        flash ("Erro na operação")
            case Estado.COMPLETO.value:
                match operation:
                    case "marcar-retirado":
                        update_retirado(db, id)
                    case _:
                        flash ("Erro na operação")
            case _:
                flash ("Erro na operação")
            #de refresh na pagina para atualizar display
        return redirect(url_for('scan.scan', id=id))

    #mostre a pagina certa para o estado atual
    match estado_atual:
        case Estado.AGUARDANDO.value:
            return render_template("scan/checkin.html", placa=placa, estado=estado_enum.get_msg(), oficina_completa=oficina_completa, teste_completo=teste_completo, lavagem_completa=lavagem_completa, pode_completar=pode_completar)
        case Estado.OFICINA.value | Estado.TESTE.value | Estado.LAVAGEM.value:
            return render_template("scan/checkout.html", placa=placa, estado=estado_enum.get_msg())
        case Estado.COMPLETO.value:
            return render_template("scan/completo.html", placa=placa, estado=estado_enum.get_msg())
        case Estado.RETIRADO.value:
            return render_template("scan/retirado.html", placa=placa, estado=estado_enum.get_msg())
        case _:
            return render_template("scan.html")
            

#TODO: adicionar logging para todas estas funções do banco de dados
def update_unset(dbcon, id, alvo): #Em teoria deve não deve permitir injeção porque alvo não é diretamente entrado pelo usuario
    cur = dbcon.cursor()
    query = f"UPDATE ordem_servico SET {alvo}=0 WHERE id=(?)"
    cur.execute(query,(id))
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
            cur.execute("UPDATE ordem_servico SET estado=(?),oficina_completa=1 WHERE id=(?)", (Estado.AGUARDANDO.value, id))
        case Estado.TESTE.value:
            cur.execute("UPDATE ordem_servico SET estado=(?),teste_completo=1 WHERE id=(?)", (Estado.AGUARDANDO.value, id))
        case Estado.LAVAGEM.value:
            cur.execute("UPDATE ordem_servico SET estado=(?),lavagem_completa=1 WHERE id=(?)", (Estado.AGUARDANDO.value, id))
    dbcon.commit()


def update_completo(dbcon,id):
    cur = dbcon.cursor()
    cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.COMPLETO.value, id))
    dbcon.commit()

def update_retirado(dbcon,id):
    cur = dbcon.cursor()
    cur.execute("UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.RETIRADO.value, id))
    dbcon.commit()


class Veiculo:
    def __init__(self,placa,status,id):
        self.placa = placa
        self.status = status
        self.id = id


@bp.route('/dash')
def dash():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, id FROM ordem_servico WHERE estado <> "Retirado"' ) #TODO: mostrar retirados recentes, mas não aqueles retirados muito antes
    allrows = cur.fetchall()
    veiculos = [Veiculo(row[0],row[1],row[2]) for row in allrows]
    return render_template("dash.html", veiculos=veiculos)
