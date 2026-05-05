from __future__ import annotations

from unittest import mock

import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from sqlalchemy_cubrid.dialect import CubridDialect
from sqlalchemy_cubrid.types import VARCHAR


class _MockInspector:
    def __init__(self, bind, tables):
        self.bind = bind
        self.dialect = bind.dialect
        self.info_cache = {}
        self._tables = tables

    def _table(self, table_name):
        return self._tables[table_name]

    def get_table_names(self, schema=None):
        return list(self._tables)

    def get_columns(self, table_name, schema=None, **kw):
        return self._table(table_name)["columns"]

    def get_pk_constraint(self, table_name, schema=None, **kw):
        return self._table(table_name).get(
            "pk_constraint", {"name": None, "constrained_columns": []}
        )

    def get_foreign_keys(self, table_name, schema=None, **kw):
        return self._table(table_name).get("foreign_keys", [])

    def get_indexes(self, table_name, schema=None, **kw):
        return self._table(table_name).get("indexes", [])

    def get_unique_constraints(self, table_name, schema=None, **kw):
        return self._table(table_name).get("unique_constraints", [])

    def get_table_comment(self, table_name, schema=None, **kw):
        return self._table(table_name).get("table_comment", {"text": None})

    def get_check_constraints(self, table_name, schema=None, **kw):
        return []

    def get_table_options(self, table_name, schema=None, **kw):
        return {}

    def _get_multi(self, method_name, schema=None, filter_names=None):
        names = filter_names or list(self._tables)
        method = getattr(self, method_name)
        return {(schema, name): method(name, schema=schema) for name in names}

    def get_multi_columns(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_columns", schema=schema, filter_names=filter_names)

    def get_multi_pk_constraint(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_pk_constraint", schema=schema, filter_names=filter_names)

    def get_multi_foreign_keys(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_foreign_keys", schema=schema, filter_names=filter_names)

    def get_multi_indexes(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_indexes", schema=schema, filter_names=filter_names)

    def get_multi_unique_constraints(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_unique_constraints", schema=schema, filter_names=filter_names)

    def get_multi_table_comment(self, schema=None, filter_names=None, **kw):
        return self._get_multi("get_table_comment", schema=schema, filter_names=filter_names)

    def get_multi_check_constraints(self, schema=None, filter_names=None, **kw):
        return {(schema, name): [] for name in (filter_names or list(self._tables))}

    def get_multi_table_options(self, schema=None, filter_names=None, **kw):
        return {(schema, name): {} for name in (filter_names or list(self._tables))}

    def reflect_table(self, table, include_columns=None, resolve_fks=False, _reflect_info=None):
        table_data = self._table(table.name)

        for column in table_data["columns"]:
            table.append_column(
                sa.Column(
                    column["name"],
                    column["type"],
                    nullable=column.get("nullable", True),
                    comment=column.get("comment"),
                )
            )

        pk_constraint = table_data.get("pk_constraint")
        if pk_constraint and pk_constraint.get("constrained_columns"):
            table.append_constraint(
                sa.PrimaryKeyConstraint(
                    *[table.c[name] for name in pk_constraint["constrained_columns"]],
                    name=pk_constraint.get("name"),
                )
            )

        for unique_constraint in table_data.get("unique_constraints", []):
            table.append_constraint(
                sa.UniqueConstraint(
                    *[table.c[name] for name in unique_constraint["column_names"]],
                    name=unique_constraint.get("name"),
                )
            )

        for foreign_key in table_data.get("foreign_keys", []):
            referred_schema = foreign_key.get("referred_schema")
            referred_table = foreign_key["referred_table"]
            table_name = (
                f"{referred_schema}.{referred_table}" if referred_schema else referred_table
            )
            table.append_constraint(
                sa.ForeignKeyConstraint(
                    [table.c[name] for name in foreign_key["constrained_columns"]],
                    [f"{table_name}.{name}" for name in foreign_key["referred_columns"]],
                    name=foreign_key.get("name"),
                )
            )

        table.comment = table_data.get("table_comment", {}).get("text")


def _make_connection():
    connection = mock.Mock()
    dialect = CubridDialect()
    dialect.supports_comments = True
    connection.dialect = dialect
    connection.engine = mock.Mock()
    return connection


def test_create_reflect_compare_roundtrip_no_diffs() -> None:
    import sqlalchemy_cubrid.alembic_impl  # noqa: F401

    metadata = sa.MetaData()

    sa.Table(
        "accounts",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", VARCHAR(200), nullable=False),
        sa.Column("display_name", VARCHAR(100), nullable=True),
        sa.UniqueConstraint("email", name="uq_accounts_email"),
        comment="account records",
    )

    sa.Table(
        "projects",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("slug", VARCHAR(60), nullable=False),
        sa.Index("ix_projects_slug", "slug"),
    )

    reflected_schema = {
        "accounts": {
            "columns": [
                {"name": "id", "type": sa.Integer(), "nullable": False, "autoincrement": True},
                {"name": "email", "type": VARCHAR(200), "nullable": False},
                {"name": "display_name", "type": VARCHAR(100), "nullable": True},
            ],
            "pk_constraint": {"name": None, "constrained_columns": ["id"]},
            "unique_constraints": [{"name": "uq_accounts_email", "column_names": ["email"]}],
            "table_comment": {"text": "account records"},
        },
        "projects": {
            "columns": [
                {"name": "id", "type": sa.Integer(), "nullable": False},
                {"name": "account_id", "type": sa.Integer(), "nullable": False},
                {"name": "slug", "type": VARCHAR(60), "nullable": False},
            ],
            "pk_constraint": {"name": None, "constrained_columns": ["id"]},
            "foreign_keys": [
                {
                    "name": "fk_projects_account_id_accounts",
                    "constrained_columns": ["account_id"],
                    "referred_schema": None,
                    "referred_table": "accounts",
                    "referred_columns": ["id"],
                    "options": {},
                }
            ],
            "indexes": [{"name": "ix_projects_slug", "column_names": ["slug"], "unique": False}],
        },
    }

    connection = _make_connection()
    inspector = _MockInspector(connection, reflected_schema)

    with (
        mock.patch("alembic.autogenerate.api.inspect", return_value=inspector),
        mock.patch("alembic.autogenerate.compare.schema.inspect", return_value=inspector),
    ):
        context = MigrationContext.configure(connection=connection, opts={"compare_type": True})
        assert compare_metadata(context, metadata) == []
        assert compare_metadata(context, metadata) == []
