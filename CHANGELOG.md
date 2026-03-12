# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-03-12

### Added
- **Error code mapping**: `is_disconnect()` detects dropped connections via string-based message
  matching (14 patterns) and numeric CUBRID CCI error codes (-21003, -21005, -10005, -10007).
- **`_extract_error_code()`**: Extracts numeric error codes from CUBRID DBAPI exceptions
  (supports both integer args and string-embedded codes like "-21003 message").
- **`do_ping()`**: Connection liveness check using CUBRID Python driver's native `ping()`
  method — enables SQLAlchemy's `pool_pre_ping` feature.
- **Connection pool tuning guide**: `docs/CONNECTION.md` expanded with pool configuration
  recommendations (`pool_size`, `pool_recycle`, `pool_pre_ping`), CUBRID broker timeout
  interaction, disconnect detection, and error code mapping documentation.
- **CUBRID-Python driver compatibility matrix**: `docs/DRIVER_COMPAT.md` documenting tested
  driver versions, CUBRID server compatibility, and known issues.
- **Python 3.14 support**: Added to CI matrix and `pyproject.toml` classifiers.
- **44 new offline tests**: Comprehensive coverage for `is_disconnect()` (14 message patterns,
  4 error codes, edge cases), `_extract_error_code()` (7 tests), `do_ping()` (2 tests),
  `postfetch_lastrowid` validation (5 tests), and disconnect message integrity (3 tests).

### Changed
- CI integration test matrix expanded: Python {3.10, 3.12, 3.14} × CUBRID {11.4, 11.2, 11.0, 10.2}.
- `pyproject.toml`: Added `Programming Language :: Python :: 3.14` classifier.


## [1.2.2] - 2026-03-12

### Added
- `docs/CONNECTION.md`: Connection guide — URL format, driver setup, troubleshooting.
- `docs/TYPES.md`: Type mapping reference — standard types, CUBRID-specific types, collection types, boolean handling.
- `docs/ISOLATION_LEVELS.md`: Isolation level guide — all 6 CUBRID levels, dual-granularity model, configuration.
- `docs/DML_EXTENSIONS.md`: DML extensions reference — ON DUPLICATE KEY UPDATE, MERGE, GROUP_CONCAT, TRUNCATE, FOR UPDATE, index hints.
- `docs/ALEMBIC.md`: Alembic migration guide — setup, configuration, limitations, batch workarounds.
- `docs/DEVELOPMENT.md`: Development guide — setup, testing, Docker, coverage, CI/CD pipeline.

### Changed
- `README.md`: Rewritten as a concise landing page (~80 lines); all detailed content moved to `docs/` files.
- `docs/source/index.rst`: Added links to all new documentation files.
- `docs/FEATURE_SUPPORT.md`: Updated version reference from v1.2.0 to v1.2.2.


## [1.2.1] - 2026-03-12

### Fixed
- README: Fixed lint badge referencing deleted `pre-commit.yml` workflow — now points to `ci.yml`.
- SECURITY.md: Added v1.1.x and v1.2.x to supported versions table.
- `docs/source/index.rst`: Replaced Sphinx quickstart boilerplate with proper project documentation.
- `docs/source/conf.py`: Updated version to 1.2.0, added `viewcode` and `intersphinx` extensions.
- `docs/source/sqlalchemy_cubrid.rst`: Added `dml` and `alembic_impl` module autodoc sections.
- `samples/create_engine.py`: Modernized to SA 2.0 API (`text()`, context manager).
- `samples/cubrid_datatypes.py`: Modernized to SA 2.0 API (`metadata.create_all`, CUBRID types).
- `samples/env.sample`: Replaced hardcoded external IP with `localhost`.

### Removed
- Removed legacy files superseded by `pyproject.toml`: `setup.py`, `setup.cfg`, `CHANGES.rst`, `requirements.txt`, `requirements-dev.txt`, `install_cubrid_python.sh`.
- Removed duplicate `pre-commit.yml` GitHub Actions workflow (functionality covered by `ci.yml`).
## [1.2.0] - 2026-03-12

### Added
- Alembic migration support via `CubridImpl` (`alembic.ddl` entry-point).
  Install with `pip install sqlalchemy-cubrid[alembic]`.
- `test/test_alembic.py`: 8 tests covering import, registry, entry-point, and import-error scenarios.

### Changed
- Edge-case tests added for compiler.py, dml.py, and dialect.py — coverage raised from 97% to 99% (306 → 314 tests).
- `docs/FEATURE_SUPPORT.md`: Alembic row updated from ❌ to ✅.

## [1.1.0] - 2026-03-12

### Added
- `FOR UPDATE` clause support (`SELECT … FOR UPDATE [OF col1, col2]`).
- `INSERT … DEFAULT VALUES` and empty INSERT support.
- Window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `LEAD`, etc.) with `OVER()` clause.
- `NULLS FIRST` / `NULLS LAST` ordering in ORDER BY.
- Table and column `COMMENT` support — inline DDL, `ALTER` statements, and schema reflection.
- `IF NOT EXISTS` / `IF EXISTS` DDL support for `CREATE TABLE` and `DROP TABLE`.
- `ON DUPLICATE KEY UPDATE` via CUBRID-specific `sqlalchemy_cubrid.insert()` construct (MySQL-compatible syntax).
- `MERGE` statement via `sqlalchemy_cubrid.merge()` with full `WHEN MATCHED` / `WHEN NOT MATCHED` clause support.
- `GROUP_CONCAT` aggregate function compilation.
- `TRUNCATE TABLE` autocommit detection.
- Index hint documentation (`USING INDEX`, `USE INDEX`, `FORCE INDEX`, `IGNORE INDEX` via SQLAlchemy’s built-in `with_hint()` / `suffix_with()`).
- `docs/FEATURE_SUPPORT.md`: Comprehensive feature support matrix updated with all new capabilities.

## [1.0.0] - 2026-03-12

### Changed
- **BREAKING**: Minimum Python version raised from 3.6 to 3.10.
- **BREAKING**: Minimum SQLAlchemy version raised from 1.3 to 2.0.
- Complete rewrite of all dialect modules for SQLAlchemy 2.0 compatibility.
- Modernized project infrastructure (`pyproject.toml`, ruff linting, GitHub Actions CI).

### Fixed
- `compiler.py`: Fixed `visit_cast` missing space before `AS` keyword (`CAST(exprAS type)` → `CAST(expr AS type)`).
- `compiler.py`: Fixed `visit_CHAR` missing closing parenthesis.
- `compiler.py`: Fixed `visit_list` using Python 2 `basestring` — crashes on Python 3.
- `compiler.py`: Fixed `limit_clause` using `sql.literal()` without importing `sql` module.
- `compiler.py`: Fixed `limit_clause` for SA 2.0 (`_limit_clause` / `_offset_clause` are now ClauseElements).
- `types.py`: Fixed `REAL.__init__` calling `super(FLOAT, self)` instead of `super(REAL, self)`.
- `types.py`: Fixed `_StringType.__repr__` using `inspect.getargspec` removed in Python 3.11+.
- `dialect.py`: Fixed `get_pk_constraint` using string literal instead of f-string and missing `text()`.
- `dialect.py`: Fixed `get_indexes` shadowing outer `result` variable inside loop.
- `dialect.py`: Fixed `has_table` SQL injection via f-string interpolation — now uses parameterized query.
- `dialect.py`: Fixed `get_foreign_keys` empty stub — now queries `db_constraint` system table.
- `dialect.py`: Fixed `postfetch_lastrowid = False` → `True` so SA can retrieve auto-generated keys.
- `dialect.py`: Fixed CUBRID driver defaulting to `autocommit=True` — `on_connect()` now calls `conn.set_autocommit(False)`.
- `dialect.py`: Removed unused `from cmd import IDENTCHARS` import.
- `base.py`: Implemented `CubridExecutionContext.get_lastrowid()` using `conn.get_last_insert_id()` with `SELECT LAST_INSERT_ID()` fallback.
- All files: Modernized `super(ClassName, self).__init__()` to `super().__init__()`.

### Added
- `dialect.py`: `import_dbapi()` classmethod (SA 2.0 API).
- `dialect.py`: `supports_statement_cache = True` for SA 2.0 query caching.
- `dialect.py`: `supports_comments`, `supports_is_distinct_from`, `insert_returning`, `update_returning`, `delete_returning` flags.
- `dialect.py`: `get_schema_names()`, `get_table_comment()`, `get_check_constraints()`, `has_sequence()` methods.
- `dialect.py`: `get_unique_constraints()` now queries `db_constraint` system table.
- `dialect.py`: `get_isolation_level_values()` method (SA 2.0 API).
- `dialect.py`: `do_release_savepoint()` no-op override — CUBRID does not support `RELEASE SAVEPOINT`.
- `compiler.py`: `CubridDDLCompiler.get_column_specification()` for proper `AUTO_INCREMENT` DDL emission.
- `requirements.py`: Comprehensive SA 2.0 test requirement flags (40+ properties), including binary, LOB, identifier quoting, and FOR UPDATE skip markers.
- `test/test_compiler.py`: 70 offline SQL compilation tests.
- `test/test_types.py`: 48 offline type system tests.
- `test/test_requirements.py`: 46 parametrized requirement flag tests.
- `test/test_dialect_offline.py`: 24 offline dialect tests (reflection, connection, isolation, savepoint).
- `test/test_base.py`: 15 base module tests.
- `test/test_integration.py`: 20 integration tests against live CUBRID Docker instances.
- `.github/workflows/ci.yml`: Full CI/CD pipeline with Python × CUBRID version matrix.
- `CHANGELOG.md`: This file.
- `docs/PRD.md`: Product requirements document.
- `docs/FEATURE_SUPPORT.md`: Feature-by-feature comparison with MySQL, PostgreSQL, and SQLite.

### Removed
- `.pre-commit-config.yaml`: Replaced by ruff configuration in `pyproject.toml`.

## [0.0.1] - 2022-01-01

### Added
- Initial release with basic CUBRID dialect for SQLAlchemy 1.3.
