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