from .schema import Base
from .schema import ModelOne
from condenser import NumpyQuery
from condenser.utils import load_spatialite
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listen
from sqlalchemy.sql import select, func

import os
import pytest

try:
    from geoalchemy2.types import Geometry
    import pygeos

    has_geo = True
except ImportError:
    has_geo = False

requires_geo = pytest.mark.skipif(not has_geo, reason="requires GeoAlchemy2 and pygeos")


@pytest.fixture(scope="session")
def db_engine(request):
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    engine = create_engine("sqlite://")
    if has_geo:
        # https://geoalchemy-2.readthedocs.io/en/latest/spatialite_tutorial.html
        listen(engine, "connect", load_spatialite)
        conn = engine.connect()
        conn.execute(select([func.InitSpatialMetaData()]))
        conn.close()

    session_factory = scoped_session(sessionmaker(bind=engine))

    Base.metadata.create_all(engine)

    record = ModelOne(
        col_int=2,
        col_str="foo",
        col_float=5.2,
        col_bool=True,
        col_text="once upon a time",
    )
    if has_geo:
        record.col_geom = "POINT (2 3)"

    session = session_factory()
    session.add(record)
    session.commit()
    session.close()

    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine, query_cls=NumpyQuery))


@pytest.fixture(scope="function")
def db_session(db_session_factory):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session = db_session_factory()

    yield session

    session.rollback()
    session.close()
