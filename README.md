sqlalchemy-cubrid
=================

CUBRID dialect for SQLAlchemy 2.0+.

[![CI](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml/badge.svg)](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml)
[![lint](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/pre-commit.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-green.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Requirements
------------

- Python 3.10+
- SQLAlchemy 2.0 – 2.1
- [CUBRID-Python](https://github.com/CUBRID/cubrid-python) driver


Quick Start
-----------

Install the library:

```bash
pip install sqlalchemy-cubrid
```

Install the CUBRID Python driver (if not already installed):

```bash
pip install CUBRID-Python
```


Usage
-----

```python
from sqlalchemy import create_engine, text

engine = create_engine("cubrid://dba:password@localhost:33000/demodb")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())
```

The dialect registers two entry points:
- `cubrid://` (default)
- `cubrid+cubrid://` (explicit)


Features
--------

- Full SQLAlchemy 2.0 dialect interface
- Statement caching (`supports_statement_cache = True`)
- Type system: all CUBRID numeric, string, date/time, bit, LOB, and collection types
- SQL compilation: SELECT, JOIN, CAST, LIMIT/OFFSET, UPDATE with LIMIT
- `FOR UPDATE` clause (`SELECT … FOR UPDATE [OF col1, col2]`)
- `ON DUPLICATE KEY UPDATE` via CUBRID-specific `insert()` construct
- `MERGE` statement via `merge()` construct with full WHEN MATCHED/NOT MATCHED support
- Window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, etc.) with `OVER()`
- `NULLS FIRST` / `NULLS LAST` in ORDER BY
- `INSERT … DEFAULT VALUES` and empty inserts
- Table and column `COMMENT` support (inline DDL + ALTER + reflection)
- `IF NOT EXISTS` / `IF EXISTS` DDL for CREATE TABLE and DROP TABLE
- `GROUP_CONCAT` aggregate function
- `TRUNCATE TABLE` with autocommit detection
- Reflection: tables, views, columns, primary keys, foreign keys, indexes, unique constraints
- Isolation level management (all 6 CUBRID isolation levels)
- Connection string translation to CUBRID format (`CUBRID:host:port:db:::`)
- PEP 561 typed package (`py.typed`)


Type Mapping
------------

### Standard SQL Types

| Python / SQLAlchemy Type | CUBRID SQL Type | Notes |
|---|---|---|
| `Integer` | `INTEGER` | 32-bit signed integer |
| `SmallInteger` | `SMALLINT` | 16-bit signed integer |
| `BigInteger` | `BIGINT` | 64-bit signed integer |
| `Float` | `FLOAT` | 7-digit precision |
| `Double`, `REAL` | `DOUBLE` | 15-digit precision |
| `Numeric(p, s)` | `NUMERIC(p, s)` | Exact numeric, up to 38 digits |
| `String(n)` | `VARCHAR(n)` | Variable-length character data |
| `Text` | `STRING` | Alias for `VARCHAR(1,073,741,823)` |
| `Unicode(n)` | `NVARCHAR(n)` | National character set |
| `UnicodeText` | `NVARCHAR` | National character, max length |
| `LargeBinary` | `BLOB` | Binary Large Object |
| `Boolean` | `SMALLINT` | ⚠️ No native boolean; mapped to 0/1 |
| `Date` | `DATE` | |
| `Time` | `TIME` | |
| `DateTime` | `DATETIME` | |
| `TIMESTAMP` | `TIMESTAMP` | |

### CUBRID-Specific Types

```python
from sqlalchemy_cubrid import (
    # Numeric
    SMALLINT, BIGINT, NUMERIC, DECIMAL, FLOAT, REAL,
    DOUBLE, DOUBLE_PRECISION,
    # String
    CHAR, VARCHAR, NCHAR, NVARCHAR, STRING,
    # Binary
    BIT,
    # LOB
    BLOB, CLOB,
    # Collections
    SET, MULTISET, SEQUENCE,
)
```

| CUBRID Type | Description |
|---|---|
| `STRING` | `VARCHAR(1,073,741,823)` — max-length variable string |
| `BIT(n)` / `BIT VARYING(n)` | Fixed/variable-length bit strings |
| `CLOB` | Character Large Object |
| `SET(type)` | Unordered collection of unique elements |
| `MULTISET(type)` | Unordered collection allowing duplicates |
| `SEQUENCE(type)` | Ordered collection allowing duplicates |


Isolation Levels
----------------

CUBRID supports six isolation levels — more than the SQL standard's four:

| Level | Constant |
|---|---|
| 6 | `SERIALIZABLE` |
| 5 | `REPEATABLE READ` |
| 4 | `READ COMMITTED` (default) |
| 3 | `REPEATABLE READ CLASS, READ UNCOMMITTED INSTANCES` |
| 2 | `READ COMMITTED CLASS, READ COMMITTED INSTANCES` |
| 1 | `READ COMMITTED CLASS, READ UNCOMMITTED INSTANCES` |

```python
engine = create_engine(
    "cubrid://dba@localhost:33000/testdb",
    isolation_level="REPEATABLE READ",
)
```


Known Limitations
-----------------

| Feature | Status | Reason |
|---|---|---|
| `RETURNING` clause | ❌ | CUBRID does not support `RETURNING` |
| Native `BOOLEAN` | ⚠️ | Mapped to `SMALLINT` |
| `JSON` type | ❌ | No JSON data type in CUBRID |
| `ARRAY` type | ❌ | Use `SET`/`MULTISET`/`SEQUENCE` instead |
| Sequences | ❌ | CUBRID uses `AUTO_INCREMENT` |
| Multi-schema | ❌ | Single-schema model |
| Temporary tables | ❌ | Not confirmed in CUBRID |
| `IS DISTINCT FROM` | ❌ | Not supported by CUBRID |
| Alembic migrations | ✅ | Supported via `alembic_cubrid` implementation |

For a detailed feature-by-feature comparison with MySQL, PostgreSQL, and SQLite,
see [Feature Support Comparison](docs/FEATURE_SUPPORT.md).


Compatibility Matrix
--------------------

| | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 |
|---|:---:|:---:|:---:|:---:|
| **Offline Tests** | ✅ | ✅ | ✅ | ✅ |
| **CUBRID 11.4** | ✅ | — | ✅ | — |
| **CUBRID 11.2** | ✅ | — | ✅ | — |
| **CUBRID 11.0** | ✅ | — | ✅ | — |
| **CUBRID 10.2** | ✅ | — | ✅ | — |

Integration tests run against live CUBRID Docker instances in CI.


Development
-----------

### Quick Start

```bash
# Clone and install
git clone https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid.git
cd sqlalchemy-cubrid
make install
```

### Using Make Targets

```bash
make help          # Show all available targets
make lint          # Run ruff linter + format checks
make format        # Auto-fix lint and format code
make test          # Run offline tests with coverage (95% threshold)
make test-all      # Run tox across all Python versions
make integration   # Start Docker, run integration tests, stop Docker
make docker-up     # Start CUBRID Docker container
make docker-down   # Stop and remove CUBRID Docker container
make clean         # Remove build artifacts
```

### Manual Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run offline tests (no CUBRID instance needed)
pytest test/ -v --ignore=test/test_integration.py --ignore=test/test_suite.py

# Run with coverage
pytest test/ -v --ignore=test/test_integration.py --ignore=test/test_suite.py \
  --cov=sqlalchemy_cubrid --cov-report=term-missing

# Run integration tests (requires CUBRID instance)
docker compose up -d
export CUBRID_TEST_URL="cubrid://dba@localhost:33000/testdb"
pytest test/test_integration.py -v

# Run full SA test suite (requires CUBRID instance)
pytest --dburi cubrid://dba@localhost:33000/testdb

# Lint
ruff check sqlalchemy_cubrid/ test/
ruff format sqlalchemy_cubrid/ test/
```

### Docker

A `docker-compose.yml` is provided for local development:

```bash
# Start with default CUBRID version (11.2)
docker compose up -d

# Start with a specific version
CUBRID_VERSION=11.4 docker compose up -d
```


Contributing
------------

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing instructions,
and pull request guidelines.


Security
--------

To report a security vulnerability, see [SECURITY.md](SECURITY.md).


License
-------

MIT License. See [LICENSE](LICENSE) for details.
