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

This project reads data from SQLAlchemy into structured numpy arrays. Next to
the builtin SQLAlchemy types, it also supports reading geometries into ``pygeos``
arrays of geometries.

Installation
------------

Install via pip using::

$ pip install condenser

Include geometry support::

$ pip install condenser[geo]

Usage
-----

``condenser`` exposes one object: ``NumpyQuery``, which is used
as a custom SQLAlchemy query class as follows::

>>> from condenser import NumpyQuery
>>> # create the session with a custom query class
>>> session = session_factory(query_cls=NumpyQuery)

If a session is constructed like that, every query object will have an
additional method to dump the selected data into a numpy structured array::

>>> query = session.query(SomeModel.float_type_column, SomeModel.int_type_column)
>>> my_array = query.as_structarray()

Geometry support
----------------

Geometry columns are automatically converted to arrays of ``pygeos.Geometry``
objects. See https://pygeos.readthedocs.io on for (vectorized) numpy functions
that can act on these arrays.

Transform geometries (using the `ST_Transform` database function) as follows::

>>> query.with_transformed_geometries(target_srid=28992)

Note that this will only transform geometries with a known SRID. If an SRID is
known only from another metadata source, use a function appropriate to your
database backend to set the projection before converting it. Another option
is using the ``pyproj`` library in combination with ``pygeos.apply`` to
transform geometries from Python.


Custom dtype mapping
--------------------

`condenser` has a safe approach on guessing the Numpy dtypes from SQLAlchemy
dtypes. It always takes 8-byte signed integers and floats. For some database
backends this can be changed to for example 4-byte datatypes.
Override an SQLAlchemy to NumPy type mapping after constructing the query::

>>> from sqlalchemy import Integer
>>> query = session.query(SomeModel.float_type_column)
>>> query.numpy_settings[Integer]["dtype"] = np.int32
>>> query.as_structarray()

Or globally::

>>> NumpyQuery.default_numpy_settings[Integer]["dtype"] = np.int32

NULL values
-----------

Most numpy datatypes handle NULL (Python: None) values natively. Only integer
typed columns deserve extra attention as they have no equivalent in the NumPy
integer dtype. This package converts NULLs in integer columns to `-1` by
default. A complete list of what to expect:

- NULL in integer columns becomes `-1`
- NULL in float and numeric columns becomes `nan`
- NULL in boolean columns becomes `False`
- NULL in object typed columns (string, text, geometry) becomes `None`

Adjust the NULL value before executing the query::

>>> from sqlalchemy import Integer
>>> query = session.query(SomeModel.float_type_column)
>>> query.numpy_settings[Integer]["null"] = -9999
>>> query.numpy_settings[Boolean]["null"] = True
>>> query.as_structarray()

Or globally::

>>> NumpyQuery.default_numpy_settings[Integer]["null"] = -9999

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
