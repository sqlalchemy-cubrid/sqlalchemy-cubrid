from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from sqlalchemy_cubrid.dialect import CubridDialect


class _Result:
    _rows: list[tuple[Any, ...]]

    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def __iter__(self) -> Iterator[tuple[object, ...]]:
        return iter(self._rows)

    def fetchone(self) -> tuple[object, ...] | None:
        return self._rows[0] if self._rows else None


class _MockConnection:
    _show_columns: list[tuple[Any, ...]]
    _show_indexes: list[tuple[Any, ...]]
    _show_create: list[tuple[Any, ...]]
    _db_index: list[tuple[Any, ...]]
    _db_constraint: list[tuple[Any, ...]]
    _db_attribute: list[tuple[Any, ...]]

    def __init__(self) -> None:
        self._show_columns = [
            ("id", "INTEGER", "NO", "PRI", None, "auto_increment"),
            ("email", "VARCHAR(200)", "NO", "UNI", None, ""),
            ("team_id", "INTEGER", "YES", "MUL", None, ""),
            ("score", "DECIMAL(10,2)", "YES", "", "0.00", ""),
        ]
        self._show_indexes = [
            ("users", 1, "idx_users_team_id", 1, "team_id"),
            ("users", 1, "idx_users_team_id", 2, "id"),
            ("users", 0, "uq_users_email", 1, "email"),
            ("users", 1, "pk_users", 1, "id"),
            ("users", 1, "fk_users_team", 1, "team_id"),
        ]
        self._show_create = [
            (
                "users",
                """
CREATE TABLE [users] (
  [id] INTEGER NOT NULL AUTO_INCREMENT,
  [email] VARCHAR(200) NOT NULL,
  [team_id] INTEGER,
  [score] DECIMAL(10,2) DEFAULT 0.00,
  CONSTRAINT [pk_users] PRIMARY KEY ([id]),
  CONSTRAINT [uq_users_email] UNIQUE KEY ([email]),
  CONSTRAINT [fk_users_team] FOREIGN KEY ([team_id]) REFERENCES [dba.teams] ([id]) ON DELETE SET NULL ON UPDATE RESTRICT
)
""",
            )
        ]
        self._db_index = [
            ("pk_users", True, False),
            ("fk_users_team", False, True),
            ("idx_users_team_id", False, False),
            ("uq_users_email", False, False),
        ]
        self._db_constraint = [("pk_users",)]
        self._db_attribute = [
            ("id", "identifier"),
            ("email", "email address"),
            ("team_id", "team reference"),
            ("score", "quality score"),
        ]

    def execute(self, statement: Any, params: Any = None) -> _Result:
        sql = str(statement)
        if sql.startswith("SHOW COLUMNS IN"):
            return _Result(self._show_columns)
        if sql.startswith("SHOW INDEXES IN"):
            return _Result(self._show_indexes)
        if sql.startswith("SHOW CREATE TABLE"):
            return _Result(self._show_create)
        if "FROM _db_index" in sql:
            return _Result(self._db_index)
        if "FROM db_constraint" in sql:
            return _Result(self._db_constraint)
        if "FROM _db_attribute" in sql:
            return _Result(self._db_attribute)
        raise AssertionError(f"Unexpected SQL: {sql}, params={params}")


@pytest.fixture
def mock_connection() -> _MockConnection:
    return _MockConnection()


@pytest.fixture
def dialect() -> CubridDialect:
    return CubridDialect()


def test_get_columns_golden(dialect: CubridDialect, mock_connection: _MockConnection) -> None:
    columns = [dict(column) for column in dialect.get_columns(mock_connection, "users")]
    assert [column["name"] for column in columns] == ["id", "email", "team_id", "score"]
    assert [column["nullable"] for column in columns] == [False, False, True, True]
    assert [column["autoincrement"] for column in columns] == [True, False, False, False]
    assert [column["default"] for column in columns] == [None, None, None, "0.00"]
    assert [column["comment"] for column in columns] == [
        "identifier",
        "email address",
        "team reference",
        "quality score",
    ]
    assert [column["type"].__class__.__name__ for column in columns] == [
        "INTEGER",
        "VARCHAR",
        "INTEGER",
        "DECIMAL",
    ]


def test_get_pk_constraint_golden(dialect: CubridDialect, mock_connection: _MockConnection) -> None:
    pk = dialect.get_pk_constraint(mock_connection, "users")
    assert pk == {"name": "pk_users", "constrained_columns": ["id"]}


def test_get_foreign_keys_golden(dialect: CubridDialect, mock_connection: _MockConnection) -> None:
    foreign_keys = dialect.get_foreign_keys(mock_connection, "users")
    assert foreign_keys == [
        {
            "name": "fk_users_team",
            "constrained_columns": ["team_id"],
            "options": {"ondelete": "SET NULL", "onupdate": "RESTRICT"},
            "referred_schema": None,
            "referred_table": "teams",
            "referred_columns": ["id"],
        }
    ]


def test_get_unique_constraints_golden(
    dialect: CubridDialect, mock_connection: _MockConnection
) -> None:
    unique_constraints = dialect.get_unique_constraints(mock_connection, "users")
    assert unique_constraints == [{"name": "uq_users_email", "column_names": ["email"]}]


def test_get_indexes_golden(dialect: CubridDialect, mock_connection: _MockConnection) -> None:
    indexes = dialect.get_indexes(mock_connection, "users")
    assert indexes == [
        {
            "name": "idx_users_team_id",
            "column_names": ["team_id", "id"],
            "unique": False,
        },
        {
            "name": "uq_users_email",
            "column_names": ["email"],
            "unique": True,
        },
    ]
