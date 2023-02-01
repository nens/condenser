from .conftest import requires_geo
from .schema import ModelOne
from condenser import NumpyQuery
from numpy.testing import assert_almost_equal
from numpy.testing import assert_array_equal
from numpy.testing import assert_equal
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

import numpy as np
import pytest


try:
    import shapely
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
        (ModelOne.col_bool, np.dtype(bool)),
    ],
)
def test_numpy_dtype(db_session, entity, expected_type):
    """Numpy dtype of all entities"""
    q = db_session.query(entity)
    assert q.numpy_dtype[0] == expected_type


@pytest.mark.parametrize(
    "entity,expected_type",
    [
        (ModelOne.col_int, np.int32),  # adapted
        (ModelOne.col_float, np.float64),  # untouched
    ],
)
def test_adapted_numpy_dtype(db_session, entity, expected_type):
    """Override type_mapping on the query instance"""
    q = db_session.query(entity)
    q.numpy_settings[Integer]["dtype"] = np.int32
    assert q.numpy_dtype[0] == expected_type


def test_as_structarray(db_session, record):
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


def test_as_structarray_null(db_session, record_null):
    """Convert all records to a numpy structured array"""
    q = db_session.query(
        ModelOne.col_int,
        ModelOne.col_float,
        ModelOne.col_str,
        ModelOne.col_text,
        ModelOne.col_bool,
    )
    actual = q.as_structarray()

    assert actual.dtype == q.numpy_dtype

    # compare element by element (to be able to check nans)
    assert actual["col_int"][0] == -1
    assert np.isnan(actual["col_float"][0])
    assert actual["col_str"][0] is None
    assert actual["col_text"][0] is None
    assert actual["col_bool"][0] == False


def test_adapted_null_values(db_session, record_null):
    """Convert all records to a numpy structured array"""
    q = db_session.query(
        ModelOne.col_int,
        ModelOne.col_float,
        ModelOne.col_str,
        ModelOne.col_text,
        ModelOne.col_bool,
    )
    q.numpy_settings[Integer]["null"] = -9999
    q.numpy_settings[Float]["null"] = 1e26
    q.numpy_settings[String]["null"] = ""
    q.numpy_settings[Text]["null"] = "empty"
    q.numpy_settings[Boolean]["null"] = True
    actual = q.as_structarray()

    assert actual.dtype == q.numpy_dtype

    # compare element by element (to be able to check nans)
    assert actual["col_int"][0] == -9999
    assert actual["col_float"][0] == pytest.approx(1e26)
    assert actual["col_str"][0] == ""
    assert actual["col_text"][0] == "empty"
    assert actual["col_bool"][0] == True


@requires_geo
def test_geometry(db_session, record):
    """Convert geometry fields to a array of shapely geometries"""
    q = db_session.query(ModelOne.col_geom)
    actual = q.as_structarray()

    # see conftest.py
    assert actual["col_geom"][0] == shapely.points(2, 3)


@requires_geo
def test_geometry_null(db_session, record_null):
    """Convert geometry fields to a array of shapely geometries"""
    q = db_session.query(ModelOne.col_geom)
    actual = q.as_structarray()

    assert actual["col_geom"][0] == None


@requires_geo
def test_geometry_transform(db_session, record):
    """Reproject a column that has 4326 projection"""
    q = db_session.query(ModelOne.col_geom_4326).with_transformed_geometries(3857)
    actual = q.as_structarray()

    # see conftest.py for the EPSG4326 coordinates
    assert_almost_equal(
        shapely.get_coordinates(actual["col_geom_4326"]), [[569472, 6816930]], decimal=0
    )


@requires_geo
def test_geometry_transform_unknown_input_srid(db_session, record):
    """Attempt to reproject a column that has no projection"""
    q = db_session.query(ModelOne.col_geom).with_transformed_geometries(3857)
    actual = q.as_structarray()

    # see conftest.py
    assert actual["col_geom"][0] == shapely.points(2, 3)
