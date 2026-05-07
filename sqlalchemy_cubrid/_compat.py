from __future__ import annotations

from typing import Any

from sqlalchemy.sql import elements, visitors


def is_literal_value(value: Any) -> bool:
    """Check if value is a plain Python literal (not a SQL element or schema object)."""
    if isinstance(value, visitors.Visitable):
        return False
    if hasattr(value, "__clause_element__"):
        return False
    return True


def bind_with_type(element: elements.BindParameter[Any], type_: Any) -> elements.BindParameter[Any]:
    """Create a copy of *element* with *type_* overridden, preserving all internal state."""
    cloned = element._clone()
    cloned.type = type_
    return cloned


def get_for_update_arg(select: Any) -> Any | None:
    return getattr(select, "_for_update_arg", None)


def get_limit_clause(select: Any) -> Any | None:
    return getattr(select, "_limit_clause", None)


def get_offset_clause(select: Any) -> Any | None:
    return getattr(select, "_offset_clause", None)


def get_distinct(select: Any) -> Any:
    return getattr(select, "_distinct", False)
