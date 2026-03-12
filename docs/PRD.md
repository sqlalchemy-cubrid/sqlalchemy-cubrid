# PRD: sqlalchemy-cubrid — CUBRID Dialect for SQLAlchemy 2.0

## 1. Overview

**Project**: sqlalchemy-cubrid  
**Version**: 1.0.0 (reboot)  
**Status**: Revival from abandoned 0.0.1 (SQLAlchemy 1.3 era)  
**Goal**: Production-ready CUBRID dialect for SQLAlchemy 2.0+

### 1.1 Problem Statement

The existing `sqlalchemy-cubrid` project is abandoned and broken:
- Targets SQLAlchemy < 1.4 (current is 2.0+)
- Uses deprecated APIs (`@reflection.cache`, `select._distinct`, `select._limit`, `basestring`)
- Has Python 2 remnants (`basestring`, `super()` with explicit args)
- Multiple bugs in compiler (missing `sql` import in `limit_clause`, broken CHAR type compiler)
- Incomplete reflection methods (foreign keys stub, broken PK constraint query)
- No CI pipeline that actually tests the dialect
- Cannot be installed on modern Python + SQLAlchemy environments

### 1.2 Success Criteria

1. **Installable**: `pip install sqlalchemy-cubrid` works on Python 3.9+
2. **Compatible**: Works with SQLAlchemy 2.0+ (specifically 2.0 - 2.1)
3. **Testable**: Unit tests pass without a live CUBRID instance (mock DBAPI layer)
4. **Complete**: All required dialect methods implemented (reflection, compilation, type system)
5. **CI/CD**: GitHub Actions runs tests on push/PR
6. **Publishable**: Can be published to PyPI via release workflow

---

## 2. Technical Architecture

### 2.1 Module Structure

```
sqlalchemy_cubrid/
├── __init__.py          # Public API exports, __version__
├── base.py              # IdentifierPreparer, ExecutionContext, reserved words
├── compiler.py          # SQLCompiler, DDLCompiler, TypeCompiler
├── dialect.py           # CubridDialect (main entry point)
├── types.py             # CUBRID-specific SQLAlchemy type objects
├── requirements.py      # Test suite requirements (feature flags)
└── provision.py         # Test provisioning (optional)

test/
├── __init__.py
├── conftest.py          # Dialect registration, pytest config
├── test_suite.py        # SQLAlchemy standard test suite
├── test_dialects.py     # CUBRID-specific dialect tests
└── test_compiler.py     # SQL compilation tests (no DB needed)
└── test_types.py        # Type mapping tests (no DB needed)
```

### 2.2 Dependency Matrix

| Package | Version | Purpose |
|---------|---------|---------|
| SQLAlchemy | >=2.0,<2.2 | Core ORM/engine framework |
| Python | >=3.9 | Runtime |
| CUBRID-Python | >=11.0 | DBAPI driver (optional, for live DB) |
| pytest | >=7.0 | Testing |
| ruff | >=0.4 | Linting + formatting |

### 2.3 Entry Points

```toml
[project.entry-points."sqlalchemy.dialects"]
cubrid = "sqlalchemy_cubrid.dialect:CubridDialect"
"cubrid.cubrid" = "sqlalchemy_cubrid.dialect:CubridDialect"
```

---

## 3. Component Specifications

### 3.1 Type System (`types.py`)

CUBRID data types mapped to SQLAlchemy type hierarchy:

| CUBRID Type | SQLAlchemy Base | Custom Class |
|-------------|-----------------|--------------|
| SHORT/SMALLINT | `sqltypes.SMALLINT` | `SMALLINT` |
| INTEGER | `sqltypes.INTEGER` | (use SA built-in) |
| BIGINT | `sqltypes.BIGINT` | `BIGINT` |
| NUMERIC(p,s) | `sqltypes.NUMERIC` | `NUMERIC` |
| DECIMAL(p,s) | `sqltypes.DECIMAL` | `DECIMAL` |
| FLOAT(p) | `sqltypes.FLOAT` | `FLOAT` |
| DOUBLE | `sqltypes.Float` | `DOUBLE` |
| DOUBLE PRECISION | `sqltypes.Float` | `DOUBLE_PRECISION` |
| DATE | `sqltypes.DATE` | (use SA built-in) |
| TIME | `sqltypes.TIME` | (use SA built-in) |
| TIMESTAMP | `sqltypes.TIMESTAMP` | (use SA built-in) |
| DATETIME | `sqltypes.DATETIME` | (use SA built-in) |
| BIT(n) | `sqltypes.TypeEngine` | `BIT` |
| BIT VARYING(n) | `sqltypes.TypeEngine` | `BIT` (varying=True) |
| CHAR(n) | `sqltypes.CHAR` | `CHAR` |
| VARCHAR(n) | `sqltypes.VARCHAR` | `VARCHAR` |
| NCHAR(n) | `sqltypes.NCHAR` | `NCHAR` |
| NCHAR VARYING(n) | `sqltypes.NVARCHAR` | `NVARCHAR` |
| STRING | `sqltypes.Text` | `STRING` |
| BLOB | `sqltypes.LargeBinary` | `BLOB` |
| CLOB | `sqltypes.Text` | `CLOB` |
| SET | `sqltypes.TypeEngine` | `SET` |
| MULTISET | `sqltypes.TypeEngine` | `MULTISET` |
| SEQUENCE/LIST | `sqltypes.TypeEngine` | `SEQUENCE` |

**Bugs to fix**:
- `REAL.__init__` calls `super(FLOAT, ...)` instead of `super(REAL, ...)`
- `_StringType.__repr__` uses deprecated `inspect.getargspec` (→ `inspect.getfullargspec` or remove)
- `basestring` reference in `compiler.py` `visit_list` (Python 2 only)

### 3.2 Compiler (`compiler.py`)

#### SQLCompiler
- `visit_sysdate_func` → `"SYSDATE"`
- `visit_utc_timestamp_func` → `"UTC_TIME()"`
- `visit_cast` → `"CAST(expr AS type)"` (fix missing space before AS)
- `render_literal_value` → escape backslashes
- `get_select_precolumns` → DISTINCT handling (SA 2.0 API: `select._distinct`)
- `visit_join` → INNER/LEFT OUTER JOIN
- `limit_clause` → `LIMIT offset, count` (SA 2.0: use `self._limit_clause`, `self._offset_clause`)
- `for_update_clause` → empty (CUBRID doesn't support SELECT ... FOR UPDATE)
- `update_limit_clause` → `LIMIT n`
- `update_tables_clause` → multi-table update
- `update_from_clause` → None (not supported)

**SA 2.0 breaking changes**:
- `select._distinct` → `select._distinct`  (still exists but check)
- `select._limit` / `select._offset` → `select._limit_clause` / `select._offset_clause`
- `self.process(sql.literal(x))` → `self.process(elements.literal(x))`
- Need to import `sql` module for `limit_clause` (currently missing import!)

#### DDLCompiler
- Implement `visit_create_table` if CUBRID has non-standard CREATE TABLE syntax
- Handle AUTO_INCREMENT (CUBRID uses `AUTO_INCREMENT(start, increment)`)

#### TypeCompiler
- All CUBRID types → SQL DDL strings
- Fix `visit_CHAR`: missing closing paren `f"CHAR({type_.length}"` → `f"CHAR({type_.length})"`

### 3.3 Dialect (`dialect.py`)

#### Core Configuration
```python
class CubridDialect(default.DefaultDialect):
    name = "cubrid"
    driver = "cubrid"
    
    supports_alter = True
    supports_native_enum = False
    supports_native_boolean = True
    supports_native_decimal = True
    supports_sequences = False
    supports_default_values = False
    supports_default_metavalue = False
    supports_empty_insert = False
    supports_multivalues_insert = True
    supports_comments = False
    supports_is_distinct_from = False
    postfetch_lastrowid = False
    requires_name_normalize = True
    
    default_paramstyle = "qmark"
    max_identifier_length = 254
```

#### Reflection Methods (Required)

| Method | Status | Notes |
|--------|--------|-------|
| `get_columns()` | Needs fix | Type parsing regex bugs |
| `get_pk_constraint()` | Broken | Wrong SQL (f-string not interpolated) |
| `get_foreign_keys()` | Stub | Must implement with `db_constraint` |
| `get_table_names()` | Works | Minor cleanup |
| `get_view_names()` | Works | Minor cleanup |
| `get_view_definition()` | Works | |
| `get_indexes()` | Needs fix | Variable shadowing (`result` reused) |
| `get_unique_constraints()` | Stub | Should use index introspection |
| `has_table()` | Works | SQL injection risk (f-string) |
| `has_sequence()` | Missing | Return False always |
| `get_schema_names()` | Missing | Implement |
| `get_table_comment()` | Missing | Implement or return empty |
| `get_check_constraints()` | Missing | Implement or return empty |

#### SA 2.0 Reflection API Changes
- Remove `@reflection.cache` decorator → use `@reflection.cache` (still exists in SA 2.0 but signature changed)
- All reflection methods must use `connection.execute(text(...))` 
- Parameterize SQL queries (prevent SQL injection in `has_table`, `get_pk_constraint`)

#### Connection
```python
def create_connect_args(self, url):
    # CUBRID connection string format:
    # CUBRID:host:port:db_name:db_user:db_password:::
    opts = url.translate_connect_args()
    connect_url = f"CUBRID:{opts['host']}:{opts['port']}:{opts['database']}:::"
    return ([connect_url, opts['username'], opts['password']], {})
```

### 3.4 Base (`base.py`)

#### IdentifierPreparer
- Reserved words list (keep current, verify against CUBRID 11)
- Double-quote identifier quoting
- `_quote_free_identifiers` helper

#### ExecutionContext
- `should_autocommit_text` for DML detection
- Remove explicit `__init__` (unnecessary override)

---

## 4. Testing Strategy

### 4.1 Unit Tests (No DB Required)

| Test File | Coverage |
|-----------|----------|
| `test_compiler.py` | SQL compilation output for SELECT, INSERT, UPDATE, DELETE, DDL |
| `test_types.py` | Type compilation (TypeCompiler → DDL strings) |
| `test_dialects.py` | Connection string building, dialect configuration |

### 4.2 Integration Tests (Requires CUBRID)

| Test File | Coverage |
|-----------|----------|
| `test_suite.py` | SQLAlchemy standard dialect test suite |

### 4.3 Mock DBAPI

Create a lightweight mock of CUBRIDdb for offline testing:
```python
# test/mock_cubriddb.py
class MockCursor:
    def execute(self, stmt, params=None): ...
    def fetchone(self): ...
    def fetchall(self): ...
    
class MockConnection:
    def cursor(self): return MockCursor()
    def close(self): ...
```

---

## 5. Migration Checklist (SA 1.3 → SA 2.0)

- [ ] Replace `super(ClassName, self).__init__()` → `super().__init__()`
- [ ] Replace `basestring` → `str`
- [ ] Replace `inspect.getargspec` → `inspect.getfullargspec`
- [ ] Fix `select._limit` → `select._limit_clause`
- [ ] Fix `select._offset` → `select._offset_clause`
- [ ] Add missing `sql` import in compiler `limit_clause`
- [ ] Fix CAST compiler: add space before AS
- [ ] Fix CHAR TypeCompiler: missing closing paren
- [ ] Fix REAL type: `super(FLOAT, ...)` → `super(REAL, ...)`
- [ ] Fix `get_pk_constraint`: use text() and f-string interpolation
- [ ] Fix `get_indexes`: don't shadow `result` variable
- [ ] Parameterize all SQL in reflection methods (prevent injection)
- [ ] Remove `from cmd import IDENTCHARS` (unused import)
- [ ] Update entry points format for modern setuptools
- [ ] Add `import_dbapi()` classmethod (SA 2.0 prefers over `dbapi()`)

---

## 6. Release Plan

### v1.0.0 — Revival Release
- Full SQLAlchemy 2.0 compatibility
- All reflection methods implemented
- Unit tests passing without live DB
- Modern Python packaging (pyproject.toml)
- GitHub Actions CI

### v1.1.0 — Future
- Alembic migration support
- CUBRID-specific DDL (AUTO_INCREMENT syntax)
- Performance optimization for reflection
- Support for CUBRID 12 features

---

## 7. Known Limitations

1. **CUBRID-Python driver**: May not be actively maintained. The dialect should gracefully handle ImportError.
2. **No FOR UPDATE**: CUBRID doesn't support `SELECT ... FOR UPDATE` locking.
3. **No RETURNING**: CUBRID doesn't support `INSERT ... RETURNING`.
4. **No DEFAULT VALUES**: `INSERT INTO t DEFAULT VALUES` not supported.
5. **Boolean type**: CUBRID uses SMALLINT for booleans.
6. **Transaction isolation**: CUBRID has unique isolation level naming.
