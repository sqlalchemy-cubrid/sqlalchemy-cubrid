# Feature Support Comparison

A comprehensive comparison of **sqlalchemy-cubrid** capabilities against the mature SQLAlchemy dialects for MySQL, PostgreSQL, and SQLite.

Use this document to understand what the CUBRID dialect supports, what it doesn't, and how it compares to other database backends when choosing a dialect for your project.

---

## Table of Contents

- [Legend](#legend)
- [Summary](#summary)
- [DML — Data Manipulation Language](#dml--data-manipulation-language)
- [DDL — Data Definition Language](#ddl--data-definition-language)
- [Query Features](#query-features)
- [Type System](#type-system)
- [Schema Reflection](#schema-reflection)
- [Transactions & Connections](#transactions--connections)
- [Dialect Engine Features](#dialect-engine-features)
- [CUBRID-Specific Features](#cubrid-specific-features)
- [Known Limitations & Roadmap](#known-limitations--roadmap)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully supported |
| ⚠️ | Partial or emulated support |
| ❌ | Not supported |

---

## Summary

High-level overview by feature category.

| Category | CUBRID | MySQL | PostgreSQL | SQLite |
|----------|--------|-------|------------|--------|
| DML | ⚠️ | ✅ | ✅ | ⚠️ |
| DDL | ⚠️ | ✅ | ✅ | ⚠️ |
| Query features | ⚠️ | ✅ | ✅ | ✅ |
| Type system | ⚠️ | ✅ | ✅ | ⚠️ |
| Schema reflection | ⚠️ | ✅ | ✅ | ⚠️ |
| Transactions | ✅ | ✅ | ✅ | ⚠️ |
| Engine features | ⚠️ | ✅ | ✅ | ⚠️ |

---

## DML — Data Manipulation Language

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| INSERT … RETURNING | ❌ | ❌ | ✅ | ✅ |
| UPDATE … RETURNING | ❌ | ❌ | ✅ | ✅ |
| DELETE … RETURNING | ❌ | ❌ | ✅ | ✅ |
| INSERT … DEFAULT VALUES | ❌ | ❌ | ✅ | ✅ |
| Empty INSERT | ❌ | ⚠️ | ✅ | ✅ |
| Multi-row INSERT | ✅ | ✅ | ✅ | ✅ |
| INSERT FROM SELECT | ✅ | ✅ | ✅ | ✅ |
| UPSERT | ❌ | ✅ | ✅ | ✅ |
| FOR UPDATE (row locking) | ❌ | ✅ | ✅ | ❌ |
| UPDATE with LIMIT | ✅ | ✅ | ❌ | ❌ |
| IS DISTINCT FROM | ❌ | ❌ | ✅ | ❌ |
| Postfetch LASTROWID | ❌ | ✅ | ❌ | ✅ |

### Notes

- **RETURNING**: CUBRID has no `RETURNING` clause. Auto-generated keys cannot be fetched in the same round-trip as the INSERT; `postfetch_lastrowid` is also unavailable.
- **Empty INSERT**: MySQL works around the missing `DEFAULT VALUES` syntax with `INSERT INTO t () VALUES ()`. CUBRID does not support either form.
- **UPSERT**: CUBRID supports `ON DUPLICATE KEY UPDATE` at the SQL level, but the dialect does not wire it into SQLAlchemy's `insert().on_conflict_do_update()` API.
- **FOR UPDATE**: CUBRID does not support `SELECT … FOR UPDATE`. The compiler emits an empty string for `for_update_clause`.
- **UPDATE with LIMIT**: CUBRID and MySQL both support `UPDATE … LIMIT n`. PostgreSQL and SQLite do not.
- **IS DISTINCT FROM**: Not a CUBRID SQL operator. SQLAlchemy may emulate it with `CASE` expressions on dialects that lack native support.

---

## DDL — Data Definition Language

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| ALTER TABLE | ✅ | ✅ | ✅ | ⚠️ |
| Table comments | ❌ | ✅ | ✅ | ❌ |
| Column comments | ❌ | ✅ | ✅ | ❌ |
| DROP … IF EXISTS | ❌ | ✅ | ✅ | ✅ |
| Temporary tables | ❌ | ✅ | ✅ | ✅ |
| Multiple schemas | ❌ | ✅ | ✅ | ⚠️ |

### Notes

- **ALTER TABLE**: CUBRID supports standard `ALTER TABLE` for adding/dropping columns and constraints. SQLite has limited ALTER support (add column only; no drop/rename column before 3.35).
- **Comments**: CUBRID does not support `COMMENT ON` or inline `COMMENT` syntax for tables or columns.
- **IF EXISTS**: The CUBRID DDL compiler does not emit `IF EXISTS` for `DROP TABLE` and similar statements.
- **Temporary tables**: CUBRID does not support `CREATE TEMPORARY TABLE` or session-scoped tables.
- **Multiple schemas**: CUBRID operates in a single-schema model. MySQL uses databases as schemas. SQLite can attach databases but does not have true schema support.

---

## Query Features

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| Common Table Expressions (WITH) | ✅ | ✅ | ✅ | ✅ |
| CTEs on DML | ❌ | ❌ | ✅ | ❌ |
| Window functions | ❌ | ✅ | ✅ | ✅ |
| INTERSECT | ✅ | ✅ | ✅ | ✅ |
| EXCEPT | ✅ | ✅ | ✅ | ✅ |
| DISTINCT | ✅ | ✅ | ✅ | ✅ |
| LIMIT / OFFSET | ✅ | ✅ | ✅ | ✅ |

### Notes

- **CTEs**: CUBRID 11.0 supports `WITH` clauses for read queries. Writable CTEs (`WITH … INSERT/UPDATE/DELETE`) are not supported.
- **Window functions**: CUBRID does not support `OVER()`, `ROW_NUMBER()`, `RANK()`, etc. MySQL added these in 8.0; SQLite in 3.25.
- **LIMIT / OFFSET**: CUBRID uses MySQL-style `LIMIT [offset,] count` syntax. When only an offset is given, the dialect emits `LIMIT offset, 1073741823` (max int) as a workaround.

---

## Type System

### Standard SQL Types

| Type | CUBRID | MySQL | PostgreSQL | SQLite |
|------|--------|-------|------------|--------|
| SMALLINT | ✅ | ✅ | ✅ | ✅ |
| INTEGER | ✅ | ✅ | ✅ | ✅ |
| BIGINT | ✅ | ✅ | ✅ | ✅ |
| NUMERIC / DECIMAL | ✅ | ✅ | ✅ | ✅ |
| FLOAT | ✅ | ✅ | ✅ | ✅ |
| DOUBLE / REAL | ✅ | ✅ | ✅ | ✅ |
| BOOLEAN | ⚠️ | ⚠️ | ✅ | ⚠️ |
| DATE | ✅ | ✅ | ✅ | ✅ |
| TIME | ✅ | ✅ | ✅ | ✅ |
| DATETIME | ✅ | ✅ | ✅ | ✅ |
| TIMESTAMP | ✅ | ✅ | ✅ | ✅ |
| CHAR | ✅ | ✅ | ✅ | ✅ |
| VARCHAR | ✅ | ✅ | ✅ | ✅ |
| NCHAR / NVARCHAR | ✅ | ⚠️ | ❌ | ❌ |
| TEXT | ✅ | ✅ | ✅ | ✅ |
| BLOB | ✅ | ✅ | ✅ | ✅ |
| CLOB | ✅ | ✅ | ✅ | ✅ |
| BIT / BIT VARYING | ✅ | ✅ | ✅ | ❌ |

### Extended Types

| Type | CUBRID | MySQL | PostgreSQL | SQLite |
|------|--------|-------|------------|--------|
| ENUM | ❌ | ✅ | ✅ | ❌ |
| JSON | ❌ | ✅ | ✅ | ⚠️ |
| ARRAY | ❌ | ❌ | ✅ | ❌ |
| UUID | ❌ | ❌ | ✅ | ❌ |
| INTERVAL | ❌ | ❌ | ✅ | ❌ |
| HSTORE | ❌ | ❌ | ✅ | ❌ |

### Notes

- **BOOLEAN**: CUBRID maps `BOOLEAN` to `SMALLINT`. MySQL maps it to `TINYINT(1)`. SQLite stores booleans as integers. Only PostgreSQL has a native `BOOLEAN` type.
- **NCHAR / NVARCHAR**: CUBRID has first-class national character types. MySQL handles national characters via column charset. PostgreSQL and SQLite have no separate national character types.
- **JSON**: CUBRID does not have a JSON data type or JSON functions. MySQL (5.7+) and PostgreSQL have native JSON support. SQLite has JSON functions but no dedicated column type.
- **ARRAY**: CUBRID uses collection types (`SET`, `MULTISET`, `SEQUENCE`) which serve a similar purpose but are not SQL-standard arrays. PostgreSQL has native `ARRAY[]` support.
- **CLOB**: CUBRID and MySQL have explicit `CLOB` types. PostgreSQL uses `TEXT` (unlimited length). SQLite stores all text as `TEXT`.

---

## Schema Reflection

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| Table names | ✅ | ✅ | ✅ | ✅ |
| Column information | ✅ | ✅ | ✅ | ✅ |
| Primary keys | ✅ | ✅ | ✅ | ✅ |
| Foreign keys | ✅ | ✅ | ✅ | ✅ |
| Indexes | ✅ | ✅ | ✅ | ✅ |
| Unique constraints | ✅ | ✅ | ✅ | ✅ |
| Check constraints | ❌ | ✅ | ✅ | ❌ |
| Table comments | ❌ | ✅ | ✅ | ❌ |
| View names | ✅ | ✅ | ✅ | ✅ |
| View definitions | ✅ | ✅ | ✅ | ✅ |
| Schema names | ❌ | ✅ | ✅ | ❌ |
| Sequences | ❌ | ❌ | ✅ | ❌ |
| `has_table` | ✅ | ✅ | ✅ | ✅ |
| `has_index` | ✅ | ❌ | ✅ | ✅ |
| `has_sequence` | ❌ | ❌ | ✅ | ❌ |

### Notes

- **Check constraints**: CUBRID stores check constraints internally but the dialect does not reflect them. The `get_check_constraints()` method returns an empty list.
- **has_index**: The CUBRID dialect implements `has_index()` by querying `db_index`. The MySQL SA dialect does not provide a dedicated `has_index()` method.
- **Reflection source**: CUBRID reflection queries the system catalog tables (`db_class`, `db_attribute`, `db_index`, `db_constraint`, `_db_index`) rather than `INFORMATION_SCHEMA`.

---

## Transactions & Connections

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| Isolation level management | ✅ | ✅ | ✅ | ✅ |
| Savepoints | ✅ | ✅ | ✅ | ✅ |
| Two-phase commit | ❌ | ✅ | ✅ | ❌ |
| Server-side cursors | ❌ | ✅ | ✅ | ❌ |
| Autocommit detection | ✅ | ✅ | ✅ | ✅ |
| Connection-level encoding | ❌ | ✅ | ✅ | ❌ |

### CUBRID Isolation Levels

CUBRID supports six isolation levels — more than the SQL standard's four:

| Level | Description |
|-------|-------------|
| `SERIALIZABLE` | Full serialization |
| `REPEATABLE READ CLASS, REPEATABLE READ INSTANCES` | Repeatable read for both schema and data |
| `REPEATABLE READ CLASS, READ COMMITTED INSTANCES` | Repeatable read for schema, read committed for data |
| `REPEATABLE READ CLASS, READ UNCOMMITTED INSTANCES` | Repeatable read for schema, read uncommitted for data |
| `READ COMMITTED CLASS, READ COMMITTED INSTANCES` | Read committed for both |
| `READ COMMITTED CLASS, READ UNCOMMITTED INSTANCES` | Read committed for schema, read uncommitted for data |

### Notes

- **Two-phase commit**: CUBRID does not support distributed transactions via `XA`.
- **Server-side cursors**: The CUBRID Python driver does not expose server-side cursor functionality.
- **Autocommit detection**: The CUBRID execution context uses a regex pattern matching `SET`, `ALTER`, `CREATE`, `DROP`, `GRANT`, `REVOKE`, and `TRUNCATE` statements to determine when to enable autocommit.

---

## Dialect Engine Features

| Feature | CUBRID | MySQL | PostgreSQL | SQLite |
|---------|--------|-------|------------|--------|
| Statement caching | ✅ | ✅ | ✅ | ✅ |
| Native enum | ❌ | ✅ | ✅ | ❌ |
| Native boolean | ❌ | ❌ | ✅ | ❌ |
| Native decimal | ✅ | ✅ | ✅ | ❌ |
| Sequences | ❌ | ❌ | ✅ | ❌ |
| ON UPDATE CASCADE | ✅ | ✅ | ✅ | ✅ |
| ON DELETE CASCADE | ✅ | ✅ | ✅ | ✅ |
| Self-referential FKs | ✅ | ✅ | ✅ | ✅ |
| Independent connections | ✅ | ✅ | ✅ | ✅ |
| Unicode DDL | ✅ | ✅ | ✅ | ✅ |
| Name normalization | ✅ | ❌ | ✅ | ❌ |

### Notes

- **Statement caching**: `supports_statement_cache = True`. The dialect is fully compatible with SQLAlchemy 2.0's compiled cache.
- **Name normalization**: CUBRID folds unquoted identifiers to lowercase. The dialect normalizes identifiers to match Python-side expectations (`requires_name_normalize = True`).
- **Max identifier length**: CUBRID allows identifiers up to 254 characters — significantly longer than MySQL (64) or PostgreSQL (63).

---

## CUBRID-Specific Features

These types and capabilities are unique to the CUBRID dialect and have no direct equivalent in MySQL, PostgreSQL, or SQLite.

| Feature | Description |
|---------|-------------|
| `MONETARY` type | Fixed-point currency type with locale-aware formatting |
| `STRING` type | Alias for `VARCHAR(1,073,741,823)` — maximum-length variable string |
| `OBJECT` type | OID reference type pointing to another row by object identifier |
| `SET` collection | Unordered collection of unique elements |
| `MULTISET` collection | Unordered collection that allows duplicates |
| `SEQUENCE` collection | Ordered collection that allows duplicates |
| 6 isolation levels | Separate class-level and instance-level isolation granularity |
| 254-char identifiers | Longer than MySQL (64) and PostgreSQL (63) |

### Collection Types

CUBRID's collection types (`SET`, `MULTISET`, `SEQUENCE`) are typed containers that hold elements of a specified data type. They are declared in DDL as:

```
SET(INTEGER)
MULTISET(VARCHAR)
SEQUENCE(DOUBLE)
```

These are fully supported by the dialect's type compiler and can be used in `Column` definitions.

---

## Known Limitations & Roadmap

Features not currently supported that may be added in future releases, depending on CUBRID database evolution and community contributions.

| Feature | Status | Blocker |
|---------|--------|---------|
| Window functions | ❌ | CUBRID lacks `OVER()` support |
| JSON type | ❌ | CUBRID lacks JSON data type |
| RETURNING clause | ❌ | CUBRID lacks `RETURNING` syntax |
| Temporary tables | ❌ | CUBRID lacks `CREATE TEMPORARY TABLE` |
| Table / column comments | ❌ | CUBRID lacks `COMMENT` syntax |
| Check constraint reflection | ❌ | Requires catalog query implementation |
| UPSERT integration | ❌ | Requires wiring `ON DUPLICATE KEY UPDATE` to SA's conflict API |
| DDL IF EXISTS | ❌ | Requires DDL compiler override |
| FOR UPDATE | ❌ | CUBRID lacks row-level locking in SELECT |
| Postfetch LASTROWID | ❌ | CUBRID Python driver limitation |

---

*Last updated: March 2026 · sqlalchemy-cubrid v1.0.0 · SQLAlchemy 2.0+*
