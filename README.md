# sqlalchemy-cubrid

**CUBRID dialect for SQLAlchemy 2.0+**

[🇺🇸 English](README.md) · [🇨🇳 中文](docs/README.zh.md) · [🇮🇳 हिन्दी](docs/README.hi.md) · [🇩🇪 Deutsch](docs/README.de.md) · [🇷🇺 Русский](docs/README.ru.md)

[![PyPI](https://img.shields.io/pypi/v/sqlalchemy-cubrid.svg)](https://pypi.org/project/sqlalchemy-cubrid/)
[![CI](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml/badge.svg)](https://github.com/sqlalchemy-cubrid/sqlalchemy-cubrid/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-green.svg)](https://www.sqlalchemy.org/)
[![Coverage 99%](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](docs/DEVELOPMENT.md#code-coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why sqlalchemy-cubrid?

CUBRID is a high-performance open-source relational database, widely adopted in
Korean public-sector and enterprise applications. Until now, there was no
production-ready SQLAlchemy dialect that supports the modern 2.0 API.

**sqlalchemy-cubrid** bridges that gap:

- Full SQLAlchemy 2.0 dialect with **statement caching** and **PEP 561 typing**
- **426 offline tests** with **99%+ code coverage** — no database required to run them
- Tested against **4 CUBRID versions** (10.2, 11.0, 11.2, 11.4) across **Python 3.10 -- 3.13**
- CUBRID-specific DML constructs: `ON DUPLICATE KEY UPDATE`, `MERGE`, `REPLACE INTO`
- Alembic migration support out of the box
- **Two driver options** — C-extension (`cubrid://`) or pure Python (`cubrid+pycubrid://`)

## Requirements

- Python 3.10+
- SQLAlchemy 2.0 – 2.1
- [CUBRID-Python](https://github.com/CUBRID/cubrid-python) (C-extension) **or** [pycubrid](https://github.com/sqlalchemy-cubrid/pycubrid) (pure Python)

## Installation

```bash
pip install sqlalchemy-cubrid
```

With the pure Python driver (no C build needed):

```bash
pip install "sqlalchemy-cubrid[pycubrid]"
```

With Alembic support:

```bash
pip install "sqlalchemy-cubrid[alembic]"
```

## Quick Start

### Core (Connection-Level)

```python
from sqlalchemy import create_engine, text

engine = create_engine("cubrid://dba:password@localhost:33000/demodb")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())
```

### ORM (Session-Level)

```python
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)


engine = create_engine("cubrid://dba:password@localhost:33000/demodb")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
```

## Features

- Complete type system -- numeric, string, date/time, bit, LOB, and collection types
- SQL compilation -- SELECT, JOIN, CAST, LIMIT/OFFSET, subqueries, CTEs, window functions
- DML extensions -- `ON DUPLICATE KEY UPDATE`, `MERGE`, `REPLACE INTO`, `FOR UPDATE`, `TRUNCATE`
- DDL support -- `COMMENT`, `IF NOT EXISTS` / `IF EXISTS`, `AUTO_INCREMENT`
- Schema reflection -- tables, views, columns, PKs, FKs, indexes, unique constraints, comments
- Alembic migrations via `CubridImpl` (auto-discovered entry point)
- All 6 CUBRID isolation levels (dual-granularity: class-level + instance-level)

## Documentation

| Guide | Description |
|---|---|
| [Connection](docs/CONNECTION.md) | Connection strings, URL format, driver setup, pool tuning |
| [Type Mapping](docs/TYPES.md) | Full type mapping, CUBRID-specific types, collection types |
| [DML Extensions](docs/DML_EXTENSIONS.md) | ON DUPLICATE KEY UPDATE, MERGE, REPLACE INTO, query trace |
| [Isolation Levels](docs/ISOLATION_LEVELS.md) | All 6 CUBRID isolation levels, configuration |
| [Alembic Migrations](docs/ALEMBIC.md) | Setup, configuration, limitations, batch workarounds |
| [Feature Support](docs/FEATURE_SUPPORT.md) | Comparison with MySQL, PostgreSQL, SQLite |
| [ORM Cookbook](docs/ORM_COOKBOOK.md) | Practical ORM examples, relationships, queries |
| [Development](docs/DEVELOPMENT.md) | Dev setup, testing, Docker, coverage, CI/CD |
| [Driver Compatibility](docs/DRIVER_COMPAT.md) | CUBRID-Python driver versions and known issues |

## Compatibility

| | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 |
|---|:---:|:---:|:---:|:---:|
| **Offline Tests** | ✅ | ✅ | ✅ | ✅ |
| **CUBRID 11.4** | ✅ | -- | ✅ | -- |
| **CUBRID 11.2** | ✅ | -- | ✅ | -- |
| **CUBRID 11.0** | ✅ | -- | ✅ | -- |
| **CUBRID 10.2** | ✅ | -- | ✅ | -- |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for development setup.

## Security

Report vulnerabilities via email -- see [SECURITY.md](SECURITY.md). Do not open public issues for security concerns.

## License

MIT -- see [LICENSE](LICENSE).
