# sqlalchemy_cubrid/dml.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""CUBRID DML constructs."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from sqlalchemy import exc, util
from sqlalchemy.sql._typing import _DMLTableArgument
from sqlalchemy.sql.base import _exclusive_against, _generative, ColumnCollection, ReadOnlyColumnCollection
from sqlalchemy.sql.dml import Insert as StandardInsert
from sqlalchemy.sql.elements import ClauseElement, KeyedColumnElement
from sqlalchemy.sql.expression import alias
from sqlalchemy.sql.selectable import NamedFromClause
from sqlalchemy.util.typing import Self

__all__ = ("Insert", "insert")

_UpdateArg = Union[
    Mapping[str, Any],
    List[Tuple[str, Any]],
]


def insert(table: _DMLTableArgument) -> Insert:
    """Construct a CUBRID-specific variant :class:`Insert` construct.

    Includes :meth:`Insert.on_duplicate_key_update`.
    """
    return Insert(table)


class Insert(StandardInsert):
    """CUBRID-specific implementation of INSERT.

    Adds methods for CUBRID-specific syntaxes such as ON DUPLICATE KEY UPDATE.
    """

    stringify_dialect = "cubrid"
    inherit_cache = False

    @property
    def inserted(self) -> ReadOnlyColumnCollection[str, KeyedColumnElement[Any]]:
        """Provide the "inserted" namespace for an ON DUPLICATE KEY UPDATE statement.

        CUBRID uses VALUES() to reference the row being inserted,
        identical to MySQL's pre-8.0 syntax.
        """
        return self.inserted_alias.columns

    @util.memoized_property
    def inserted_alias(self) -> NamedFromClause:
        return alias(self.table, name="inserted")

    @_generative
    @_exclusive_against(
        "_post_values_clause",
        msgs={
            "_post_values_clause": "This Insert construct already "
            "has an ON DUPLICATE KEY clause present"
        },
    )
    def on_duplicate_key_update(self, *args: _UpdateArg, **kw: Any) -> Self:
        """Specifies the ON DUPLICATE KEY UPDATE clause.

        :param **kw: Column keys linked to UPDATE values.
        :param *args: A dictionary or list of 2-tuples as a single positional argument.
        """
        arg_values = list(args)
        values = kw

        if arg_values and kw:
            raise exc.ArgumentError(
                "Can't pass kwargs and positional arguments simultaneously"
            )
        if arg_values:
            if len(arg_values) > 1:
                raise exc.ArgumentError(
                    "Only a single dictionary or list of tuples "
                    "is accepted positionally."
                )
            values = next(iter(arg_values), kw)

        self._post_values_clause = OnDuplicateClause(self.inserted_alias, values)
        return self


class OnDuplicateClause(ClauseElement):
    __visit_name__ = "on_duplicate_key_update"

    _parameter_ordering: Optional[List[str]] = None
    update: Dict[str, Any]
    stringify_dialect = "cubrid"

    def __init__(self, inserted_alias: NamedFromClause, update: _UpdateArg) -> None:
        self.inserted_alias = inserted_alias
        if isinstance(update, list) and (update and isinstance(update[0], tuple)):
            self._parameter_ordering = [key for key, _ in update]
            update = dict(update)
        if isinstance(update, dict):
            if not update:
                raise ValueError("update parameter dictionary must not be empty")
        elif isinstance(update, ColumnCollection):
            update = dict(update)
        else:
            raise ValueError(
                "update parameter must be a non-empty dictionary "
                "or a ColumnCollection such as the `.c.` collection "
                "of a Table object"
            )
        self.update = update
