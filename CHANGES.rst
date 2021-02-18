Changelog of threedi-modelchecker
=================================

0.1.0 (unreleased)
------------------

- Basic project structure.

- Added ``NumpyQuery`` to override ``query_cls`` in the SQLAlchemy sessionmaker.

- Added ``NumpyQueryMixin`` to adapt existing custom query classes.

- Implemented ``NumpyQuery().numpy_dtype``.

- Implemented ``NumpyQuery().as_structarray``.

- Implemented ``NumpyQuery().with_numpy_cast_columns``.

- Implemented ``NumpyQuery().numpy_settings`` and 
  ``NumpyQuery.default_numpy_settings``.

- Enabled bulk reading of Boolean, Float, Integer, Numeric, String, Text.

- Added optional dependency ``condenser[geo]`` which enables bulk reading of
  Geometry columns through GeoAlchemy2 into an array of ``pygeos.Geometry``.

- Added ``NumpyQuery().with_transformed_geometries``.
