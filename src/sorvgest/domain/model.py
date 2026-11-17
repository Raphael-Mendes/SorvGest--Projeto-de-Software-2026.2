
import abc
#Exceções:

class EstoqueInsuficiente(Exception):
    pass

class PedidoNaoPodeSerCancelado(Exception):
    pass

class PedidoNaoPodeSerFinalizado(Exception):
    pass

class ItemInvalido(Exception):
    pass

#Classe 1: Preço

class Preco:
    def __init__(self, centavos):
        if centavos < 0:
            raise ValueError("O preço não pode ser negativo.")
        self.centavos = centavos

    @property
    def reais(self):
        return self.centavos / 100

    def __add__(self, outro):
        if isinstance(outro, Preco):
            return Preco(self.centavos + outro.centavos)

    def __mul__(self, quantidade):
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa.")
        return Preco(self.centavos * quantidade)

    def __rmul__(self, quantidade):
        return self.__mul__(quantidade)

    def __eq__(self, outro):
        if isinstance(outro, Preco):
            return self.centavos == outro.centavos
        return False

    def __hash__(self):
        return hash(self.centavos)

    def __repr__(self):
        return f"Preco({self.centavos} centavos)"

#Classe 2: Sabor

class Sabor:
    def __init__(self, referencia, nome, preco, quantidade_estoque=0):
        if not referencia:
            raise ValueError("A referencia nao pode ser vazia.")
        if not nome:
            raise ValueError("O nome nao pode ser vazio.")
        if quantidade_estoque < 0:
            raise ValueError("A Quantidade em estoque nao pode ser negativa.")

        self.referencia = referencia
        self.nome = nome
        self.preco_centavos = preco.centavos
        self.quantidade_estoque = quantidade_estoque

    @property
    def preco(self):
        return Preco(self.preco_centavos)

    def baixar_estoque(self, quantidade):
        if quantidade < 0:
            raise ValueError("A quantidade a baixar não pode ser negativa.")
        if quantidade == 0:
            raise ValueError("A quantidade a baixar não pode ser zero.")
        if quantidade > self.quantidade_estoque:
            raise EstoqueInsuficiente("Estoque insuficiente para baixar a quantidade inserida")

        self.quantidade_estoque -= quantidade

    def tem_estoque_para(self, quantidade):
        return quantidade <= self.quantidade_estoque

    def repor_estoque(self, quantidade):
        if quantidade < 0:
            raise ValueError("A quantidade a repor não pode ser negativa.")
        if quantidade == 0:
            raise ValueError("A quantidade a repor não pode ser zero.")

        self.quantidade_estoque += quantidade

    def __repr__(self):
        return f"Sabor(referencia={self.referencia}, nome={self.nome}, preco={self.preco}, quantidade_estoque={self.quantidade_estoque})"


        #Status do Pedido

class StatusPedido:
    ABERTO = "ABERTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"

#ItemPedido

class ItemPedido:
    def __init__(self, sabor, quantidade):
        self.sabor = sabor
        self.quantidade = quantidade

    @property
    def subtotal(self):
        return self.sabor.preco * self.quantidade

    def __repr__(self):
        return f"ItemPedido(sabor={self.sabor}, quantidade={self.quantidade})"

#Baixa de estoque

class BaixaDeEstoque(abc.ABC):
    """Abstração da qual o Pedido depende para baixar o estoque dos seus itens."""

    @abc.abstractmethod
    def baixar(self, itens):
        raise NotImplementedError


class BaixaNoSabor(BaixaDeEstoque):
    """Regra padrão: confere o estoque de todos os itens e só então baixa (tudo ou nada)."""

    def baixar(self, itens):
        for item in itens:
            if not item.sabor.tem_estoque_para(item.quantidade):
                raise EstoqueInsuficiente(f"Estoque insuficiente para o sabor {item.sabor.nome}.")

        for item in itens:
            item.sabor.baixar_estoque(item.quantidade)

#Pedido
#Estados do Pedido (padrão State)

class EstadoPedido:
    """Estado do ciclo de vida do Pedido. Por padrão, nenhuma operação é permitida."""

    nome = None

    def adicionar_item(self, pedido, sabor, quantidade):
        raise PedidoNaoPodeSerFinalizado("Nao e possivel adicionar itens a um pedido que nao esta aberto.")

    def finalizar(self, pedido, baixa_de_estoque):
        raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido que não está aberto.")

    def cancelar(self, pedido):
        raise PedidoNaoPodeSerCancelado("Não é possível cancelar um pedido que não está aberto.")


class PedidoAberto(EstadoPedido):
    nome = StatusPedido.ABERTO

    def adicionar_item(self, pedido, sabor, quantidade):
        pedido._incluir_item(sabor, quantidade)

    def finalizar(self, pedido, baixa_de_estoque):
        if not pedido.itens:
            raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido sem itens.")

        baixa = baixa_de_estoque or BaixaNoSabor()
        baixa.baixar(pedido.itens)

        pedido._mudar_para(PedidoFinalizado.nome)

    def cancelar(self, pedido):
        pedido._mudar_para(PedidoCancelado.nome)


class PedidoFinalizado(EstadoPedido):
    nome = StatusPedido.FINALIZADO


class PedidoCancelado(EstadoPedido):
    nome = StatusPedido.CANCELADO


_ESTADOS = {estado.nome: estado for estado in (PedidoAberto(), PedidoFinalizado(), PedidoCancelado())}


#Pedido

class Pedido:
    def __init__(self, cliente_id=None, pedido_id=None):
        self.pedido_id = pedido_id
        self.cliente_id = cliente_id
        self.status = StatusPedido.ABERTO
        self._itens = []

    @property
    def estado(self):
        return _ESTADOS[self.status]

    @property
    def itens(self):
        return list(self._itens)

    @property
    def total(self):
        resultado = Preco(0)
        for item in self.itens:
            resultado = resultado + item.subtotal
        return resultado

    def adicionar_item(self, sabor, quantidade):
        self.estado.adicionar_item(self, sabor, quantidade)

    def finalizar(self, baixa_de_estoque=None):
        self.estado.finalizar(self, baixa_de_estoque)

    def cancelar(self):
        self.estado.cancelar(self)

    def _incluir_item(self, sabor, quantidade):
        if quantidade <= 0:
            raise ItemInvalido("A quantidade deve ser maior que zero.")

        refs_existentes = [item.sabor.referencia for item in self._itens]
        if sabor.referencia in refs_existentes:
            raise ItemInvalido("O sabor ja esta presente no pedido.")

        self._itens.append(ItemPedido(sabor, quantidade))

    def _mudar_para(self, status):
        self.status = status

    def __repr__(self):
        return f"Pedido(cliente_id={self.cliente_id}, status={self.status}, itens={self.itens})"

class SaldoInsuficiente(Exception):
    pass
            
#Cliente

class Cliente:
    def __init__(self, cliente_id, nome):
        if not cliente_id:
            raise ValueError("O id do cliente nao pode ser vazio.")
        if not nome:
            raise ValueError("O nome do cliente nao pode ser vazio.")

        self.cliente_id = cliente_id
        self.nome = nome

    def __eq__(self, outro):
        if isinstance(outro, Cliente):
            return self.cliente_id == outro.cliente_id
        return False

    def __hash__(self):
        return hash(self.cliente_id)

    def __repr__(self):
        return f"Cliente(cliente_id={self.cliente_id}, nome={self.nome})"


#ContaFidelidade

class ContaFidelidade:
    """Agregado: o saldo de pontos nunca fica negativo e o resgate exige saldo suficiente."""

    def __init__(self, cliente_id, saldo=0):
        if not cliente_id:
            raise ValueError("A conta precisa estar associada a um cliente.")
        if saldo < 0:
            raise ValueError("O saldo inicial nao pode ser negativo.")

        self.cliente_id = cliente_id
        self._saldo = saldo

    @property
    def saldo(self):
        return self._saldo

    def acumular(self, pontos):
        if pontos <= 0:
            raise ValueError("A quantidade de pontos a acumular deve ser maior que zero.")

        self._saldo += pontos

    def resgatar(self, pontos):
        if pontos <= 0:
            raise ValueError("A quantidade de pontos a resgatar deve ser maior que zero.")
        if pontos > self._saldo:
            raise SaldoInsuficiente("Saldo de pontos insuficiente para o resgate.")

        self._saldo -= pontos

    def __repr__(self):
        return f"ContaFidelidade(cliente_id={self.cliente_id}, saldo={self._saldo})"