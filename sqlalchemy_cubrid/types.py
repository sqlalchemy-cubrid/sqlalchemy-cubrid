# sqlalchemy_cubrid/types.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.sql import sqltypes

# see: https://www.cubrid.org/manual/en/9.3.0/sql/datatype.html
class _NumericType(object):
    """Base for CUBRID numeric types."""

    def __init__(self, **kw):
        super(_NumericType, self).__init__(**kw)


class _FloatType(_NumericType, sqltypes.Float):
    def __init__(self, precision=None, **kw):
        super(_FloatType, self).__init__(precision=precision, **kw)


class _IntegerType(_NumericType, sqltypes.Integer):
    def __init__(self, display_width=None, **kw):
        self.display_width = display_width
        super(_IntegerType, self).__init__(**kw)


class _StringType(sqltypes.String):
    """Base for CUBRID string types."""

    def __init__(self, national=False, values=None, **kw):
        self.national = national
        self.values = values
        super(_StringType, self).__init__(**kw)

    def __repr__(self):
        attributes = inspect.getargspec(self.__init__)[0][1:]
        attributes.extend(inspect.getargspec(_StringType.__init__)[0][1:])

        params = {}
        for attr in attributes:
            val = getattr(self, attr)
            if val is not None and val is not False:
                params[attr] = val

        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(["%s=%r" % (k, params[k]) for k in params]),
        )


class NUMERIC(_NumericType, sqltypes.NUMERIC):
    """CUBRID NUMERIC type.
    Default value is NUMERIC(15,0)
    """

    __visit_name__ = "NUMERIC"

    def __init__(self, precision=None, scale=None, **kw):
        """Construct a NUMERIC.

        :param precision: Total digits in this number.  If scale and precision
          are both None, values are stored to limits allowed by the server.
        :param scale: The number of digits after the decimal point.

        """
        super(NUMERIC, self).__init__(precision=precision, scale=scale, **kw)


class DECIMAL(_NumericType, sqltypes.DECIMAL):
    """CUBRID DECIMAL type."""

    __visit_name__ = "DECIMAL"

    def __init__(self, precision=None, scale=None, **kw):
        """Construct a DECIMAL.
        :param precision: max number of digits that can be stored (range from 1 thru 38)
        :param scale: number of fractional digits of :param precision: to the
                    right of the decimal point  (range from 0 to :param precision:)
        """
        super(DECIMAL, self).__init__(precision=precision, scale=scale, **kw)


class DOUBLE(_FloatType):
    """CUBRID DOUBLE type."""

    __visit_name__ = "DOUBLE"


class FLOAT(_FloatType, sqltypes.FLOAT):
    """CUBRID FLOAT type."""

    __visit_name__ = "FLOAT"

    def __init__(self, precision=None, **kw):
        """Construct a FLOAT.

        :param precision: Total digits in this number.  If scale and precision
          are both None, values are stored to limits allowed by the server.
        """
        super(FLOAT, self).__init__(precision=precision, **kw)

    def bind_processor(self, dialect):
        return None


class SMALLINT(_IntegerType, sqltypes.SMALLINT):
    """CUBRID SMALLINT type."""

    __visit_name__ = "SMALLINT"


class BIGINT(_IntegerType, sqltypes.BIGINT):
    """CUBRID BIGINT type."""

    __visit_name__ = "BIGINT"


class BIT(sqltypes.TypeEngine):
    """CUBRID BIT type."""

    __visit_name__ = "BIT"

    def __init__(self, length=None, varying=False):
        """Construct a BIT.

        :param length: Optional, number of bits.
        """
        if not varying:
            self.length = (
                length or 1
            )  # BIT without VARYING defaults to length 1
        else:
            self.length = length  # but BIT VARYING can be unlimited-length, so no default
        self.varying = varying


class CHAR(_StringType, sqltypes.CHAR):
    """CUBRID CHAR type, for fixed-length character data."""

    __visit_name__ = "CHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a CHAR.

        :param length: number of characters or bytes allocated.
        """
        super(CHAR, self).__init__(length=length, **kwargs)


class VARCHAR(_StringType, sqltypes.VARCHAR):
    """CUBRID VARCHAR type, for variable-length character data."""

    __visit_name__ = "VARCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a VARCHAR.

        :param length: number of characters or bytes allocated.
        """
        super(VARCHAR, self).__init__(length=length, **kwargs)


class NVARCHAR(_StringType, sqltypes.NVARCHAR):
    """CUBRID NVARCHAR type.
    For variable-length character data in the server's configured national
    character set.
    """

    __visit_name__ = "NVARCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a NVARCHAR.

        :param length: number of characters or bytes allocated.
        """
        kwargs["national"] = True
        super(NVARCHAR, self).__init__(length=length, **kwargs)


class NCHAR(_StringType, sqltypes.NCHAR):
    """CUBRID NCHAR type.
    For fixed-length character data in the server's configured national
    character set.
    """

    __visit_name__ = "NCHAR"

    def __init__(self, length=None, **kwargs):
        """Construct a NCHAR.

        :param length: number of characters or bytes allocated.
        """
        kwargs["national"] = True
        super(NCHAR, self).__init__(length=length, **kwargs)


class STRING(_StringType):
    """CUBRID STRING type
    STRING is a variable-length character string data type.
    STRING is the same as the VARCHAR with the length specified to the maximum value.
    That is, STRING and VARCHAR(1,073,741,823) have the same value.
    """

    __visit_name__ = "STRING"

    def __init__(self, length=None, national=False, **kwargs):
        super(STRING, self).__init__(length=length, **kwargs)


class BLOB(sqltypes.LargeBinary):
    """CUBRID BLOB type"""

    __visit_name__ = "BLOB"


class MONETARY(_FloatType):
    """CUBRID MONETARY type"""

    __visit_name__ = "MONETARY"


class OBJECT(_StringType):
    """CUBRID OBJECT type."""

    __visit_name__ = "OBJECT"


class SET(_StringType):
    """CUBRID SET type."""

    __visit_name__ = "SET"

    def __init__(self, *values, **kw):
        """Construct a SET"""
        self._ddl_values = values
        super(SET, self).__init__(**kw)


class MULTISET(_StringType):
    """CUBRID MULTISET type."""

    __visit_name__ = "MULTISET"

    def __init__(self, *values, **kw):
        """Construct a MULTISET"""
        self._ddl_values = values
        super(MULTISET, self).__init__(**kw)


class SEQUENCE(_StringType):
    """CUBRID SEQUENCE type."""

    __visit_name__ = "SEQUENCE"

    def __init__(self, *values, **kw):
        """Construct a SEQUENCE"""
        self._ddl_values = values
        super(SEQUENCE, self).__init__(**kw)
