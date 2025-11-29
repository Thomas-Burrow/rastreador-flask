import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
from rastreador.db import get_db, placa_e_estado, veiculos_pendentes
from rastreador.models import Estado, Veiculo
from rastreador.cargos import pode_alterar_status
from datetime import datetime

bp = Blueprint(
    "scan",
    __name__,
)


@bp.route("/scan/<id>", methods=("GET", "POST"))
def scan(id):
    if not g.user:
        return redirect(url_for("auth.login"))
    if not pode_alterar_status(g.user):
        return "Falha na autorização.", 403
    (placa, estado_enum) = placa_e_estado(id)
    estado_atual = estado_enum.value
    oficina_completa = estado_enum > Estado.OFICINA
    teste_completo = estado_enum > Estado.TESTE
    lavagem_completa = estado_enum > Estado.LAVAGEM
    db = get_db()

    if (
        request.method == "POST"
    ):  # mude o estado com base no estado atual e a operação solicitada
        operation = request.form["operation"]
        if operation is None:
            return redirect(get_url("scan.scan", id=id))
        match estado_enum:
            case Estado.AGUARDANDO:
                match operation:
                    case "checkin-oficina":
                        update_checkin(db, id, "oficina")
                    case _:
                        flash("Erro na operação")
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
            case (
                Estado.OFICINA | Estado.TESTE | Estado.LAVAGEM
            ):  # TODO: Separar oficina dos demais para lidar com as subetapas da oficina
                match operation:
                    case "checkout":
                        update_checkout(db, id, estado_atual)
                    case _:
                        flash("Erro na operação")
            case Estado.COMPLETO:
                match operation:
                    case "corrigir-lavagem":
                        update_unset(db, id, "lavagem_completa")
                    case "marcar-retirado":
                        update_retirado(db, id)
                    case _:
                        flash("Erro na operação")
            case _:
                flash("Erro na operação")
            # de refresh na pagina para atualizar display
        return redirect(url_for("scan.scan", id=id))

    # mostre a pagina certa para o estado atual
    match estado_enum:
        case Estado.AGUARDANDO | Estado.AGUARDANDO_TESTE | Estado.AGUARDANDO_LAVAGEM:
            return render_template(
                "scan/checkin.html",
                placa=placa,
                estado=estado_enum.get_msg(),
                oficina_completa=oficina_completa,
                teste_completo=teste_completo,
                lavagem_completa=lavagem_completa,
            )
        case Estado.OFICINA | Estado.TESTE | Estado.LAVAGEM:
            return render_template(
                "scan/checkout.html", placa=placa, estado=estado_enum.get_msg()
            )
        case Estado.COMPLETO:
            return render_template(
                "scan/completo.html", placa=placa, estado=estado_enum.get_msg()
            )
        case Estado.RETIRADO:
            return render_template(
                "scan/retirado.html", placa=placa, estado=estado_enum.get_msg()
            )


# TODO: adicionar logging para todas estas funções do banco de dados
def update_unset(
    dbcon, id, alvo
):  # Em teoria deve não deve permitir injeção porque alvo não é diretamente entrado pelo usuario
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

    cur.execute(query, (novo_estado, id))
    dbcon.commit()


def update_checkin(dbcon, id, alvo):
    cur = dbcon.cursor()
    match alvo:
        case "oficina":
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.OFICINA.value, id),
            )
        case "teste":
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.TESTE.value, id),
            )
        case "lavagem":
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.LAVAGEM.value, id),
            )
    dbcon.commit()


def update_checkout(dbcon, id, alvo):
    cur = dbcon.cursor()
    match alvo:
        case Estado.OFICINA.value:
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.AGUARDANDO_TESTE.value, id),
            )
        case Estado.TESTE.value:
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.AGUARDANDO_LAVAGEM.value, id),
            )
        case Estado.LAVAGEM.value:
            cur.execute(
                "UPDATE ordem_servico SET estado=(?) WHERE id=(?)",
                (Estado.COMPLETO.value, id),
            )
    dbcon.commit()


def update_completo(dbcon, id):
    cur = dbcon.cursor()
    cur.execute(
        "UPDATE ordem_servico SET estado=(?) WHERE id=(?)", (Estado.COMPLETO.value, id)
    )
    dbcon.commit()


def update_retirado(dbcon, id):
    cur = dbcon.cursor()
    cur.execute(
        "UPDATE ordem_servico SET estado=(?),retirado_em=(?) WHERE id=(?)",
        (Estado.RETIRADO.value, datetime.now(), id),
    )
    dbcon.commit()


@bp.route("/dash")
def dash():
    veiculos = veiculos_pendentes()
    return render_template("dash.html", veiculos=veiculos)
