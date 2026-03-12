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

from typing import TYPE_CHECKING

try:
    from alembic.ddl.impl import DefaultImpl
except ImportError:  # pragma: no cover — optional dependency
    raise ImportError(
        "Alembic is required for migration support.  "
        "Install it with:  pip install sqlalchemy-cubrid[alembic]"
    ) from None

if TYPE_CHECKING:
    pass


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

    __dialect__ = "cubrid"
    transactional_ddl = False
