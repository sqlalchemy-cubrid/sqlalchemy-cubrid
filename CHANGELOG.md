# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
