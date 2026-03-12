sqlalchemy-cubrid
==================

CUBRID dialect for SQLAlchemy 2.0+.

This package provides a full-featured SQLAlchemy dialect for the `CUBRID <https://www.cubrid.org/>`_
relational database. It supports SQL compilation, type mapping, schema reflection,
DDL generation, DML extensions (``ON DUPLICATE KEY UPDATE``, ``MERGE``),
window functions, Alembic migrations, and more.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   sqlalchemy_cubrid


Quick Start
^^^^^^^^^^^

Install::

   pip install sqlalchemy-cubrid

Usage:

.. code-block:: python

   from sqlalchemy import create_engine, text

   engine = create_engine("cubrid://dba:password@localhost:33000/demodb")

   with engine.connect() as conn:
       result = conn.execute(text("SELECT 1"))
       print(result.scalar())


Links
^^^^^

- `GitHub Repository <https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid>`_
- `Feature Support Matrix <https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/blob/main/docs/FEATURE_SUPPORT.md>`_
- `Changelog <https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/blob/main/CHANGELOG.md>`_
- `CUBRID Documentation <https://www.cubrid.org/manual/en/11.2/>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
