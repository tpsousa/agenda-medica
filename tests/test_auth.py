from tests.conftest import login


def test_login_com_credenciais_validas_redireciona_para_agenda(client):
    response = login(client, "admin", "admin123")

    assert response.status_code == 200
    assert response.request.path == "/agenda/"


def test_login_com_credenciais_invalidas_exibe_mensagem_clara(client):
    response = login(client, "admin", "senha-errada")

    assert response.status_code == 200
    assert response.request.path == "/auth/login"
    assert "inválidos" in response.get_data(as_text=True)


def test_login_com_campos_vazios_nao_quebra_a_aplicacao(client):
    response = client.post("/auth/login", data={"identifier": "", "password": ""})

    assert response.status_code == 200
    assert "usuário/e-mail e senha" in response.get_data(as_text=True).lower()
