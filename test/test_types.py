# test/test_types.py
"""Offline type tests — no live CUBRID required.

Verify that custom type classes instantiate correctly and have proper
visit names, repr, and inheritance.
"""

from __future__ import annotations

from sqlalchemy.sql import sqltypes

from sqlalchemy_cubrid.types import (
    BIGINT,
    BIT,
    BLOB,
    CHAR,
    CLOB,
    DECIMAL,
    DOUBLE,
    DOUBLE_PRECISION,
    FLOAT,
    MONETARY,
    MULTISET,
    NCHAR,
    NUMERIC,
    NVARCHAR,
    OBJECT,
    REAL,
    SEQUENCE,
    SET,
    SMALLINT,
    STRING,
    VARCHAR,
)


class TestVisitNames:
    """Every type must declare a __visit_name__ matching the CUBRID type."""

    def test_smallint(self):
        assert SMALLINT.__visit_name__ == "SMALLINT"

    def test_bigint(self):
        assert BIGINT.__visit_name__ == "BIGINT"

    def test_numeric(self):
        assert NUMERIC.__visit_name__ == "NUMERIC"

    def test_decimal(self):
        assert DECIMAL.__visit_name__ == "DECIMAL"

    def test_float(self):
        assert FLOAT.__visit_name__ == "FLOAT"

    def test_real(self):
        assert REAL.__visit_name__ == "REAL"

    def test_double(self):
        assert DOUBLE.__visit_name__ == "DOUBLE"

    def test_double_precision(self):
        assert DOUBLE_PRECISION.__visit_name__ == "DOUBLE_PRECISION"

    def test_bit(self):
        assert BIT.__visit_name__ == "BIT"

    def test_char(self):
        assert CHAR.__visit_name__ == "CHAR"

    def test_varchar(self):
        assert VARCHAR.__visit_name__ == "VARCHAR"

    def test_nchar(self):
        assert NCHAR.__visit_name__ == "NCHAR"

    def test_nvarchar(self):
        assert NVARCHAR.__visit_name__ == "NVARCHAR"

    def test_string(self):
        assert STRING.__visit_name__ == "STRING"

    def test_blob(self):
        assert BLOB.__visit_name__ == "BLOB"

    def test_clob(self):
        assert CLOB.__visit_name__ == "CLOB"

    def test_set(self):
        assert SET.__visit_name__ == "SET"

    def test_multiset(self):
        assert MULTISET.__visit_name__ == "MULTISET"

    def test_sequence(self):
        assert SEQUENCE.__visit_name__ == "SEQUENCE"

    def test_monetary(self):
        assert MONETARY.__visit_name__ == "MONETARY"

    def test_object(self):
        assert OBJECT.__visit_name__ == "OBJECT"


class TestTypeInstantiation:
    """Verify types can be constructed without errors."""

    def test_smallint(self):
        t = SMALLINT()
        assert isinstance(t, sqltypes.SMALLINT)

    def test_bigint(self):
        t = BIGINT()
        assert isinstance(t, sqltypes.BIGINT)

    def test_numeric_defaults(self):
        t = NUMERIC()
        assert t.precision is None
        assert t.scale is None

    def test_numeric_with_params(self):
        t = NUMERIC(precision=10, scale=2)
        assert t.precision == 10
        assert t.scale == 2

    def test_decimal_with_params(self):
        t = DECIMAL(precision=15, scale=4)
        assert t.precision == 15
        assert t.scale == 4

    def test_float_default_precision(self):
        t = FLOAT()
        assert t.precision == 7

    def test_float_custom_precision(self):
        t = FLOAT(precision=14)
        assert t.precision == 14

    def test_real(self):
        t = REAL()
        assert isinstance(t, sqltypes.Float)

    def test_double(self):
        t = DOUBLE()
        assert isinstance(t, sqltypes.Float)

    def test_bit_default(self):
        t = BIT()
        assert t.length == 1
        assert t.varying is False

    def test_bit_varying(self):
        t = BIT(length=256, varying=True)
        assert t.length == 256
        assert t.varying is True

    def test_char(self):
        t = CHAR(length=50)
        assert isinstance(t, sqltypes.CHAR)
        assert t.length == 50

    def test_varchar(self):
        t = VARCHAR(length=255)
        assert isinstance(t, sqltypes.VARCHAR)
        assert t.length == 255

    def test_nchar_national(self):
        t = NCHAR(length=100)
        assert t.national is True

    def test_nvarchar_national(self):
        t = NVARCHAR(length=200)
        assert t.national is True

    def test_string(self):
        t = STRING()
        assert isinstance(t, sqltypes.String)

    def test_blob(self):
        t = BLOB()
        assert isinstance(t, sqltypes.LargeBinary)

    def test_clob(self):
        t = CLOB()
        assert isinstance(t, sqltypes.Text)

    def test_monetary(self):
        t = MONETARY()
        assert isinstance(t, sqltypes.TypeEngine)

    def test_object(self):
        t = OBJECT()
        assert isinstance(t, sqltypes.TypeEngine)

class TestCollectionTypes:
    """Test SET, MULTISET, SEQUENCE (CUBRID collection types)."""

    def test_set_stores_values(self):
        t = SET("a", "b", "c")
        assert t._ddl_values == ("a", "b", "c")

    def test_multiset_stores_values(self):
        t = MULTISET("x", "y")
        assert t._ddl_values == ("x", "y")

    def test_sequence_stores_values(self):
        t = SEQUENCE("p", "q")
        assert t._ddl_values == ("p", "q")

    def test_set_with_type_objects(self):
        t = SET(CHAR(10), VARCHAR(255))
        assert len(t._ddl_values) == 2

    def test_empty_set(self):
        t = SET()
        assert t._ddl_values == ()


class TestRepr:
    """Test _StringType __repr__."""

    def test_char_repr(self):
        t = CHAR(length=50)
        r = repr(t)
        assert "CHAR" in r
        assert "50" in r

    def test_varchar_repr(self):
        t = VARCHAR(length=255)
        r = repr(t)
        assert "VARCHAR" in r
        assert "255" in r

    def test_nchar_repr(self):
        t = NCHAR(length=100)
        r = repr(t)
        assert "NCHAR" in r


class TestBindProcessor:
    """FLOAT and REAL bind_processor should return None (pass-through)."""

    def test_float_bind_processor(self):
        t = FLOAT()
        assert t.bind_processor(None) is None

    def test_real_bind_processor(self):
        t = REAL()
        assert t.bind_processor(None) is None

    def test_repr_exception_path_valueerror(self):
        """Test __repr__ when inspect.signature raises ValueError."""
        from unittest.mock import patch
        from sqlalchemy_cubrid.types import CHAR

        t = CHAR(length=50)
        with patch("sqlalchemy_cubrid.types.inspect.signature", side_effect=ValueError("no sig")):
            r = repr(t)
            assert "CHAR" in r
            # When signature fails, attributes=[] so no params shown
            assert r == "CHAR()"

    def test_repr_exception_path_typeerror(self):
        """Test __repr__ when inspect.signature raises TypeError."""
        from unittest.mock import patch
        from sqlalchemy_cubrid.types import VARCHAR

        t = VARCHAR(length=100)
        with patch("sqlalchemy_cubrid.types.inspect.signature", side_effect=TypeError("bad")):
            r = repr(t)
            assert "VARCHAR" in r
            assert r == "VARCHAR()"
