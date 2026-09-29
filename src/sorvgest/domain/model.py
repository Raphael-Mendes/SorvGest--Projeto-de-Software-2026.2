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

#Pedido

class Pedido:
    def __init__(self, cliente_id=None):
        self.cliente_id = cliente_id
        self.status = StatusPedido.ABERTO
        self._itens = []

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
        if self.status != StatusPedido.ABERTO:
            raise PedidoNaoPodeSerFinalizado("Nao e possivel adicionar itens a um pedido que nao esta aberto.")

        if quantidade <= 0:
            raise ItemInvalido("A quantidade deve ser maior que zero.")

        refs_existentes = [item.sabor.referencia for item in self._itens]
        if sabor.referencia in refs_existentes:
            raise ItemInvalido("O sabor ja esta presente no pedido.")

        self._itens.append(ItemPedido(sabor, quantidade))

    def finalizar(self):
        if self.status != StatusPedido.ABERTO:
            raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido que não está aberto.")
        if not self.itens:
            raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido sem itens.")

        for item in self.itens:
            if item.quantidade > item.sabor.quantidade_estoque:
                raise EstoqueInsuficiente(f"Estoque insuficiente para o sabor {item.sabor.nome}.")

        for item in self.itens:
            item.sabor.baixar_estoque(item.quantidade)

        self.status = StatusPedido.FINALIZADO

    def cancelar(self):
        if self.status != StatusPedido.ABERTO:
            raise PedidoNaoPodeSerCancelado("Não é possível cancelar um pedido que não está aberto.")

        self.status = StatusPedido.CANCELADO

    def __repr__(self):
        return f"Pedido(cliente_id={self.cliente_id}, status={self.status}, itens={self.itens})"
            
        