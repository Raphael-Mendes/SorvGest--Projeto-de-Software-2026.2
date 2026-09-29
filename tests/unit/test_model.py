import pytest

from sorvgest.domain.model import Preco

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
