"""Casos de uso do SorvGest. Orquestram o domínio e os repositórios."""

from sorvgest.domain.model import Cliente, ContaFidelidade, Pedido, Preco, Sabor


class SaborNaoEncontrado(Exception):
    pass


class PedidoNaoEncontrado(Exception):
    pass


class ClienteNaoEncontrado(Exception):
    pass


class JaCadastrado(Exception):
    pass


# --- Sabores -----------------------------------------------------------------

def cadastrar_sabor(referencia, nome, preco_centavos, quantidade_estoque, sabores, session):
    if sabores.get(referencia) is not None:
        raise JaCadastrado(f"Sabor {referencia} ja cadastrado.")
    sabores.add(Sabor(referencia, nome, Preco(preco_centavos), quantidade_estoque))
    session.commit()


def repor_estoque(referencia, quantidade, sabores, session):
    sabor = sabores.get(referencia)
    if sabor is None:
        raise SaborNaoEncontrado(f"Sabor {referencia} nao encontrado.")
    sabor.repor_estoque(quantidade)
    session.commit()


# --- Pedidos -----------------------------------------------------------------

def criar_pedido(pedido_id, cliente_id, pedidos, session):
    if pedidos.get(pedido_id) is not None:
        raise JaCadastrado(f"Pedido {pedido_id} ja existe.")
    pedidos.add(Pedido(cliente_id=cliente_id, pedido_id=pedido_id))
    session.commit()


def adicionar_item(pedido_id, referencia_sabor, quantidade, pedidos, sabores, session):
    pedido = _buscar_pedido(pedido_id, pedidos)
    sabor = sabores.get(referencia_sabor)
    if sabor is None:
        raise SaborNaoEncontrado(f"Sabor {referencia_sabor} nao encontrado.")
    pedido.adicionar_item(sabor, quantidade)
    session.commit()


def finalizar_pedido(pedido_id, pedidos, contas, session):
    """Finaliza o pedido e credita pontos de fidelidade: 1 ponto por real inteiro."""
    pedido = _buscar_pedido(pedido_id, pedidos)
    pedido.finalizar()

    if pedido.cliente_id is not None:
        conta = contas.get(pedido.cliente_id)
        pontos = pedido.total.centavos // 100
        if conta is not None and pontos > 0:
            conta.acumular(pontos)

    session.commit()
    return pedido.total.centavos


def cancelar_pedido(pedido_id, pedidos, session):
    pedido = _buscar_pedido(pedido_id, pedidos)
    pedido.cancelar()
    session.commit()


def _buscar_pedido(pedido_id, pedidos):
    pedido = pedidos.get(pedido_id)
    if pedido is None:
        raise PedidoNaoEncontrado(f"Pedido {pedido_id} nao encontrado.")
    return pedido


# --- Clientes e fidelidade ---------------------------------------------------

def cadastrar_cliente(cliente_id, nome, clientes, contas, session):
    """Cadastra o cliente e já abre sua conta de fidelidade com saldo zero."""
    if clientes.get(cliente_id) is not None:
        raise JaCadastrado(f"Cliente {cliente_id} ja cadastrado.")
    clientes.add(Cliente(cliente_id, nome))
    contas.add(ContaFidelidade(cliente_id))
    session.commit()


def resgatar_pontos(cliente_id, pontos, contas, session):
    conta = contas.get(cliente_id)
    if conta is None:
        raise ClienteNaoEncontrado(f"Cliente {cliente_id} nao encontrado.")
    conta.resgatar(pontos)
    session.commit()
    return conta.saldo