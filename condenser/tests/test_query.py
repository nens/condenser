from .conftest import requires_geo
from .schema import ModelOne
from condenser import NumpyQuery

from sqlalchemy import Integer

import pytest
import numpy as np
from numpy.testing import assert_array_equal

try:
    import pygeos
except ImportError:
    pass


def test_query_cls(db_session):
    """Test whether query_cls is overriden in conftest.py."""
    assert isinstance(db_session.query(ModelOne), NumpyQuery)


@pytest.mark.parametrize(
    "entity,expected_type",
    [
        (ModelOne, np.dtype("O")),
        (ModelOne.col_int, np.int64),
        (ModelOne.col_float, np.float64),
        (ModelOne.col_str, np.dtype("O")),
        (ModelOne.col_text, np.dtype("O")),
        (ModelOne.col_bool, np.bool),
    ],
)
def test_numpy_dtype(db_session, entity, expected_type):
    """Numpy dtype of all entities"""
    q = db_session.query(entity)
    assert q.numpy_dtype[0] == expected_type


def test_as_structarray(db_session):
    """Convert all records to a numpy structured array"""
    q = db_session.query(
        ModelOne.col_int,
        ModelOne.col_float,
        ModelOne.col_str,
        ModelOne.col_text,
        ModelOne.col_bool,
    )
    actual = q.as_structarray()

    # see conftest.py
    expected = np.array(
        [(2, 5.2, "foo", "once upon a time", True)], dtype=q.numpy_dtype
    )

    assert_array_equal(actual, expected)


@requires_geo
def test_geometry(db_session):
    """Convert all records to a numpy structured array"""
    q = db_session.query(ModelOne.col_geom)
    actual = q.as_structarray()

    # see conftest.py
    assert actual["col_geom"][0] == pygeos.points(2, 3)
