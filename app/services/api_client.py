import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "paciente",
    "cpf",
    "medico",
    "especialidade",
    "data",
    "horario",
    "convenio",
    "status",
]


class ApiUnavailableError(Exception):
    """A API não respondeu (timeout, conexão recusada ou erro HTTP)."""


class ApiInvalidResponseError(Exception):
    """A API respondeu, mas o corpo é vazio, malformado ou inesperado."""


def get_agendamentos():
    """Busca os agendamentos na API (real ou mockada) via HTTP.

    Retorna uma tupla (agendamentos_validos, aviso).

    `aviso` é preenchido quando registros com campos obrigatórios ausentes
    foram descartados, para que o usuário seja informado sem que a
    aplicação quebre.
    """
    base_url = current_app.config["API_BASE_URL"]
    timeout = current_app.config["API_TIMEOUT"]
    url = f"{base_url}/api/agendamentos"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar a API de agendamentos em %s.", url)
        raise ApiUnavailableError("timeout") from None
    except requests.exceptions.ConnectionError:
        logger.error("Falha de conexão ao consultar a API de agendamentos em %s.", url)
        raise ApiUnavailableError("connection_error") from None
    except requests.exceptions.HTTPError as exc:
        logger.error("A API de agendamentos retornou um erro HTTP: %s", exc)
        raise ApiUnavailableError("http_error") from None

    try:
        payload = response.json()
    except ValueError:
        # Cenário: resposta vazia ou inválida da API.
        logger.error("A API de agendamentos retornou um corpo que não é um JSON válido.")
        raise ApiInvalidResponseError("not_json") from None

    dados = payload.get("dados") if isinstance(payload, dict) else payload
    if dados is None:
        logger.error("A resposta da API não contém a chave 'dados' esperada.")
        raise ApiInvalidResponseError("missing_key")

    if not isinstance(dados, list):
        logger.error("A chave 'dados' da resposta da API não é uma lista.")
        raise ApiInvalidResponseError("not_a_list")

    validos = []
    descartados = 0
    for item in dados:
        # Cenário: campos obrigatórios ausentes na resposta recebida.
        if isinstance(item, dict) and all(item.get(campo) not in (None, "") for campo in REQUIRED_FIELDS):
            validos.append({campo: item[campo] for campo in REQUIRED_FIELDS})
        else:
            descartados += 1
            logger.warning("Registro descartado por conter campos obrigatórios ausentes: %r", item)

    aviso = None
    if descartados:
        aviso = f"{descartados} registro(s) foram ignorados por estarem incompletos."

    return validos, aviso
