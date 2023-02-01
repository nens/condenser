from .utils import has_geo
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm.query import Query

import copy
import numpy as np


if has_geo:
    from geoalchemy2.types import Geometry
    from geoalchemy2.functions import ST_AsBinary, ST_Transform
    import shapely


class NumpyQueryMixin:
    # The precise type mapping depends on the dialect.
    # Use 8-bytes to be safe (e.g. SQLite uses that by default)
    default_numpy_settings = {
        Boolean: {"dtype": np.dtype(bool)},
        Float: {"dtype": np.dtype(np.float64)},
        Integer: {"dtype": np.dtype(np.int64), "null": -1},
        Numeric: {"dtype": np.dtype(np.float64)},
        String: {"dtype": np.dtype("O")},
        Text: {"dtype": np.dtype("O")},
    }
    # Todo: BigInteger, Date, DateTime, Enum, Interval, LargeBinary, PickleType
    # SchemaType, SmallInteger, Time, Unicode, UnicodeText

    # Geometry is only available if the optional dependencies geoalchemy2 and
    # shapely are present.
    if has_geo:
        default_numpy_settings[Geometry] = {
            "dtype": np.dtype("O"),
            "sql_cast": ST_AsBinary,
            "numpy_cast": shapely.from_wkb,
        }

    def __init__(self, *args, **kwargs):
        # deepcopy the numpy settings to allow per-query adaptation
        self.numpy_settings = copy.deepcopy(self.default_numpy_settings)
        return super().__init__(*args, **kwargs)

    @property
    def numpy_dtype(self):
        """Map the SQL column types to numpy dtypes (defaulting to object).

        Mapping is done according to self.numpy_settings[:]["dtype"].
        """
        result = []
        for i, descr in enumerate(self.column_descriptions):
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            dtype = settings.get("dtype", np.dtype("O"))
            result.append((descr["name"] or "f{}".format(i), dtype))
        return np.dtype(result)

    def with_numpy_entities(self):
        """Convert the entities in this query to numpy-compatible ones.

        - SQL casts are done according to self.numpy_settings[:]["sql_cast"]
        - NULL values are replaced according to self.numpy_settings[:]["null"]
        - column labels are set to "f{entity_number}" if not present
        """
        new_expressions = []
        for i, descr in enumerate(self.column_descriptions):
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            expr = descr["expr"]

            cast_func = settings.get("sql_cast")
            if cast_func is not None:
                expr = cast_func(expr)

            null_value = settings.get("null")
            if null_value is not None:
                expr = func.coalesce(expr, null_value)

            expr = expr.label(descr["name"] or "f{}".format(i))

            new_expressions.append(expr)
        return self.with_entities(*new_expressions)

    def as_structarray(self):
        """Read all entities in this query into a numpy structured array.

        Every entity is mapped to a column in the structured array.

        Specific types are converted into numpy datatypes. This is configured
        through ``self.numpy_settings``.
        """
        # Apply casts and get the data
        cast_query = self.with_numpy_entities()
        data = list(cast_query)

        # Cannot use np.fromiter or np.array directly (because have a list
        # of tuples/Row instances to iterate over)
        arr = np.empty((len(data),), dtype=cast_query.numpy_dtype)
        for i in range(len(data)):
            arr[i] = tuple(data[i])

        # Execute numpy typecasts if present
        for descr in self.column_descriptions:
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            numpy_cast = settings.get("numpy_cast")
            if numpy_cast is not None:
                arr[descr["name"]] = numpy_cast(arr[descr["name"]])

        return arr

    def with_transformed_geometries(self, target_srid):
        """Transform all SRID-aware columns to given target SRID

        Args:
          target_srid (int): The SRID to reproject the geometries into.

        See also:
          Columns that are not SRID-aware do not support coordinate
          transformations. If an SRID is known from metadata, use a function
          appropriate to your database backend to set it (e.g. `ST_SetSRID`
          for PostGIS and `setsrid` for SQLite/spatialite)
        """
        if not has_geo:
            raise ImportError("This function requires GeoAlchemy2 and shapely")
        srid = int(target_srid)
        new_columns = []
        for descr in self.column_descriptions:
            if descr["type"].__class__ == Geometry and descr["type"].srid > 0:
                new_columns.append(
                    ST_Transform(descr["expr"], srid).label(descr["name"])
                )
            else:
                new_columns.append(descr["expr"])
        # Note: this discards the names of cast columns
        return self.with_entities(*new_columns)


class NumpyQuery(NumpyQueryMixin, Query):
    pass
