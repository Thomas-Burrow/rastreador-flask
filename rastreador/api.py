import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, jsonify, session, url_for, current_app
)
import qrcode
import base64
from enum import Enum
from io import BytesIO
from rastreador.db import get_db
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validate
from rastreador.ordem import Estado
from rastreador.scan import Veiculo

#TODO: falar com grupo do banco de dados para criar um campo com chave de API para usuario
#   com intuito de permitir operações que modificam o estado sejam associadas com um usuario

#ver https://flask-marshmallow.readthedocs.io/en/latest/ para mais informações

bp = Blueprint('api', __name__, url_prefix='/api')
ma = Marshmallow(bp) # Initialize Flask-Marshmallow

class VeiculoSchema(ma.Schema):
    placa = fields.Str(required=True)
    status = fields.Str(required=True)
    id = fields.Int(required=True)

#Semelhante ao dashboard, mas JSON
@bp.route('/veiculos', methods=['GET'])
def get_veiculos():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, id FROM ordem_servico WHERE estado <> "Retirado"' )
    allrows = cur.fetchall()
    veiculos = [Veiculo(row[0],row[1],row[2]) for row in allrows]
    veiculo_schema = VeiculoSchema(many=True)
    result = veiculo_schema.dump(veiculos)
    return jsonify(result)

@bp.route('/veiculo/por_placa/<placa>', methods=['GET'])
def get_veiculo_por_placa(placa):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, id FROM ordem_servico WHERE placa = (?) COLLATE NOCASE ORDER BY id DESC', (placa,))
    row = cur.fetchone()
    if row is None:
        return "{}\n", 404
    veiculo = Veiculo(row[0],row[1],row[2])
    veiculo_schema = VeiculoSchema()
    result = veiculo_schema.dump(veiculo)
    return jsonify(result)

@bp.route('/veiculo/por_id/<id>', methods=['GET'])
def get_veiculo_por_id(id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT placa, estado, id FROM ordem_servico WHERE id = (?)', id)
    row = cur.fetchone()
    if row is None:
        return "{}\n", 404
    veiculo = Veiculo(row[0],row[1],row[2])
    veiculo_schema = VeiculoSchema()
    result = veiculo_schema.dump(veiculo)
    return jsonify(result)