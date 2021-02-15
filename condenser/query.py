import numpy as np
from collections import defaultdict
import copy
from collections import defaultdict
from sqlalchemy.orm.query import Query

from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text


class NumpyQueryMixin:
    # The precise type mapping depends on the dialect.
    # Use 8-bytes to be safe (e.g. SQLite uses that by default)
    default_numpy_settings = {
        Boolean: {"dtype": np.dtype(np.bool)},
        Float: {"dtype": np.dtype(np.float64)},
        Integer: {"dtype": np.dtype(np.int64)},
        Numeric: {"dtype": np.dtype(np.float64)},
        String: {"dtype": np.dtype("O")},
        Text: {"dtype": np.dtype("O")},
    }
    # Todo: BigInteger, Date, DateTime, Enum, Interval, LargeBinary, PickleType
    # SchemaType, SmallInteger, Time, Unicode, UnicodeText

    # Geometry is only available if the optional dependencies geoalchemy2 and
    # pygeos are present.
    try:
        from geoalchemy2.types import Geometry
        from geoalchemy2.functions import ST_AsBinary
        import pygeos

        default_numpy_settings[Geometry] = {
            "dtype": np.dtype("O"),
            "sql_cast": ST_AsBinary,
            "numpy_cast": pygeos.from_wkb,
        }
    except ImportError:
        pass

    def __init__(self, *args, **kwargs):
        # deepcopy the numpy settings to allow adaptation
        self.numpy_settings = copy.deepcopy(self.default_numpy_settings)
        return super().__init__(*args, **kwargs)

    @property
    def numpy_dtype(self):
        """Map the SQL Column types to NumPy dtypes (defaulting to object)

        Mapping is done according to self.numpy_settings[:]["dtype"].
        """
        result = []
        for i, descr in enumerate(self.column_descriptions):
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            dtype = settings.get("dtype", np.dtype("O"))
            result.append((descr["name"] or "f{}".format(i), dtype))
        return np.dtype(result)

    def with_numpy_cast_columns(self):
        """Cast the entities in this query to numpy-compatible ones

        Casts is done according to self.numpy_settings[:]["sql_cast"].
        """
        new_columns = []
        for descr in self.column_descriptions:
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            cast_func = settings.get("sql_cast")
            if cast_func is not None:
                new_columns.append(cast_func(descr["expr"]))
            else:
                new_columns.append(descr["expr"])
        # Note: this discards the names of cast columns
        return self.with_entities(*new_columns)

    def as_structarray(self):
        # Apply casts
        cast_query = self.with_numpy_cast_columns()

        # Get the numpy dtype
        dtype = cast_query.numpy_dtype

        # insert the column names back in from the original query (it might
        # have been lost in the sql typecasts)
        dtype.names = [
            (x["name"] or "f{}".format(i))
            for (i, x) in enumerate(self.column_descriptions)
        ]

        # Cannot use np.fromiter with complex dtypes, so we go through a list
        arr = np.array(list(cast_query), dtype=dtype)

        for descr in self.column_descriptions:
            settings = self.numpy_settings.get(descr["type"].__class__, {})
            if "numpy_cast" in settings:
                arr[descr["name"]] = settings["numpy_cast"](arr[descr["name"]])

        return arr


class NumpyQuery(NumpyQueryMixin, Query):
    pass
