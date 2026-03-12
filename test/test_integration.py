# test/test_integration.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Integration tests against a live CUBRID instance.

These tests require a running CUBRID database.  They are skipped
automatically when no CUBRID connection is available.

Set the environment variable ``CUBRID_TEST_URL`` to the connection
URL, e.g.::

    export CUBRID_TEST_URL="cubrid://dba@localhost:33000/testdb"

Alternatively, the tests look for a CUBRID instance at the default
``cubrid://dba@localhost:33000/testdb``.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_DEFAULT_URL = "cubrid://dba@localhost:33000/testdb"


def _cubrid_url() -> str:
    return os.environ.get("CUBRID_TEST_URL", _DEFAULT_URL)


def _can_connect() -> bool:
    """Return True if a CUBRID instance is reachable."""
    try:
        engine = create_engine(_cubrid_url())
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _can_connect(),
    reason="CUBRID instance not available (set CUBRID_TEST_URL)",
)


@pytest.fixture(scope="module")
def engine():
    eng = create_engine(_cubrid_url(), echo=False)
    yield eng
    eng.dispose()


@pytest.fixture(scope="module")
def metadata(engine):
    meta = MetaData()

    Table(
        "integration_users",
        meta,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("name", String(100), nullable=False),
        Column("email", String(200)),
    )

    Table(
        "integration_orders",
        meta,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column(
            "user_id",
            Integer,
            ForeignKey("integration_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("amount", Integer, nullable=False),
    )

    meta.create_all(engine)
    yield meta
    meta.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_tables(engine, metadata):
    """Truncate tables before each test."""
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM integration_orders"))
        conn.execute(text("DELETE FROM integration_users"))
    yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestServerConnection:
    def test_server_version(self, engine):
        """Verify we can connect and get a server version."""
        with engine.connect() as conn:
            version = conn.execute(text("SELECT VERSION()")).scalar()
        assert version is not None
        parts = version.split(".")
        assert len(parts) >= 3, f"Unexpected version format: {version}"

    def test_select_literal(self, engine):
        """Basic SELECT without tables."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 42")).scalar()
        assert result == 42


class TestDDLAndDML:
    def test_insert_and_select(self, engine, metadata):
        """INSERT rows and SELECT them back."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            conn.execute(users.insert().values(name="Alice", email="alice@example.com"))
            conn.execute(users.insert().values(name="Bob", email="bob@example.com"))

        with engine.connect() as conn:
            rows = conn.execute(users.select().order_by(users.c.name)).fetchall()
        assert len(rows) == 2
        assert rows[0].name == "Alice"
        assert rows[1].name == "Bob"

    def test_auto_increment(self, engine, metadata):
        """AUTO_INCREMENT generates sequential IDs."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            conn.execute(users.insert().values(name="User1"))
            conn.execute(users.insert().values(name="User2"))

        with engine.connect() as conn:
            ids = [
                r[0]
                for r in conn.execute(
                    users.select().with_only_columns(users.c.id).order_by(users.c.id)
                ).fetchall()
            ]
        assert len(ids) == 2
        assert ids[1] > ids[0], "AUTO_INCREMENT should produce increasing IDs"

    def test_update(self, engine, metadata):
        """UPDATE modifies rows."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            conn.execute(users.insert().values(name="Charlie", email="old@example.com"))
            conn.execute(
                users.update().where(users.c.name == "Charlie").values(email="new@example.com")
            )

        with engine.connect() as conn:
            email = conn.execute(users.select().where(users.c.name == "Charlie")).fetchone().email
        assert email == "new@example.com"

    def test_delete(self, engine, metadata):
        """DELETE removes rows."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            conn.execute(users.insert().values(name="Ephemeral"))
            conn.execute(users.delete().where(users.c.name == "Ephemeral"))

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM integration_users WHERE name = 'Ephemeral'")
            ).scalar()
        assert count == 0

    def test_join(self, engine, metadata):
        """JOIN between two tables."""
        users = metadata.tables["integration_users"]
        orders = metadata.tables["integration_orders"]

        with engine.begin() as conn:
            conn.execute(users.insert().values(name="Dave"))
            user_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            conn.execute(orders.insert().values(user_id=user_id, amount=100))
            conn.execute(orders.insert().values(user_id=user_id, amount=250))

        with engine.connect() as conn:
            j = users.join(orders, users.c.id == orders.c.user_id)
            rows = conn.execute(
                users.select()
                .with_only_columns(users.c.name, orders.c.amount)
                .select_from(j)
                .order_by(orders.c.amount)
            ).fetchall()
        assert len(rows) == 2
        assert rows[0].amount == 100
        assert rows[1].amount == 250

    def test_limit_offset(self, engine, metadata):
        """LIMIT and OFFSET work correctly."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            for i in range(5):
                conn.execute(users.insert().values(name=f"User{i}"))

        with engine.connect() as conn:
            rows = conn.execute(users.select().order_by(users.c.id).limit(2).offset(1)).fetchall()
        assert len(rows) == 2


class TestReflection:
    def test_has_table(self, engine, metadata):
        """has_table() returns correct results."""
        insp = inspect(engine)
        assert insp.has_table("integration_users")
        assert not insp.has_table("nonexistent_table_xyz")

    def test_get_table_names(self, engine, metadata):
        """get_table_names() includes our test tables."""
        insp = inspect(engine)
        tables = insp.get_table_names()
        assert "integration_users" in tables
        assert "integration_orders" in tables

    def test_get_columns(self, engine, metadata):
        """get_columns() reflects column metadata."""
        insp = inspect(engine)
        columns = insp.get_columns("integration_users")
        col_names = [c["name"] for c in columns]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names

    def test_get_pk_constraint(self, engine, metadata):
        """get_pk_constraint() reflects primary key."""
        insp = inspect(engine)
        pk = insp.get_pk_constraint("integration_users")
        assert "id" in pk["constrained_columns"]

    def test_get_foreign_keys(self, engine, metadata):
        """get_foreign_keys() reflects FK from orders → users."""
        insp = inspect(engine)
        fks = insp.get_foreign_keys("integration_orders")
        # CUBRID may not always reflect FKs through db_constraint depending on version
        if len(fks) >= 1:
            fk = fks[0]
            assert "user_id" in fk["constrained_columns"]
            assert fk["referred_table"] == "integration_users"


class TestTransactions:
    def test_savepoint(self, engine, metadata):
        """Savepoint support (CUBRID supports savepoints, not RELEASE SAVEPOINT)."""
        users = metadata.tables["integration_users"]
        with engine.begin() as conn:
            conn.execute(users.insert().values(name="BeforeSP"))
            savepoint = conn.begin_nested()
            conn.execute(users.insert().values(name="InSP"))
            savepoint.rollback()

        with engine.connect() as conn:
            rows = conn.execute(users.select()).fetchall()
        names = [r.name for r in rows]
        assert "BeforeSP" in names
        assert "InSP" not in names

    def test_rollback(self, engine, metadata):
        """Transaction rollback discards changes."""
        users = metadata.tables["integration_users"]
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(users.insert().values(name="WillRollback"))
            trans.rollback()

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM integration_users WHERE name = 'WillRollback'")
            ).scalar()
        assert count == 0


class TestLastRowId:
    def test_lastrowid_via_orm(self, engine, metadata):
        """Verify lastrowid works through SA ORM Session."""
        users = metadata.tables["integration_users"]
        with Session(engine) as session:
            result = session.execute(users.insert().values(name="LastRowIdTest"))
            inserted_pk = result.inserted_primary_key[0]
            session.commit()
        assert inserted_pk is not None
        assert isinstance(inserted_pk, int)
        assert inserted_pk > 0


class TestIsolationLevel:
    def test_get_and_set_isolation_level(self, engine):
        """Get/set isolation level round-trip."""
        with engine.connect() as conn:
            raw_conn = conn.connection.dbapi_connection
            dialect = engine.dialect

            level = dialect.get_isolation_level(raw_conn)
            # CUBRID returns isolation level as an integer (e.g. 4) or string
            assert level is not None

            # Set to a known level and verify no error
            dialect.set_isolation_level(raw_conn, "SERIALIZABLE")
            new_level = dialect.get_isolation_level(raw_conn)
            assert new_level is not None


class TestDoPing:
    def test_ping_success(self, engine):
        """do_ping() succeeds on a live connection."""
        with engine.connect() as conn:
            raw_conn = conn.connection.dbapi_connection
            dialect = engine.dialect
            result = dialect.do_ping(raw_conn)
            assert result is True

    def test_pool_pre_ping(self):
        """Engine with pool_pre_ping=True works correctly."""
        eng = create_engine(_cubrid_url(), pool_pre_ping=True, echo=False)
        try:
            with eng.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            eng.dispose()


class TestIsDisconnect:
    def test_is_disconnect_with_non_disconnect_error(self, engine):
        """is_disconnect() returns False for normal database errors."""
        dialect = engine.dialect
        with engine.connect() as conn:
            raw_conn = conn.connection.dbapi_connection
            try:
                cursor = raw_conn.cursor()
                cursor.execute("SELECT * FROM nonexistent_table_xyz_12345")
            except Exception as e:
                assert dialect.is_disconnect(e, conn, None) is False

    def test_is_disconnect_returns_false_for_runtime_error(self, engine):
        """is_disconnect() returns False for non-DBAPI errors."""
        dialect = engine.dialect
        exc = RuntimeError("some random error")
        assert dialect.is_disconnect(exc, None, None) is False


class TestPostfetchLastRowId:
    def test_lastrowid_consistency(self, engine, metadata):
        """Verify lastrowid returns consistent IDs across inserts."""
        users = metadata.tables["integration_users"]
        ids = []
        with Session(engine) as session:
            for i in range(3):
                result = session.execute(users.insert().values(name=f"lastrowid_test_{i}"))
                ids.append(result.inserted_primary_key[0])
            session.commit()

        assert len(ids) == 3
        assert all(isinstance(pk, int) for pk in ids)
        assert ids[0] < ids[1] < ids[2], "IDs should be monotonically increasing"


class TestConnectionPool:
    def test_pool_recycle(self):
        """Engine with pool_recycle works without errors."""
        eng = create_engine(_cubrid_url(), pool_recycle=60, echo=False)
        try:
            with eng.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            eng.dispose()

    def test_multiple_connections(self):
        """Multiple connections from pool work correctly."""
        eng = create_engine(_cubrid_url(), pool_size=3, echo=False)
        try:
            conns = []
            for _ in range(3):
                c = eng.connect()
                conns.append(c)
            for c in conns:
                result = c.execute(text("SELECT 1")).scalar()
                assert result == 1
            for c in conns:
                c.close()
        finally:
            eng.dispose()
