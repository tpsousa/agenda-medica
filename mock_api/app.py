"""Serviço mockado de agendamentos, consumido pela aplicação principal via HTTP.

Endpoint: GET /api/agendamentos

Aceita o parâmetro opcional ?simulate= para reproduzir manualmente os
cenários de falha exigidos no desafio:
  - simulate=empty    -> retorna lista vazia (nenhum agendamento encontrado)
  - simulate=invalid  -> retorna um corpo que não é um JSON válido
  - simulate=missing  -> retorna registros com campos obrigatórios ausentes
  - simulate=error    -> retorna HTTP 500 (indisponibilidade da API)
"""
import logging

from flask import Flask, Response, jsonify, request

from data import AGENDAMENTOS

logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/api/agendamentos")
def agendamentos():
    simulate = request.args.get("simulate")

    if simulate == "error":
        logger.warning("Simulando indisponibilidade da API (HTTP 500).")
        return jsonify({"mensagem": "erro interno simulado"}), 500

    if simulate == "empty":
        logger.info("Simulando resposta sem agendamentos.")
        return jsonify({"dados": []})

    if simulate == "invalid":
        logger.info("Simulando resposta com corpo inválido.")
        return Response("isto nao e um json valido", mimetype="application/json")

    if simulate == "missing":
        logger.info("Simulando registros com campos obrigatórios ausentes.")
        incompletos = [{**item, "cpf": ""} for item in AGENDAMENTOS]
        return jsonify({"dados": incompletos})

    return jsonify({"dados": AGENDAMENTOS})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
