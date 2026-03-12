# sqlalchemy-cubrid

CUBRID dialect for SQLAlchemy 2.0+.

[![CI](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml/badge.svg)](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-green.svg)](https://www.sqlalchemy.org/)
[![Coverage 99%](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](docs/DEVELOPMENT.md#code-coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Requirements

- Python 3.10+
- SQLAlchemy 2.0 – 2.1
- [CUBRID-Python](https://github.com/CUBRID/cubrid-python) driver

## Install

```bash
pip install sqlalchemy-cubrid
```

## Quick Start

```python
from sqlalchemy import create_engine, text

engine = create_engine("cubrid://dba:password@localhost:33000/demodb")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())
```

## Features

- Full SQLAlchemy 2.0 dialect with statement caching
- Complete type system — numeric, string, date/time, bit, LOB, and collection types
- SQL compilation — SELECT, JOIN, CAST, LIMIT/OFFSET, subqueries, CTEs, window functions
- DML extensions — `ON DUPLICATE KEY UPDATE`, `MERGE`, `FOR UPDATE`, `TRUNCATE`
- DDL support — `COMMENT`, `IF NOT EXISTS` / `IF EXISTS`, `AUTO_INCREMENT`
- Schema reflection — tables, views, columns, PKs, FKs, indexes, unique constraints, comments
- Alembic migrations via `CubridImpl` (auto-discovered entry point)
- All 6 CUBRID isolation levels
- PEP 561 typed package

## Documentation

| Guide | Description |
|---|---|
| **[Connection](docs/CONNECTION.md)** | Connection strings, URL format, driver setup, troubleshooting |
| **[Type Mapping](docs/TYPES.md)** | Full type mapping, CUBRID-specific types, collection types |
| **[DML Extensions](docs/DML_EXTENSIONS.md)** | ON DUPLICATE KEY UPDATE, MERGE, GROUP_CONCAT, TRUNCATE, index hints |
| **[Isolation Levels](docs/ISOLATION_LEVELS.md)** | All 6 CUBRID isolation levels, configuration, comparison |
| **[Alembic Migrations](docs/ALEMBIC.md)** | Setup, configuration, limitations, batch workarounds |
| **[Feature Support](docs/FEATURE_SUPPORT.md)** | Full comparison with MySQL, PostgreSQL, and SQLite |
| **[Development](docs/DEVELOPMENT.md)** | Dev setup, testing, Docker, coverage, CI/CD |

## Compatibility

| | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 |
|---|:---:|:---:|:---:|:---:|
| **Offline Tests** | ✅ | ✅ | ✅ | ✅ |
| **CUBRID 11.4** | ✅ | — | ✅ | — |
| **CUBRID 11.2** | ✅ | — | ✅ | — |
| **CUBRID 11.0** | ✅ | — | ✅ | — |
| **CUBRID 10.2** | ✅ | — | ✅ | — |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for dev setup.

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
