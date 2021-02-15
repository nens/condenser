=========
condenser
=========

.. image:: https://github.com/nens/condenser/workflows/Linux/badge.svg
        :target: https://github.com/nens/condenser/actions?query=workflow%3ALinux

.. image:: https://img.shields.io/pypi/v/condenser.svg
        :target: https://pypi.python.org/pypi/condenser

A fast interface between SQLAlchemy and Numpy

Features
--------

This project aims to read data from SQLAlchemy into structured numpy arrays.
It provides this function by exposing one object: ``NumpyQuery``, which is used
as a custom SQLAlchemy query class as follows::

>>> from condenser import NumpyQuery
>>> # create the session with a custom query class
>>> session = session_factory(query_cls=NumpyQuery)

If a session is constructed like that, every query object will have an
additional method to dump the selected data into a numpy structured array::

>>> query = session.query(SomeModel.float_type_column, SomeModel.int_type_column)
>>> my_array = query.as_structarray()


Custom dtype mapping
--------------------

Condenser has a safe approach on guessing the Numpy dtypes from SQLAlchemy
dtypes. It always takes 8-byte signed integers and floats. For some database
backends this could be more strict. Override the type mapping after constructing
the query::

>>> from sqlalchemy import Integer
>>> query = session.query(SomeModel.float_type_column)
>>> NumpyQuery.numpy_settings[Integer]["dtype"] = np.int32

Or globally::

>>> NumpyQuery.default_numpy_settings[Integer]["dtype"] = np.int32


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
