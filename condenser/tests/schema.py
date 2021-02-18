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

    pk = Column(Integer, primary_key=True)
    col_int = Column(Integer, nullable=True)
    col_bool = Column(Boolean, nullable=True)
    col_str = Column(String(32), nullable=True)
    col_text = Column(Text, nullable=True)
    col_float = Column(Float, nullable=True)

    try:
        from geoalchemy2.types import Geometry

        col_geom = Column(
            Geometry(geometry_type="POINT", management=True), nullable=True
        )
        col_geom_4326 = Column(
            Geometry(geometry_type="POINT", management=True, srid=4326), nullable=True
        )
    except ImportError:
        pass
