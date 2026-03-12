# Connection & Driver Setup

This guide covers how to install the CUBRID Python driver, configure SQLAlchemy connection strings, and understand the connection lifecycle.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installing the CUBRID Python Driver](#installing-the-cubrid-python-driver)
- [Connection String Format](#connection-string-format)
- [Entry Points](#entry-points)
- [How the Dialect Translates URLs](#how-the-dialect-translates-urls)
- [Connection Options](#connection-options)
- [Autocommit Behavior](#autocommit-behavior)
- [Server Version Detection](#server-version-detection)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement        | Version         |
|--------------------|-----------------|
| Python             | 3.10+           |
| SQLAlchemy         | 2.0 – 2.1       |
| CUBRID Server      | 10.2 – 11.4     |
| CUBRID Python Driver | Latest          |

---

## Installing the CUBRID Python Driver

The dialect requires the [CUBRID-Python](https://github.com/CUBRID/cubrid-python) driver:

```bash
pip install CUBRID-Python
```

Or install both the dialect and driver together:

```bash
pip install sqlalchemy-cubrid
pip install CUBRID-Python
```

> **Note**: `CUBRID-Python` is a C-extension driver. On some platforms you may need
> the CUBRID CCI library installed. See the
> [CUBRID Python driver documentation](https://www.cubrid.org/manual/en/11.0/api/python.html)
> for platform-specific instructions.

---

## Connection String Format

SQLAlchemy uses standard URL-style connection strings:

```
cubrid://user:password@host:port/database
```

### Examples

```python
from sqlalchemy import create_engine

# Basic connection
engine = create_engine("cubrid://dba:password@localhost:33000/demodb")

# Without password (CUBRID allows passwordless dba access by default)
engine = create_engine("cubrid://dba@localhost:33000/testdb")

# With explicit driver name
engine = create_engine("cubrid+cubrid://dba:password@localhost:33000/demodb")
```

### URL Components

| Component  | Default     | Description                            |
|------------|-------------|----------------------------------------|
| `user`     | *(required)* | Database username (typically `dba`)   |
| `password` | *(empty)*   | Database password                      |
| `host`     | `localhost` | CUBRID server hostname or IP           |
| `port`     | `33000`     | CUBRID broker port                     |
| `database` | *(required)* | Database name                         |

---

## Entry Points

The dialect registers two SQLAlchemy entry points:

| URL Scheme        | Description                  |
|-------------------|------------------------------|
| `cubrid://`       | Default (recommended)        |
| `cubrid+cubrid://`| Explicit driver specification |

Both point to the same `CubridDialect` class. Use `cubrid://` unless you have a specific reason to be explicit.

---

## How the Dialect Translates URLs

Internally, the dialect converts SQLAlchemy URLs to the CUBRID native connection format:

```
SQLAlchemy URL:  cubrid://dba:password@myhost:33000/mydb
                        ↓
CUBRID native:   CUBRID:myhost:33000:mydb:::
```

The `create_connect_args()` method returns `(connect_url, username, password)` as positional arguments to the CUBRID Python driver's `connect()` function.

### Translation Details

```python
# What the dialect does internally:
connect_url = f"CUBRID:{host}:{port}:{database}:::"
args = (connect_url, username, password)
# → CUBRIDdb.connect("CUBRID:myhost:33000:mydb:::", "dba", "password")
```

The trailing `:::` in the CUBRID connection string represents three empty optional parameters (reserved for future use by CUBRID).

---

## Connection Options

### Engine-Level Options

```python
engine = create_engine(
    "cubrid://dba@localhost:33000/testdb",

    # Set default isolation level for all connections
    isolation_level="REPEATABLE READ",

    # SQLAlchemy 2.0 connection pool settings
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,

    # Enable SQL logging
    echo=True,
)
```

### Per-Connection Isolation Level

```python
with engine.connect().execution_options(
    isolation_level="SERIALIZABLE"
) as conn:
    # This connection uses SERIALIZABLE isolation
    result = conn.execute(text("SELECT * FROM accounts"))
```

See [Isolation Levels](ISOLATION_LEVELS.md) for all supported levels.

---

## Autocommit Behavior

### Driver Default vs. Dialect Override

The CUBRID Python driver defaults to `autocommit=True`. The dialect overrides this by calling `conn.set_autocommit(False)` on every new connection, so that SQLAlchemy can manage transactions properly.

### DDL Autocommit Detection

CUBRID implicitly commits DDL statements. The dialect detects DDL patterns and enables autocommit for:

- `CREATE`, `ALTER`, `DROP`
- `GRANT`, `REVOKE`
- `TRUNCATE`
- `MERGE`

This is handled by the `CubridExecutionContext.should_autocommit_text()` method using a regex pattern.

---

## Server Version Detection

The dialect queries the server version on initialization:

```sql
SELECT VERSION()
```

The result (e.g., `11.2.0.0374`) is parsed into a tuple `(11, 2, 0, 374)` for internal version checks.

---

## Troubleshooting

### Common Connection Errors

#### `ImportError: No module named 'CUBRIDdb'`

The CUBRID Python driver is not installed:

```bash
pip install CUBRID-Python
```

#### `Connection refused` on port 33000

1. Verify the CUBRID broker is running:
   ```bash
   cubrid broker status
   ```

2. Check the broker port in `cubrid_broker.conf` — default is `33000`.

3. If using Docker:
   ```bash
   docker compose up -d
   docker compose logs cubrid
   ```

#### `Authentication failed`

CUBRID's default `dba` user has no password. If you set one, ensure it matches your connection string:

```python
# If dba has no password
engine = create_engine("cubrid://dba@localhost:33000/testdb")

# If dba has a password
engine = create_engine("cubrid://dba:mypassword@localhost:33000/testdb")
```

### Docker Quick Start

For local development, use the provided `docker-compose.yml`:

```bash
# Start CUBRID 11.2 (default)
docker compose up -d

# Start a specific version
CUBRID_VERSION=11.4 docker compose up -d

# Verify it's running
docker compose ps

# Connect
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('cubrid://dba@localhost:33000/testdb')
with engine.connect() as conn:
    print(conn.execute(text('SELECT VERSION()')).scalar())
"
```

---

*See also: [Isolation Levels](ISOLATION_LEVELS.md) · [Type Mapping](TYPES.md) · [Feature Support](FEATURE_SUPPORT.md)*
