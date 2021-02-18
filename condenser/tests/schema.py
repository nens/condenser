from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModelOne(Base):
    __tablename__ = "test_table"

    col_int = Column(Integer, primary_key=True)
    col_bool = Column(Boolean)
    col_str = Column(String(32))
    col_text = Column(Text)
    col_float = Column(Float)

    try:
        from geoalchemy2.types import Geometry

        col_geom = Column(Geometry(geometry_type="POINT", management=True))
        col_geom_4326 = Column(
            Geometry(geometry_type="POINT", management=True, srid=4326)
        )
    except ImportError:
        pass
