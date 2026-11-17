import pytest

from sorvgest.domain.model import (
    ItemInvalido,
    Pedido,
    PedidoAberto,
    PedidoCancelado,
    PedidoFinalizado,
    PedidoNaoPodeSerCancelado,
    PedidoNaoPodeSerFinalizado,
    Preco,
    Sabor,
    StatusPedido,
)


def _sabor(estoque=10):
    return Sabor("CHOC", "Chocolate", Preco(800), estoque)


def _pedido_finalizado():
    pedido = Pedido()
    pedido.adicionar_item(_sabor(), 1)
    pedido.finalizar()
    return pedido


def _pedido_cancelado():
    pedido = Pedido()
    pedido.cancelar()
    return pedido


def test_pedido_novo_comeca_no_estado_aberto():
    assert isinstance(Pedido().estado, PedidoAberto)


def test_finalizar_leva_ao_estado_finalizado():
    pedido = _pedido_finalizado()

    assert isinstance(pedido.estado, PedidoFinalizado)
    assert pedido.status == StatusPedido.FINALIZADO


def test_cancelar_leva_ao_estado_cancelado():
    pedido = _pedido_cancelado()

    assert isinstance(pedido.estado, PedidoCancelado)
    assert pedido.status == StatusPedido.CANCELADO


@pytest.mark.parametrize("criar_pedido", [_pedido_finalizado, _pedido_cancelado])
def test_estados_encerrados_bloqueiam_todas_as_operacoes(criar_pedido):
    pedido = criar_pedido()

    with pytest.raises(PedidoNaoPodeSerFinalizado):
        pedido.adicionar_item(Sabor("MOR", "Morango", Preco(700), 5), 1)
    with pytest.raises(PedidoNaoPodeSerFinalizado):
        pedido.finalizar()
    with pytest.raises(PedidoNaoPodeSerCancelado):
        pedido.cancelar()


def test_estado_aberto_ainda_valida_os_itens():
    pedido = Pedido()

    with pytest.raises(ItemInvalido):
        pedido.adicionar_item(_sabor(), 0)


def test_estado_e_derivado_do_status_persistido():
    pedido = Pedido()
    pedido.status = StatusPedido.FINALIZADO  # como se viesse do banco

    assert isinstance(pedido.estado, PedidoFinalizado)


def test_estados_sao_compartilhados_entre_pedidos():
    assert Pedido().estado is Pedido().estado