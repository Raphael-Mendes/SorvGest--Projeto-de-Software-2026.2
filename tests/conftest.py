import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker
from sqlalchemy.pool import StaticPool

from sorvgest.adapters.orm import metadata, start_mappers


@pytest.fixture
def engine_em_memoria():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine_em_memoria):
    start_mappers()
    yield sessionmaker(bind=engine_em_memoria)
    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()