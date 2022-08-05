sqlalchemy-cubrid
=================

CUBRID dialect for SQLAlchemy.


Quick Start
-----------
Install the sqlalchemy-cubird library.

```bash
pip install sqlalchemy-cubrid
```

This dialect requires ``CUBRID-Python``.


Usage
-----

```python
engine = create_engine("cubrid://dba:1234@localhost:33000/demodb"
connection = engine.connect()
```

Tests
-----

```python
py.test --dburi:cubrid://user:password@host:port
```