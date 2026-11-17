from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sorvgest.adapters import orm, repository
from sorvgest.domain import model
from sorvgest.service_layer import services

ERROS_DE_NEGOCIO = (
    ValueError,
    model.EstoqueInsuficiente,
    model.PedidoNaoPodeSerCancelado,
    model.PedidoNaoPodeSerFinalizado,
    model.ItemInvalido,
    model.SaldoInsuficiente,
    services.JaCadastrado,
)
NAO_ENCONTRADO = (
    services.SaborNaoEncontrado,
    services.PedidoNaoEncontrado,
    services.ClienteNaoEncontrado,
)


def create_app(session_factory=None):
    if session_factory is None:
        engine = create_engine("sqlite:///sorvgest.db")
        orm.metadata.create_all(engine)
        orm.start_mappers()
        session_factory = sessionmaker(bind=engine)

    app = Flask(__name__)

    def nao_encontrado(erro):
        return jsonify(erro=str(erro)), 404

    def erro_de_negocio(erro):
        return jsonify(erro=str(erro)), 400

    for excecao in NAO_ENCONTRADO:
        app.register_error_handler(excecao, nao_encontrado)
    for excecao in ERROS_DE_NEGOCIO:
        app.register_error_handler(excecao, erro_de_negocio)

    @app.post("/sabores")
    def cadastrar_sabor():
        session = session_factory()
        dados = request.json
        services.cadastrar_sabor(
            dados["referencia"],
            dados["nome"],
            dados["preco_centavos"],
            dados.get("quantidade_estoque", 0),
            repository.SqlAlchemySaborRepository(session),
            session,
        )
        return jsonify(referencia=dados["referencia"]), 201

    @app.post("/sabores/<referencia>/reposicoes")
    def repor_estoque(referencia):
        session = session_factory()
        services.repor_estoque(
            referencia,
            request.json["quantidade"],
            repository.SqlAlchemySaborRepository(session),
            session,
        )
        return "", 204

    @app.post("/pedidos")
    def criar_pedido():
        session = session_factory()
        dados = request.json
        services.criar_pedido(
            dados["pedido_id"],
            dados.get("cliente_id"),
            repository.SqlAlchemyPedidoRepository(session),
            session,
        )
        return jsonify(pedido_id=dados["pedido_id"]), 201

    @app.post("/pedidos/<pedido_id>/itens")
    def adicionar_item(pedido_id):
        session = session_factory()
        dados = request.json
        services.adicionar_item(
            pedido_id,
            dados["referencia_sabor"],
            dados["quantidade"],
            repository.SqlAlchemyPedidoRepository(session),
            repository.SqlAlchemySaborRepository(session),
            session,
        )
        return "", 204

    @app.post("/pedidos/<pedido_id>/finalizar")
    def finalizar_pedido(pedido_id):
        session = session_factory()
        total = services.finalizar_pedido(
            pedido_id,
            repository.SqlAlchemyPedidoRepository(session),
            repository.SqlAlchemyContaFidelidadeRepository(session),
            session,
        )
        return jsonify(total_centavos=total), 200

    @app.post("/pedidos/<pedido_id>/cancelar")
    def cancelar_pedido(pedido_id):
        session = session_factory()
        services.cancelar_pedido(
            pedido_id, repository.SqlAlchemyPedidoRepository(session), session
        )
        return "", 204

    @app.post("/clientes")
    def cadastrar_cliente():
        session = session_factory()
        dados = request.json
        services.cadastrar_cliente(
            dados["cliente_id"],
            dados["nome"],
            repository.SqlAlchemyClienteRepository(session),
            repository.SqlAlchemyContaFidelidadeRepository(session),
            session,
        )
        return jsonify(cliente_id=dados["cliente_id"]), 201

    @app.post("/clientes/<cliente_id>/resgates")
    def resgatar_pontos(cliente_id):
        session = session_factory()
        saldo = services.resgatar_pontos(
            cliente_id,
            request.json["pontos"],
            repository.SqlAlchemyContaFidelidadeRepository(session),
            session,
        )
        return jsonify(saldo=saldo), 200

    return app