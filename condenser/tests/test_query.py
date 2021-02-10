from .schema import TestModel
from condenser import NumpyQuery

import pytest


def test_query_cls(db_session):
    """Sample test to test the conftest.py."""
    assert isinstance(db_session.query(TestModel), NumpyQuery)
