import pytest


from sorvgest.domain.model import (
    Preco,
    Sabor,
    Pedido,
    ItemPedido,
    StatusPedido,
    EstoqueInsuficiente,
    PedidoNaoPodeSerCancelado,
    PedidoNaoPodeSerFinalizado,
    ItemInvalido,
)
#Teste de Preco
def test_preco_valido():
    preco = Preco(150)
    assert preco.centavos == 150
    assert preco.reais == 1.5

def test_preco_zero_valido():
    preco = Preco(0)
    assert preco.centavos == 0

def test_preco_negativo_levanta_erro():
    with pytest.raises(ValueError):
        Preco(-100)

def test_soma_precos():
    p1 = Preco(100)
    p2 = Preco(200)
    assert p1 + p2 == Preco(300)

def test_multiplicacao_preco_por_quantidade():
    preco = Preco(100)
    quantidade = 3
    assert preco * quantidade == Preco(300)

def test_multiplicacao_preco_por_quantidade_negativa_levanta_erro():
    preco = Preco(100)
    with pytest.raises(ValueError):
        preco * -2

def test_preco_multiplicado_por_zero():
    preco = Preco(100)
    assert preco * 0 == Preco(0)

def test_dois_precos_iguais_sao_iguais():
    p1 = Preco(100)
    p2 = Preco(100)
    assert p1 == p2

def test_dois_precos_diferentes_nao_sao_iguais():
    p1 = Preco(100)
    p2 = Preco(200)
    assert p1 != p2

#Teste de Sabor
def test_sabor_valido():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    assert sabor.referencia == "REF001"
    assert sabor.nome == "Chocolate"
    assert sabor.preco_reais == 250
    assert sabor.quantidade_estoque == 10

def test_sabor_sem_referencia_levanta_erro():
    with pytest.raises(ValueError):
        Sabor("", "Chocolate", Preco(250), 10)

def test_sabor_sem_nome_levanta_erro():
    with pytest.raises(ValueError):
        Sabor("REF001", "", Preco(250), 10)

def test_baixar_estoque_normal():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    sabor.baixar_estoque(5)
    assert sabor.quantidade_estoque == 5

def test_baixar_estoque_zero_levanta_erro():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    with pytest.raises(EstoqueInsuficiente):
        sabor.baixar_estoque(0)

def test_baixar_estoque_insuficiente_levanta_erro():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    with pytest.raises(EstoqueInsuficiente):
        sabor.baixar_estoque(15)

def test_repor_estoque_normal():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    sabor.repor_estoque(5)
    assert sabor.quantidade_estoque == 15

def test_repor_estoque_negativa_levanta_erro():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    with pytest.raises(ValueError):
        sabor.repor_estoque(-5)

def test_repor_estoque_zero_levanta_erro():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    with pytest.raises(ValueError):
        sabor.repor_estoque(0)

#Testes de Pedido e ItemPedido

def test_pedido_com_dois_itens():
    sabor1 = Sabor("REF001", "Chocolate", Preco(250), 10)
    sabor2 = Sabor("REF002", "Baunilha", Preco(200), 5)
    pedido = Pedido()
    pedido.adicionar_item(sabor1, 2)
    pedido.adicionar_item(sabor2, 1)
    assert len(pedido.itens) == 2
    assert pedido.total == Preco(700)  # 2*250 + 1*200 = 700

def test_pedido_sem_itens_total_zero():
    pedido = Pedido()
    assert pedido.total == Preco(0)


def test_nao_aceita_sabor_duplicado_no_pedido():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    pedido = Pedido()
    pedido.adicionar_item(sabor, 2)
    with pytest.raises(ItemInvalido):
        pedido.adicionar_item(sabor, 1)  # Tentativa de adicionar o mesmo sabor novamente

def test_estoque_nao_muda_se_um_item_falhar():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    pedido = Pedido()
    pedido.adicionar_item(sabor, 5)  # Estoque agora é 5
    with pytest.raises(EstoqueInsuficiente):
        pedido.finalizar()
    assert sabor.quantidade_estoque == 5  # Estoque não deve ter mudado

def test_nao_aceita_quantidade_zero_no_item():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    pedido = Pedido()
    with pytest.raises(ItemInvalido):
        pedido.adicionar_item(sabor, 0)  # Tentativa de adicionar quantidade zero

def test_finalizar_pedido_debita_estoque():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 10)
    pedido = Pedido()
    pedido.adicionar_item(sabor, 2)
    pedido.finalizar()
    assert sabor.quantidade_estoque == 8
    
def test_finalizar_pedido_sem_itens_levanta_erro():
    pedido = Pedido()
    with pytest.raises(PedidoNaoPodeSerFinalizado):
        pedido.finalizar()

def test_finalizar_pedido_com_estoque_insuficiente():
    sabor = Sabor("REF001", "Chocolate", Preco(250), 1)
    pedido = Pedido()
    pedido.adicionar_item(sabor, 2)  # Tentativa de adicionar mais do que o estoque
    with pytest.raises(EstoqueInsuficiente):
        pedido.finalizar()
    assert sabor.quantidade_estoque == 1  # Estoque não deve ter mudado
