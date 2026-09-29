#Exceções:

class EstoqueInsuficiente(Exception):
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
            