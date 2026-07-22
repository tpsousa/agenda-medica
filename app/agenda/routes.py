import logging
from functools import wraps

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.services.api_client import ApiInvalidResponseError, ApiUnavailableError, get_agendamentos

logger = logging.getLogger(__name__)
bp = Blueprint("agenda", __name__, url_prefix="/agenda")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@bp.route("/")
@login_required
def index():
    return render_template("agenda.html")


@bp.route("/api/agendamentos")
@login_required
def api_agendamentos():
    """Endpoint interno consumido pela tabela (Tabulator) via fetch/ajax."""
    termo = request.args.get("q", "").strip()

    try:
        agendamentos, aviso = get_agendamentos()
    except ApiUnavailableError:
        # Cenário: indisponibilidade temporária da API.
        return jsonify({
            "mensagem": "O serviço de agendamentos está indisponível no momento. Tente novamente em instantes."
        }), 503
    except ApiInvalidResponseError:
        # Cenário: resposta vazia ou inválida da API.
        return jsonify({
            "mensagem": "Não foi possível interpretar os dados recebidos da API de agendamentos."
        }), 502

    if termo:
        # Cenário: busca por paciente, CPF ou médico; entradas tratadas sem erro.
        alvo = termo.lower()
        agendamentos = [
            item for item in agendamentos
            if alvo in item["paciente"].lower()
            or alvo in item["cpf"].lower()
            or alvo in item["medico"].lower()
        ]
        if not agendamentos:
            return jsonify({"dados": [], "aviso": "Nenhum registro encontrado para o termo informado."})

    payload = {"dados": agendamentos}
    if aviso:
        payload["aviso"] = aviso
    return jsonify(payload)
