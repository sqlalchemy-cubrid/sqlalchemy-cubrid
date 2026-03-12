# CUBRID-Specific DML Constructs

This dialect provides custom SQLAlchemy constructs for CUBRID-specific DML (Data Manipulation Language) features that go beyond the standard SQLAlchemy API.

---

## Table of Contents

- [ON DUPLICATE KEY UPDATE](#on-duplicate-key-update)
  - [Basic Usage](#basic-usage)
  - [Referencing Inserted Values](#referencing-inserted-values)
  - [Argument Forms](#argument-forms)
- [MERGE Statement](#merge-statement)
  - [Basic Usage](#basic-usage-1)
  - [MERGE with WHERE Clauses](#merge-with-where-clauses)
  - [MERGE with DELETE WHERE](#merge-with-delete-where)
  - [Builder Methods](#builder-methods)
- [GROUP_CONCAT](#group_concat)
- [TRUNCATE TABLE](#truncate-table)
- [FOR UPDATE](#for-update)
- [UPDATE with LIMIT](#update-with-limit)
- [Index Hints](#index-hints)
  - [USING INDEX](#using-index)
  - [USE / FORCE / IGNORE INDEX](#use--force--ignore-index)

---

## ON DUPLICATE KEY UPDATE

CUBRID supports `INSERT … ON DUPLICATE KEY UPDATE` with `VALUES()` references, identical to MySQL's pre-8.0 syntax.

### Basic Usage

```python
from sqlalchemy_cubrid import insert

stmt = insert(users).values(id=1, name="alice", email="alice@example.com")
stmt = stmt.on_duplicate_key_update(name="updated_alice")
```

**Generated SQL:**

```sql
INSERT INTO users (id, name, email)
VALUES (1, 'alice', 'alice@example.com')
ON DUPLICATE KEY UPDATE name = 'updated_alice'
```

### Referencing Inserted Values

Use `stmt.inserted` to reference the values being inserted — rendered as `VALUES(column_name)` in SQL:

```python
from sqlalchemy_cubrid import insert

stmt = insert(users).values(id=1, name="alice", email="alice@example.com")
stmt = stmt.on_duplicate_key_update(
    name=stmt.inserted.name,      # → VALUES(name)
    email=stmt.inserted.email,    # → VALUES(email)
)
```

**Generated SQL:**

```sql
INSERT INTO users (id, name, email)
VALUES (1, 'alice', 'alice@example.com')
ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email)
```

### Argument Forms

The `on_duplicate_key_update()` method accepts three argument forms:

```python
# 1. Keyword arguments
stmt.on_duplicate_key_update(name="value", email="value")

# 2. Dictionary
stmt.on_duplicate_key_update({"name": "value", "email": "value"})

# 3. List of tuples (preserves column ordering)
stmt.on_duplicate_key_update([
    ("name", "value"),
    ("email", "value"),
])
```

> **Note**: You cannot mix keyword arguments with positional arguments (dict/list). Choose one form per call.

---

## MERGE Statement

CUBRID supports the full SQL `MERGE` statement for conditional INSERT/UPDATE in a single operation.

### Basic Usage

```python
from sqlalchemy_cubrid.dml import merge

stmt = (
    merge(target_table)
    .using(source_table)
    .on(target_table.c.id == source_table.c.id)
    .when_matched_then_update(
        {"name": source_table.c.name, "email": source_table.c.email}
    )
    .when_not_matched_then_insert(
        {
            "id": source_table.c.id,
            "name": source_table.c.name,
            "email": source_table.c.email,
        }
    )
)
```

**Generated SQL:**

```sql
MERGE INTO target_table
USING source_table
ON (target_table.id = source_table.id)
WHEN MATCHED THEN UPDATE SET name = source_table.name, email = source_table.email
WHEN NOT MATCHED THEN INSERT (id, name, email)
  VALUES (source_table.id, source_table.name, source_table.email)
```

### MERGE with WHERE Clauses

Both `WHEN MATCHED` and `WHEN NOT MATCHED` clauses support optional `WHERE` filters:

```python
stmt = (
    merge(target_table)
    .using(source_table)
    .on(target_table.c.id == source_table.c.id)
    .when_matched_then_update(
        {"name": source_table.c.name},
        where=source_table.c.name.is_not(None),  # Only update non-null names
    )
    .when_not_matched_then_insert(
        {"id": source_table.c.id, "name": source_table.c.name},
        where=source_table.c.name.is_not(None),  # Only insert non-null names
    )
)
```

**Generated SQL:**

```sql
MERGE INTO target_table
USING source_table
ON (target_table.id = source_table.id)
WHEN MATCHED THEN UPDATE SET name = source_table.name
  WHERE source_table.name IS NOT NULL
WHEN NOT MATCHED THEN INSERT (id, name)
  VALUES (source_table.id, source_table.name)
  WHERE source_table.name IS NOT NULL
```

### MERGE with DELETE WHERE

CUBRID supports `DELETE WHERE` within a `WHEN MATCHED` clause to conditionally delete rows:

```python
stmt = (
    merge(target_table)
    .using(source_table)
    .on(target_table.c.id == source_table.c.id)
    .when_matched_then_update(
        {"name": source_table.c.name},
        delete_where=target_table.c.active == False,
    )
    .when_not_matched_then_insert(
        {"id": source_table.c.id, "name": source_table.c.name}
    )
)
```

**Generated SQL:**

```sql
MERGE INTO target_table
USING source_table
ON (target_table.id = source_table.id)
WHEN MATCHED THEN UPDATE SET name = source_table.name
  DELETE WHERE target_table.active = 0
WHEN NOT MATCHED THEN INSERT (id, name)
  VALUES (source_table.id, source_table.name)
```

You can also add `DELETE WHERE` separately via `when_matched_then_delete()`:

```python
stmt = (
    merge(target_table)
    .using(source_table)
    .on(target_table.c.id == source_table.c.id)
    .when_matched_then_update({"name": source_table.c.name})
    .when_matched_then_delete(where=target_table.c.active == False)
    .when_not_matched_then_insert(
        {"id": source_table.c.id, "name": source_table.c.name}
    )
)
```

### Builder Methods

| Method                                                       | Description                                    |
|--------------------------------------------------------------|------------------------------------------------|
| `merge(target)`                                              | Factory function — sets the target table       |
| `.using(source)`                                             | Source table or subquery                        |
| `.on(condition)`                                             | Join condition                                 |
| `.when_matched_then_update(values, where=, delete_where=)`   | WHEN MATCHED → UPDATE SET clause               |
| `.when_matched_then_delete(where=)`                          | Adds DELETE WHERE to existing WHEN MATCHED     |
| `.when_not_matched_then_insert(values, where=)`              | WHEN NOT MATCHED → INSERT clause               |

**Requirements:**
- `using()` and `on()` are mandatory
- At least one of `when_matched_then_update` or `when_not_matched_then_insert` must be specified
- `when_matched_then_delete` can only be called after `when_matched_then_update`

---

## GROUP_CONCAT

CUBRID supports `GROUP_CONCAT` as an aggregate function:

```python
import sqlalchemy as sa

# Basic GROUP_CONCAT
stmt = sa.select(sa.func.group_concat(users.c.name))
# → SELECT GROUP_CONCAT(users.name) FROM users

# With GROUP BY
stmt = (
    sa.select(
        users.c.department,
        sa.func.group_concat(users.c.name),
    )
    .group_by(users.c.department)
)
# → SELECT users.department, GROUP_CONCAT(users.name)
#   FROM users GROUP BY users.department
```

CUBRID's `GROUP_CONCAT` supports `DISTINCT`, `ORDER BY`, and `SEPARATOR` modifiers at the SQL level, though the standard `sa.func.group_concat()` API provides access to basic usage.

---

## TRUNCATE TABLE

CUBRID supports `TRUNCATE TABLE`, which is faster than `DELETE` for removing all rows:

```python
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE temp_data"))
```

The dialect includes `TRUNCATE` in its autocommit detection pattern, so it will be executed with autocommit enabled (matching CUBRID's implicit DDL commit behavior).

---

## FOR UPDATE

CUBRID supports `SELECT … FOR UPDATE` for row-level locking:

```python
import sqlalchemy as sa

# Basic FOR UPDATE
stmt = sa.select(users).where(users.c.id == 1).with_for_update()
# → SELECT ... FROM users WHERE users.id = 1 FOR UPDATE

# FOR UPDATE OF specific columns
stmt = (
    sa.select(users)
    .where(users.c.id == 1)
    .with_for_update(of=[users.c.name, users.c.email])
)
# → SELECT ... FROM users WHERE users.id = 1 FOR UPDATE OF users.name, users.email
```

> **Note**: CUBRID does **not** support `NOWAIT` or `SKIP LOCKED` modifiers. Using them will have no effect.

---

## UPDATE with LIMIT

CUBRID supports `UPDATE … LIMIT n` to restrict the number of rows affected:

```python
from sqlalchemy import update

stmt = (
    update(users)
    .values(status="inactive")
    .where(users.c.last_login < "2025-01-01")
    .execution_options(**{"cubrid_limit": 100})
)
# → UPDATE users SET status = 'inactive'
#   WHERE users.last_login < '2025-01-01'
#   LIMIT 100
```

> **Note**: This is a CUBRID/MySQL extension. PostgreSQL and SQLite do not support `UPDATE … LIMIT`.

---

## Index Hints

CUBRID supports index hints in SELECT queries. Use SQLAlchemy's built-in hint mechanisms — no custom dialect constructs are needed.

### USING INDEX

```python
import sqlalchemy as sa

# Using with_hint (dialect-specific — only emitted for CUBRID)
stmt = (
    sa.select(users)
    .with_hint(users, "USING INDEX idx_users_name", dialect_name="cubrid")
)

# Using suffix_with (always emitted)
stmt = sa.select(users).suffix_with("USING INDEX idx_users_name")
```

### USE / FORCE / IGNORE INDEX

```python
# USE INDEX
stmt = (
    sa.select(users)
    .with_hint(users, "USE INDEX (idx_users_name)", dialect_name="cubrid")
)

# FORCE INDEX
stmt = (
    sa.select(users)
    .with_hint(users, "FORCE INDEX (idx_users_email)", dialect_name="cubrid")
)

# IGNORE INDEX
stmt = (
    sa.select(users)
    .with_hint(users, "IGNORE INDEX (idx_users_old)", dialect_name="cubrid")
)
```

> **Portability tip**: When using `with_hint(dialect_name="cubrid")`, the hint is only emitted when compiling against the CUBRID dialect. Other dialects will ignore it, making your code safely portable across database backends.

---

*See also: [Feature Support](FEATURE_SUPPORT.md) · [Type Mapping](TYPES.md) · [Connection Setup](CONNECTION.md)*
