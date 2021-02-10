from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TestModel(Base):
    __tablename__ = "test_table"

    col_int = Column(Integer, primary_key=True)
    col_str = Column(String)
    col_float = Column(Float)
