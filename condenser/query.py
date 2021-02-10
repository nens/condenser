import numpy as np
from collections import defaultdict
from sqlalchemy.orm.query import Query
# from sqlalchemy import BigInteger
from sqlalchemy import Boolean
# from sqlalchemy import Date
# from sqlalchemy import DateTime
# from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import Integer
# from sqlalchemy import ForeignKey
# from sqlalchemy import LargeBinary
# from sqlalchemy import MatchType
from sqlalchemy import Numeric
# from sqlalchemy import PickleType
# from sqlalchemy import SchemaType
# from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
# from sqlalchemy import Time
# from sqlalchemy import Unicode
# from sqlalchemy import UnicodeText


class NumpyQueryMixin:
    # casts = {
    #     Enum: None
    #     ForeignKey:
    # }
    # The precise type mapping depends on the dialect.
    # Use 8-bytes to be safe (e.g. SQLite uses that by default)
    type_mapping = {
        # BigInteger: np.dtype(np.int64),
        Boolean: np.dtype(np.bool),
        # Date: np.dtype(np.datetime64),
        # DateTime: np.dtype(np.datetime64),
        # Enum:
        Float: np.dtype(np.float64),
        Integer: np.dtype(np.int64),  # SQLite may use 8 bytes
        # Interval: np.dtype(np.timedelta64),
        # LargeBinary:
        Numeric: np.dtype(np.float64),
        # PickleType:
        # SchemaType:
        # SmallInteger: np.dtype(np.int16),
        String: np.dtype("O"),
        Text: np.dtype("O"),
        # Time: np.dtype(np.datetime64),
        # Unicode
        # UnicodeText       
    }
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    @property
    def numpy_dtype(self):
        return np.dtype([
            (
                descr["name"],
                self.type_mapping.get(descr["type"].__class__, np.dtype("O"))
            )
            for descr in self.column_descriptions
        ])

    def as_recarray(self):
        pass


class NumpyQuery(NumpyQueryMixin, Query):
    pass
