# sqlalchemy_cubrid/types.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""CUBRID-specific SQLAlchemy type definitions.

See: https://www.cubrid.org/manual/en/11.0/sql/datatype.html
"""

from __future__ import annotations

import inspect

from sqlalchemy.sql import sqltypes


# ---------------------------------------------------------------------------
# Base Mixins
# ---------------------------------------------------------------------------


class _NumericType:
    """Base for CUBRID numeric types."""

    def __init__(self, **kw):
        super().__init__(**kw)


class _FloatType(_NumericType, sqltypes.Float):
    def __init__(self, precision=None, **kw):
        super().__init__(precision=precision, **kw)


class _IntegerType(_NumericType, sqltypes.Integer):
    def __init__(self, display_width=None, **kw):
        self.display_width = display_width
        super().__init__(**kw)


class _StringType(sqltypes.String):
    """Base for CUBRID string types."""

    def __init__(self, national=False, values=None, **kw):
        self.national = national
        self.values = values
        super().__init__(**kw)

    def __repr__(self):
        try:
            sig = inspect.signature(self.__class__.__init__)
            attributes = [p.name for p in sig.parameters.values() if p.name != "self"]
        except (ValueError, TypeError):
            attributes = []

        params = {}
        for attr in attributes:
            val = getattr(self, attr, None)
            if val is not None and val is not False:
                params[attr] = val

        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(f"{k}={v!r}" for k, v in params.items()),
        )


# ---------------------------------------------------------------------------
# Numeric Types
# ---------------------------------------------------------------------------


class SMALLINT(_IntegerType, sqltypes.SMALLINT):
    """CUBRID SMALLINT type."""

    __visit_name__ = "SMALLINT"


class BIGINT(_IntegerType, sqltypes.BIGINT):
    """CUBRID BIGINT type."""

    __visit_name__ = "BIGINT"


class NUMERIC(_NumericType, sqltypes.NUMERIC):
    """CUBRID NUMERIC type."""

    __visit_name__ = "NUMERIC"

    def __init__(self, precision=None, scale=None, **kw):
        """Construct a NUMERIC.

        :param precision: Total digits in this number.  If scale and precision
          are both None, values are stored to limits allowed by the server.
        :param scale: The number of digits after the decimal point.
        """
        super().__init__(precision=precision, scale=scale, **kw)


class DECIMAL(_NumericType, sqltypes.DECIMAL):
    """CUBRID DECIMAL type."""

    __visit_name__ = "DECIMAL"

    def __init__(self, precision=None, scale=None, **kw):
        """Construct a DECIMAL.

        :param precision: Total digits in this number.  If scale and precision
          are both None, values are stored to limits allowed by the server.
          (range from 1 thru 38)
        :param scale: The number of digits following the decimal point.
        """
        super().__init__(precision=precision, scale=scale, **kw)


class FLOAT(_FloatType, sqltypes.FLOAT):
    """CUBRID FLOAT type."""

    __visit_name__ = "FLOAT"

    def __init__(self, precision=7, **kw):
        """Construct a FLOAT.

        :param precision: Defaults to 7.  Total digits in this number.
          (range from 1 thru 38)
        """
        super().__init__(precision=precision, **kw)

    def bind_processor(self, dialect):
        return None


class REAL(_FloatType, sqltypes.FLOAT):
    """CUBRID REAL type."""

    __visit_name__ = "REAL"

    def __init__(self, precision=None, **kw):
        """Construct a REAL.

        :param precision: Total digits in this number.
        """
        super().__init__(precision=precision, **kw)

    def bind_processor(self, dialect):
        return None


class DOUBLE(_FloatType):
    """CUBRID DOUBLE type."""

    __visit_name__ = "DOUBLE"


class DOUBLE_PRECISION(_FloatType):
    """CUBRID DOUBLE PRECISION type."""

    __visit_name__ = "DOUBLE_PRECISION"


# ---------------------------------------------------------------------------
# Bit String Types
# ---------------------------------------------------------------------------


class BIT(sqltypes.TypeEngine):
    """CUBRID BIT type."""

    __visit_name__ = "BIT"

    def __init__(self, length=1, varying=False):
        """Construct a BIT.

        :param length: Defaults to 1.  Optional, number of bits.
        :param varying: If True, use BIT VARYING.
        """
        if not varying:
            self.length = length or 1
        else:
            self.length = length  # BIT VARYING can be unlimited-length
        self.varying = varying


# ---------------------------------------------------------------------------
# Character String Types
# ---------------------------------------------------------------------------


class CHAR(_StringType, sqltypes.CHAR):
    """CUBRID CHAR type, for fixed-length character data."""

    __visit_name__ = "CHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a CHAR.

        :param length: The number of characters.
        """
        super().__init__(length=length, **kwargs)


class VARCHAR(_StringType, sqltypes.VARCHAR):
    """CUBRID VARCHAR type, for variable-length character data."""

    __visit_name__ = "VARCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a VARCHAR.

        :param length: The number of characters.
        """
        super().__init__(length=length, **kwargs)


class NCHAR(_StringType, sqltypes.NCHAR):
    """CUBRID NCHAR type.

    For fixed-length character data in the server's configured national
    character set.
    """

    __visit_name__ = "NCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a NCHAR.

        :param length: The number of characters.
        """
        kwargs["national"] = True
        super().__init__(length=length, **kwargs)


class NVARCHAR(_StringType, sqltypes.NVARCHAR):
    """CUBRID NVARCHAR type.

    For variable-length character data in the server's configured national
    character set.
    """

    __visit_name__ = "NVARCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a NVARCHAR.

        :param length: The number of characters.
        """
        kwargs["national"] = True
        super().__init__(length=length, **kwargs)


class STRING(_StringType):
    """CUBRID STRING type.

    STRING is a variable-length character string data type.
    STRING is the same as the VARCHAR with the length specified to the maximum value.
    That is, STRING and VARCHAR(1,073,741,823) have the same value.
    """

    __visit_name__ = "STRING"

    def __init__(self, length=None, national=False, **kwargs):
        super().__init__(length=length, **kwargs)


# ---------------------------------------------------------------------------
# LOB Types
# ---------------------------------------------------------------------------


class BLOB(sqltypes.LargeBinary):
    """CUBRID BLOB type."""

    __visit_name__ = "BLOB"


class CLOB(sqltypes.Text):
    """CUBRID CLOB type."""

    __visit_name__ = "CLOB"


# ---------------------------------------------------------------------------
# Collection Types
# ---------------------------------------------------------------------------


class SET(_StringType):
    """CUBRID SET type."""

    __visit_name__ = "SET"

    def __init__(self, *values, **kw):
        """Construct a SET."""
        self._ddl_values = values
        super().__init__(**kw)


class MULTISET(_StringType):
    """CUBRID MULTISET type."""

    __visit_name__ = "MULTISET"

    def __init__(self, *values, **kw):
        """Construct a MULTISET."""
        self._ddl_values = values
        super().__init__(**kw)


class SEQUENCE(_StringType):
    """CUBRID SEQUENCE type."""

    __visit_name__ = "SEQUENCE"

    def __init__(self, *values, **kw):
        """Construct a SEQUENCE."""
        self._ddl_values = values
        super().__init__(**kw)


# ---------------------------------------------------------------------------
# Monetary Type
# ---------------------------------------------------------------------------


class MONETARY(sqltypes.TypeEngine):
    """CUBRID MONETARY type.

    Stores monetary values with currency.  Internally represented as a
    DOUBLE with an associated currency code.
    """

    __visit_name__ = "MONETARY"


# ---------------------------------------------------------------------------
# Object Type
# ---------------------------------------------------------------------------


class OBJECT(sqltypes.TypeEngine):
    """CUBRID OBJECT type.

    Represents a reference to another CUBRID class instance (OID).
    This is a CUBRID-specific type with no direct equivalent in other databases.
    """

    __visit_name__ = "OBJECT"
