import abc

from sorvgest.domain.model import Cliente, ContaFidelidade, Pedido, Sabor


# --- Sabor -------------------------------------------------------------------

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


class SqlAlchemySaborRepository(AbstractSaborRepository):
    def __init__(self, session):
        self.session = session

    def add(self, sabor):
        self.session.add(sabor)

    def get(self, referencia):
        return self.session.get(Sabor, referencia)

    def list(self):
        return self.session.query(Sabor).all()


# --- Pedido ------------------------------------------------------------------

class AbstractPedidoRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, pedido: Pedido) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, pedido_id: str) -> Pedido | None:
        raise NotImplementedError


class FakePedidoRepository(AbstractPedidoRepository):
    def __init__(self, pedidos=None):
        self._pedidos = {p.pedido_id: p for p in (pedidos or [])}

    def add(self, pedido):
        self._pedidos[pedido.pedido_id] = pedido

    def get(self, pedido_id):
        return self._pedidos.get(pedido_id)


class SqlAlchemyPedidoRepository(AbstractPedidoRepository):
    def __init__(self, session):
        self.session = session

    def add(self, pedido):
        self.session.add(pedido)

    def get(self, pedido_id):
        return self.session.get(Pedido, pedido_id)


# --- Cliente -----------------------------------------------------------------

class AbstractClienteRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, cliente: Cliente) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, cliente_id: str) -> Cliente | None:
        raise NotImplementedError


class FakeClienteRepository(AbstractClienteRepository):
    def __init__(self, clientes=None):
        self._clientes = {c.cliente_id: c for c in (clientes or [])}

    def add(self, cliente):
        self._clientes[cliente.cliente_id] = cliente

    def get(self, cliente_id):
        return self._clientes.get(cliente_id)


class SqlAlchemyClienteRepository(AbstractClienteRepository):
    def __init__(self, session):
        self.session = session

    def add(self, cliente):
        self.session.add(cliente)

    def get(self, cliente_id):
        return self.session.get(Cliente, cliente_id)


# --- ContaFidelidade ---------------------------------------------------------

class AbstractContaFidelidadeRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, conta: ContaFidelidade) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, cliente_id: str) -> ContaFidelidade | None:
        raise NotImplementedError


class FakeContaFidelidadeRepository(AbstractContaFidelidadeRepository):
    def __init__(self, contas=None):
        self._contas = {c.cliente_id: c for c in (contas or [])}

    def add(self, conta):
        self._contas[conta.cliente_id] = conta

    def get(self, cliente_id):
        return self._contas.get(cliente_id)


class SqlAlchemyContaFidelidadeRepository(AbstractContaFidelidadeRepository):
    def __init__(self, session):
        self.session = session

    def add(self, conta):
        self.session.add(conta)

    def get(self, cliente_id):
        return self.session.get(ContaFidelidade, cliente_id)