import pytest

from sorvgest.entrypoints.flask_app import create_app


@pytest.fixture
def client(session_factory):
    app = create_app(session_factory)
    return app.test_client()


def test_fluxo_completo_de_pedido_com_fidelidade(client):
    assert client.post("/clientes", json={"cliente_id": "C1", "nome": "Ana"}).status_code == 201
    assert client.post(
        "/sabores",
        json={"referencia": "CHOC", "nome": "Chocolate", "preco_centavos": 800, "quantidade_estoque": 10},
    ).status_code == 201
    assert client.post("/pedidos", json={"pedido_id": "P1", "cliente_id": "C1"}).status_code == 201
    assert client.post(
        "/pedidos/P1/itens", json={"referencia_sabor": "CHOC", "quantidade": 2}
    ).status_code == 204

    resposta = client.post("/pedidos/P1/finalizar")

    assert resposta.status_code == 200
    assert resposta.json["total_centavos"] == 1600

    resgate = client.post("/clientes/C1/resgates", json={"pontos": 10})
    assert resgate.status_code == 200
    assert resgate.json["saldo"] == 6


def test_finalizar_sem_estoque_retorna_400(client):
    client.post(
        "/sabores",
        json={"referencia": "CHOC", "nome": "Chocolate", "preco_centavos": 800, "quantidade_estoque": 1},
    )
    client.post("/pedidos", json={"pedido_id": "P1"})
    client.post("/pedidos/P1/itens", json={"referencia_sabor": "CHOC", "quantidade": 5})

    resposta = client.post("/pedidos/P1/finalizar")

    assert resposta.status_code == 400
    assert "Estoque insuficiente" in resposta.json["erro"]


def test_pedido_inexistente_retorna_404(client):
    resposta = client.post("/pedidos/NAO-EXISTE/cancelar")

    assert resposta.status_code == 404


def test_rota_inexistente_retorna_404(client):
    assert client.get("/nada").status_code == 404