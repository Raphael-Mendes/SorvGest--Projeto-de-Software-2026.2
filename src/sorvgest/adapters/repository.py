import abc

from sorvgest.domain.model import Sabor


class AbstractSaborRepository(abc.ABC):
    """Porta de persistência para Sabor. O domínio não conhece o banco."""

    @abc.abstractmethod
    def add(self, sabor: Sabor) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, referencia: str) -> Sabor | None:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[Sabor]:
        raise NotImplementedError


class FakeSaborRepository(AbstractSaborRepository):
    """Implementação em memória, usada nos testes unitários."""

    def __init__(self, sabores=None):
        self._sabores = {s.referencia: s for s in (sabores or [])}

    def add(self, sabor):
        self._sabores[sabor.referencia] = sabor

    def get(self, referencia):
        return self._sabores.get(referencia)

    def list(self):
        return list(self._sabores.values())