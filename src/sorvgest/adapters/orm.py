from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.orm import registry, relationship

from sorvgest.domain.model import Cliente, ContaFidelidade, ItemPedido, Pedido, Sabor

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

sabores = Table(
    "sabores",
    metadata,
    Column("referencia", String(50), primary_key=True),
    Column("nome", String(100), nullable=False),
    Column("preco_centavos", Integer, nullable=False),
    Column("quantidade_estoque", Integer, nullable=False),
)

pedidos = Table(
    "pedidos",
    metadata,
    Column("pedido_id", String(50), primary_key=True),
    Column("cliente_id", String(50)),
    Column("status", String(20), nullable=False),
)

itens_pedido = Table(
    "itens_pedido",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("pedido_id", ForeignKey("pedidos.pedido_id"), nullable=False),
    Column("referencia_sabor", ForeignKey("sabores.referencia"), nullable=False),
    Column("quantidade", Integer, nullable=False),
)

clientes = Table(
    "clientes",
    metadata,
    Column("cliente_id", String(50), primary_key=True),
    Column("nome", String(100), nullable=False),
)

contas_fidelidade = Table(
    "contas_fidelidade",
    metadata,
    Column("cliente_id", ForeignKey("clientes.cliente_id"), primary_key=True),
    Column("saldo", Integer, nullable=False),
)


def start_mappers():
    """Mapeamento imperativo: o domínio não importa nada do SQLAlchemy."""
    mapper_registry.map_imperatively(Sabor, sabores)
    mapper_registry.map_imperatively(
        ItemPedido,
        itens_pedido,
        properties={"sabor": relationship(Sabor)},
    )
    mapper_registry.map_imperatively(
        Pedido,
        pedidos,
        properties={
            "_itens": relationship(ItemPedido, cascade="all, delete-orphan"),
        },
    )
    mapper_registry.map_imperatively(Cliente, clientes)
    mapper_registry.map_imperatively(
        ContaFidelidade,
        contas_fidelidade,
        properties={"_saldo": contas_fidelidade.c.saldo},
    )