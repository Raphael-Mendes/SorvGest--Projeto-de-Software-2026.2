import pytest

from sorvgest.domain.model import Cliente, ContaFidelidade, SaldoInsuficiente


def test_cliente_sem_nome_e_invalido():
    with pytest.raises(ValueError):
        Cliente("C1", "")


def test_clientes_com_mesmo_id_sao_iguais():
    assert Cliente("C1", "Ana") == Cliente("C1", "Ana Maria")


def test_conta_comeca_com_saldo_zero():
    conta = ContaFidelidade("C1")

    assert conta.saldo == 0


def test_acumular_aumenta_o_saldo():
    conta = ContaFidelidade("C1")

    conta.acumular(50)

    assert conta.saldo == 50


def test_acumular_pontos_nao_positivos_e_invalido():
    conta = ContaFidelidade("C1")

    with pytest.raises(ValueError):
        conta.acumular(0)


def test_resgatar_diminui_o_saldo():
    conta = ContaFidelidade("C1", saldo=100)

    conta.resgatar(30)

    assert conta.saldo == 70


def test_resgate_maior_que_o_saldo_e_bloqueado():
    conta = ContaFidelidade("C1", saldo=20)

    with pytest.raises(SaldoInsuficiente):
        conta.resgatar(30)

    assert conta.saldo == 20


def test_saldo_inicial_negativo_e_invalido():
    with pytest.raises(ValueError):
        ContaFidelidade("C1", saldo=-1)