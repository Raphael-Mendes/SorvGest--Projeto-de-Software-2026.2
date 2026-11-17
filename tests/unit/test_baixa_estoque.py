import pytest

from sorvgest.domain.model import (
    BaixaDeEstoque,
    BaixaNoSabor,
    EstoqueInsuficiente,
    ItemPedido,
    Pedido,
    Preco,
    Sabor,
    StatusPedido,
)


class BaixaQueRegistra(BaixaDeEstoque):
    """Dublê de teste: só anota quais itens recebeu."""

    def __init__(self):
        self.itens_recebidos = None

    def baixar(self, itens):
        self.itens_recebidos = list(itens)


class BaixaQueFalha(BaixaDeEstoque):
    def baixar(self, itens):
        raise EstoqueInsuficiente("sem estoque")


def _pedido_com_chocolate(quantidade=2, estoque=10):
    sabor = Sabor("CHOC", "Chocolate", Preco(800), estoque)
    pedido = Pedido()
    pedido.adicionar_item(sabor, quantidade)
    return pedido, sabor


def test_pedido_delega_a_baixa_para_a_politica_recebida():
    pedido, sabor = _pedido_com_chocolate()
    baixa = BaixaQueRegistra()

    pedido.finalizar(baixa)

    assert [item.sabor.referencia for item in baixa.itens_recebidos] == ["CHOC"]
    assert sabor.quantidade_estoque == 10  # o Pedido não mexeu no estoque sozinho
    assert pedido.status == StatusPedido.FINALIZADO


def test_falha_na_baixa_mantem_o_pedido_aberto():
    pedido, _ = _pedido_com_chocolate()

    with pytest.raises(EstoqueInsuficiente):
        pedido.finalizar(BaixaQueFalha())

    assert pedido.status == StatusPedido.ABERTO


def test_baixa_no_sabor_e_tudo_ou_nada():
    choc = Sabor("CHOC", "Chocolate", Preco(800), 10)
    morango = Sabor("MOR", "Morango", Preco(700), 1)
    itens = [ItemPedido(choc, 2), ItemPedido(morango, 5)]

    with pytest.raises(EstoqueInsuficiente):
        BaixaNoSabor().baixar(itens)

    assert choc.quantidade_estoque == 10
    assert morango.quantidade_estoque == 1


def test_sabor_informa_se_tem_estoque():
    sabor = Sabor("CHOC", "Chocolate", Preco(800), 3)

    assert sabor.tem_estoque_para(3)
    assert not sabor.tem_estoque_para(4)