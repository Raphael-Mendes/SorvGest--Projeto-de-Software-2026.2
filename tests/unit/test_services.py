import pytest

from sorvgest.adapters.repository import (
    FakeClienteRepository,
    FakeContaFidelidadeRepository,
    FakePedidoRepository,
    FakeSaborRepository,
)
from sorvgest.domain.model import (
    EstoqueInsuficiente,
    PedidoNaoPodeSerCancelado,
    SaldoInsuficiente,
    StatusPedido,
)
from sorvgest.service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


@pytest.fixture
def repos():
    return {
        "sabores": FakeSaborRepository(),
        "pedidos": FakePedidoRepository(),
        "clientes": FakeClienteRepository(),
        "contas": FakeContaFidelidadeRepository(),
    }


def _pedido_com_item(repos, session, quantidade=2, estoque=10, cliente_id="C1"):
    services.cadastrar_sabor("CHOC", "Chocolate", 800, estoque, repos["sabores"], session)
    services.criar_pedido("P1", cliente_id, repos["pedidos"], session)
    services.adicionar_item("P1", "CHOC", quantidade, repos["pedidos"], repos["sabores"], session)


def test_cadastrar_sabor_salva_e_faz_commit(repos):
    session = FakeSession()

    services.cadastrar_sabor("CHOC", "Chocolate", 800, 10, repos["sabores"], session)

    assert repos["sabores"].get("CHOC").nome == "Chocolate"
    assert session.committed


def test_cadastrar_sabor_duplicado_e_bloqueado(repos):
    session = FakeSession()
    services.cadastrar_sabor("CHOC", "Chocolate", 800, 10, repos["sabores"], session)

    with pytest.raises(services.JaCadastrado):
        services.cadastrar_sabor("CHOC", "Outro", 900, 1, repos["sabores"], session)


def test_repor_estoque_de_sabor_inexistente(repos):
    with pytest.raises(services.SaborNaoEncontrado):
        services.repor_estoque("NADA", 5, repos["sabores"], FakeSession())


def test_repor_estoque_soma_quantidade(repos):
    session = FakeSession()
    services.cadastrar_sabor("CHOC", "Chocolate", 800, 10, repos["sabores"], session)

    services.repor_estoque("CHOC", 5, repos["sabores"], session)

    assert repos["sabores"].get("CHOC").quantidade_estoque == 15


def test_adicionar_item_em_pedido_inexistente(repos):
    with pytest.raises(services.PedidoNaoEncontrado):
        services.adicionar_item("P9", "CHOC", 1, repos["pedidos"], repos["sabores"], FakeSession())


def test_finalizar_pedido_baixa_estoque(repos):
    session = FakeSession()
    _pedido_com_item(repos, session, quantidade=2, estoque=10)

    services.finalizar_pedido("P1", repos["pedidos"], repos["contas"], session)

    assert repos["pedidos"].get("P1").status == StatusPedido.FINALIZADO
    assert repos["sabores"].get("CHOC").quantidade_estoque == 8


def test_finalizar_pedido_credita_pontos_de_fidelidade(repos):
    session = FakeSession()
    services.cadastrar_cliente("C1", "Ana", repos["clientes"], repos["contas"], session)
    _pedido_com_item(repos, session, quantidade=2)  # 2 x R$ 8,00 = R$ 16,00

    services.finalizar_pedido("P1", repos["pedidos"], repos["contas"], session)

    assert repos["contas"].get("C1").saldo == 16


def test_finalizar_pedido_sem_estoque_nao_credita_pontos(repos):
    session = FakeSession()
    services.cadastrar_cliente("C1", "Ana", repos["clientes"], repos["contas"], session)
    _pedido_com_item(repos, session, quantidade=5, estoque=3)

    with pytest.raises(EstoqueInsuficiente):
        services.finalizar_pedido("P1", repos["pedidos"], repos["contas"], session)

    assert repos["contas"].get("C1").saldo == 0


def test_cancelar_pedido_finalizado_e_bloqueado(repos):
    session = FakeSession()
    _pedido_com_item(repos, session)
    services.finalizar_pedido("P1", repos["pedidos"], repos["contas"], session)

    with pytest.raises(PedidoNaoPodeSerCancelado):
        services.cancelar_pedido("P1", repos["pedidos"], session)


def test_cadastrar_cliente_abre_conta_com_saldo_zero(repos):
    services.cadastrar_cliente("C1", "Ana", repos["clientes"], repos["contas"], FakeSession())

    assert repos["clientes"].get("C1").nome == "Ana"
    assert repos["contas"].get("C1").saldo == 0


def test_resgatar_pontos_sem_saldo_e_bloqueado(repos):
    session = FakeSession()
    services.cadastrar_cliente("C1", "Ana", repos["clientes"], repos["contas"], session)

    with pytest.raises(SaldoInsuficiente):
        services.resgatar_pontos("C1", 10, repos["contas"], session)