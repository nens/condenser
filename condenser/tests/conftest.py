from .schema import Base
from .schema import TestModel
from condenser import NumpyQuery
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import os
import pytest


@pytest.fixture(scope='session')
def db_engine(request):
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    engine = create_engine("sqlite://")
    session_factory = scoped_session(sessionmaker(bind=engine))
    
    Base.metadata.create_all(engine)

    session = session_factory()
    session.add(TestModel(col_int=2, col_str="a", col_float=5.2))
    session.commit()
    session.close()

    yield engine
    engine.dispose()


@pytest.fixture(scope='session')
def db_session_factory(db_engine):
    """returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture(scope='function')
def db_session(db_session_factory):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    session = db_session_factory(query_cls=NumpyQuery)

    yield session

    session.rollback()
    session.close()
