from unittest.mock import Mock, patch

import requests

from tests.conftest import login


def _mock_response(dados):
    return Mock(status_code=200, json=lambda: {"dados": dados}, raise_for_status=lambda: None)


@patch("app.services.api_client.requests.get")
def test_agenda_retorna_agendamentos_quando_api_responde_normalmente(mock_get, client):
    mock_get.return_value = _mock_response([
        {
            "paciente": "Maria Silva",
            "cpf": "111.111.111-11",
            "medico": "Dr. João",
            "especialidade": "Clínico Geral",
            "data": "2026-08-01",
            "horario": "09:00",
            "convenio": "Unimed",
            "status": "confirmado",
        }
    ])
    login(client)

    response = client.get("/agenda/api/agendamentos")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["dados"]) == 1
    assert body["dados"][0]["paciente"] == "Maria Silva"


@patch("app.services.api_client.requests.get")
def test_agenda_informa_indisponibilidade_quando_api_esta_fora_do_ar(mock_get, client):
    mock_get.side_effect = requests.exceptions.ConnectionError()
    login(client)

    response = client.get("/agenda/api/agendamentos")

    assert response.status_code == 503
    assert "indisponível" in response.get_json()["mensagem"]


@patch("app.services.api_client.requests.get")
def test_busca_sem_correspondencia_informa_nenhum_registro_encontrado(mock_get, client):
    mock_get.return_value = _mock_response([
        {
            "paciente": "Maria Silva",
            "cpf": "111.111.111-11",
            "medico": "Dr. João",
            "especialidade": "Clínico Geral",
            "data": "2026-08-01",
            "horario": "09:00",
            "convenio": "Unimed",
            "status": "confirmado",
        }
    ])
    login(client)

    response = client.get("/agenda/api/agendamentos?q=paciente-que-nao-existe")

    assert response.status_code == 200
    body = response.get_json()
    assert body["dados"] == []
    assert "Nenhum registro encontrado" in body["aviso"]


def test_agenda_redireciona_para_login_quando_usuario_nao_autenticado(client):
    response = client.get("/agenda/", follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/auth/login"
