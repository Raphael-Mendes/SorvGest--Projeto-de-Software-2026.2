from sqlalchemy import text

from sorvgest.adapters.repository import (
    SqlAlchemyContaFidelidadeRepository,
    SqlAlchemyPedidoRepository,
    SqlAlchemySaborRepository,
)
from sorvgest.domain.model import ContaFidelidade, Pedido, Preco, Sabor


def test_repositorio_salva_sabor(session):
    repo = SqlAlchemySaborRepository(session)
    repo.add(Sabor("CHOC", "Chocolate", Preco(800), 10))
    session.commit()

    linhas = session.execute(
        text("SELECT referencia, nome, preco_centavos, quantidade_estoque FROM sabores")
    ).all()

    assert linhas == [("CHOC", "Chocolate", 800, 10)]


def test_repositorio_recupera_sabor(session):
    session.execute(
        text(
            "INSERT INTO sabores (referencia, nome, preco_centavos, quantidade_estoque) "
            "VALUES ('MOR', 'Morango', 700, 5)"
        )
    )
    repo = SqlAlchemySaborRepository(session)

    sabor = repo.get("MOR")

    assert sabor.nome == "Morango"
    assert sabor.preco == Preco(700)


def test_repositorio_salva_e_recupera_pedido_com_itens(session_factory):
    session = session_factory()
    sabor = Sabor("CHOC", "Chocolate", Preco(800), 10)
    pedido = Pedido(cliente_id="C1", pedido_id="P1")
    pedido.adicionar_item(sabor, 2)
    SqlAlchemyPedidoRepository(session).add(pedido)
    session.commit()

    outra_session = session_factory()
    recuperado = SqlAlchemyPedidoRepository(outra_session).get("P1")

    assert recuperado.cliente_id == "C1"
    assert len(recuperado.itens) == 1
    assert recuperado.itens[0].sabor.referencia == "CHOC"
    assert recuperado.total == Preco(1600)


def test_repositorio_preserva_saldo_da_conta(session_factory):
    session = session_factory()
    conta = ContaFidelidade("C1")
    conta.acumular(40)
    SqlAlchemyContaFidelidadeRepository(session).add(conta)
    session.commit()

    recuperada = SqlAlchemyContaFidelidadeRepository(session_factory()).get("C1")

    assert recuperada.saldo == 40