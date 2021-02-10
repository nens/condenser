from sqlalchemy.orm.query import Query


class NumpyQueryMixin:
    def as_recarray(self):
        pass


class NumpyQuery(NumpyQueryMixin, Query):
    pass
