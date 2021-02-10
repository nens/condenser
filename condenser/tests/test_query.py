from .schema import TestModel
from condenser import NumpyQuery

import pytest
import numpy as np


def test_query_cls(db_session):
    """Test whether query_cls is overriden in conftest.py."""
    assert isinstance(db_session.query(TestModel), NumpyQuery)


@pytest.mark.parametrize("entity,expected_type", [
    (TestModel, np.dtype("O")),
    (TestModel.col_int, np.int64),
    (TestModel.col_float, np.float64),
    (TestModel.col_str, np.dtype("O")),
    (TestModel.col_text, np.dtype("O")),
    (TestModel.col_bool, np.bool),
])
def test_numpy_dtype(db_session, entity, expected_type):
    """Numpy dtype of various entities"""
    q = db_session.query(entity)
    assert q.numpy_dtype[0] == expected_type
