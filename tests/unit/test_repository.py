from sorvgest.adapters.repository import FakeSaborRepository
from sorvgest.domain.model import Preco, Sabor


def test_add_e_get_retornam_o_mesmo_sabor():
    repo = FakeSaborRepository()
    sabor = Sabor("CHOC", "Chocolate", Preco(800), 10)

    repo.add(sabor)

    assert repo.get("CHOC") is sabor


def test_get_de_referencia_inexistente_retorna_none():
    repo = FakeSaborRepository()

    assert repo.get("NAO-EXISTE") is None


def test_list_retorna_todos_os_sabores():
    choc = Sabor("CHOC", "Chocolate", Preco(800), 10)
    morango = Sabor("MOR", "Morango", Preco(700), 5)
    repo = FakeSaborRepository([choc, morango])

    assert {s.referencia for s in repo.list()} == {"CHOC", "MOR"}