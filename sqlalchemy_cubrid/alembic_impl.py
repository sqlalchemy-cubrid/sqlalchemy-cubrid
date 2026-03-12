# sqlalchemy_cubrid/alembic_impl.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Alembic migration support for the CUBRID dialect.

This module provides the Alembic ``DefaultImpl`` subclass that enables
Alembic migrations against a CUBRID database.  It is registered as an
entry-point under ``alembic.ddl`` so that Alembic auto-discovers it
when the target database URL uses the ``cubrid://`` scheme.

Usage::

    # alembic.ini
    [alembic]
    sqlalchemy.url = cubrid://dba:password@localhost:33000/demodb

    # That's it — Alembic will pick up the CUBRID implementation
    # automatically via the ``alembic.ddl`` entry point.

CUBRID-specific notes
---------------------
* **DDL is auto-committed** — CUBRID implicitly commits every DDL
  statement, so ``transactional_ddl`` is set to ``False``.
* **No ALTER COLUMN TYPE** — CUBRID does not support changing a
  column's data type via ``ALTER TABLE … MODIFY``.  Alembic's
  ``alter_column(type_=…)`` will raise.  Use ``batch_alter_table``
  (table recreate) as a workaround.
* **No RENAME COLUMN** — CUBRID ≤ 11.x does not support
  ``ALTER TABLE … RENAME COLUMN``.  Alembic's ``alter_column(new_column_name=…)``
  will raise.  Use ``batch_alter_table`` (table recreate) as a
  workaround.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import sqlalchemy as sa

try:
    from alembic.ddl.impl import DefaultImpl
except ImportError:  # pragma: no cover — optional dependency
    raise ImportError("Alembic is required for migration support. Install it with: pip install sqlalchemy-cubrid[alembic]") from None

if TYPE_CHECKING:
    from typing import Protocol

    from sqlalchemy.sql.type_api import TypeEngine

    class AutogenContextLike(Protocol):
        imports: set[str]


class CubridImpl(DefaultImpl):
    """Alembic migration implementation for CUBRID.

    Registered via the ``alembic.ddl`` entry-point so Alembic
    auto-discovers it for ``cubrid://`` URLs.

    Attributes
    ----------
    __dialect__ : str
        ``"cubrid"`` — matches the SQLAlchemy dialect name.
    transactional_ddl : bool
        ``False`` — CUBRID implicitly commits DDL statements.
    """

    __dialect__: str = "cubrid"
    transactional_ddl: bool = False

    _collection_type_names: set[str] = {"SET", "MULTISET", "SEQUENCE"}

    @staticmethod
    def _normalize_collection_value(value: object) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        if isinstance(value, sa.types.TypeEngine):
            return value.__class__.__name__.lower()
        return repr(value).strip().lower()

    def render_type(
        self, type_obj: TypeEngine[Any], autogen_context: AutogenContextLike
    ) -> str | Literal[False]:
        if type(type_obj).__module__ != "sqlalchemy_cubrid.types":
            return False

        type_name = type_obj.__class__.__name__
        if type_name not in self._collection_type_names:
            return False

        values = getattr(type_obj, "_ddl_values", ())
        rendered_values: list[str] = []

        for value in values:
            if isinstance(value, str):
                rendered_values.append(repr(value))
            elif isinstance(value, sa.types.TypeEngine):
                rendered_values.append(value.__class__.__name__)
            else:
                rendered_values.append(repr(value))

        autogen_context.imports.add("from sqlalchemy_cubrid import types as cubrid_types")
        args = ", ".join(rendered_values)
        return f"cubrid_types.{type_name}({args})"

    def compare_type(self, inspector_column: sa.Column[Any], metadata_column: sa.Column[Any]) -> bool:
        inspector_type = inspector_column.type
        metadata_type = metadata_column.type

        inspector_name = inspector_type.__class__.__name__
        metadata_name = metadata_type.__class__.__name__

        is_inspector_collection = inspector_name in self._collection_type_names
        is_metadata_collection = metadata_name in self._collection_type_names

        if not is_inspector_collection and not is_metadata_collection:
            return super().compare_type(inspector_column, metadata_column)

        if is_inspector_collection != is_metadata_collection:
            return True

        if inspector_name != metadata_name:
            return True

        inspector_values = [
            self._normalize_collection_value(value)
            for value in getattr(inspector_type, "_ddl_values", ())
        ]
        metadata_values = [
            self._normalize_collection_value(value)
            for value in getattr(metadata_type, "_ddl_values", ())
        ]

        if inspector_name == "SEQUENCE":
            return inspector_values != metadata_values

        return set(inspector_values) != set(metadata_values)
