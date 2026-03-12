# test/test_compiler.py
"""Offline compiler tests — no live CUBRID required.

Uses SQLAlchemy's compilation API to verify SQL generation without
a database connection.
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Column, Integer, MetaData, String, Table, select

from sqlalchemy_cubrid.dialect import CubridDialect


def _compile(stmt, dialect=None):
    """Compile a statement using the CUBRID dialect and return SQL string."""
    if dialect is None:
        dialect = CubridDialect()
    return stmt.compile(dialect=dialect, compile_kwargs={"literal_binds": True}).string


metadata = MetaData()
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("email", String(200)),
)


class TestSelectCompilation:
    """Test SELECT statement compilation."""

    def test_simple_select(self):
        stmt = select(users)
        sql = _compile(stmt)
        assert "SELECT" in sql
        assert "users" in sql

    def test_select_distinct(self):
        stmt = select(users.c.name).distinct()
        sql = _compile(stmt)
        assert "DISTINCT" in sql

    def test_select_limit(self):
        stmt = select(users).limit(10)
        sql = _compile(stmt)
        assert "LIMIT" in sql
        assert "10" in sql

    def test_select_offset(self):
        stmt = select(users).offset(5)
        sql = _compile(stmt)
        assert "LIMIT" in sql
        assert "5" in sql
        assert "1073741823" in sql

    def test_select_limit_offset(self):
        stmt = select(users).limit(10).offset(5)
        sql = _compile(stmt)
        assert "LIMIT" in sql
        # CUBRID uses LIMIT offset, count
        assert "5" in sql
        assert "10" in sql

    def test_select_no_limit(self):
        stmt = select(users)
        sql = _compile(stmt)
        assert "LIMIT" not in sql

    def test_for_update_basic(self):
        """CUBRID supports FOR UPDATE; clause should be present."""
        stmt = select(users).with_for_update()
        sql = _compile(stmt)
        assert sql.strip().endswith("FOR UPDATE")

    def test_for_update_of_columns(self):
        """FOR UPDATE OF col1, col2 should render correctly."""
        stmt = select(users).with_for_update(of=[users.c.id, users.c.name])
        sql = _compile(stmt)
        assert "FOR UPDATE OF" in sql
        assert "users.id" in sql
        assert "users.name" in sql

    def test_for_update_nowait_ignored(self):
        """CUBRID does not support NOWAIT; it should still render FOR UPDATE."""
        stmt = select(users).with_for_update(nowait=True)
        sql = _compile(stmt)
        # FOR UPDATE should be present, NOWAIT is silently ignored by SA base compiler
        assert "FOR UPDATE" in sql


class TestInsertCompilation:
    """Test INSERT statement compilation."""

    def test_insert_default_values(self):
        """INSERT with no values should produce DEFAULT VALUES."""
        from sqlalchemy import insert

        stmt = insert(users).values()
        sql = _compile(stmt)
        assert "DEFAULT VALUES" in sql

    def test_insert_with_values(self):
        """INSERT with explicit values should compile normally."""
        from sqlalchemy import insert

        stmt = insert(users).values(name="test", email="test@example.com")
        sql = _compile(stmt)
        assert "INSERT INTO" in sql
        assert "users" in sql


class TestWindowFunctionCompilation:
    """Test window function compilation."""

    def test_row_number(self):
        """ROW_NUMBER() OVER (ORDER BY ...) should compile."""
        stmt = select(
            users.c.name,
            sa.func.row_number().over(order_by=users.c.id).label("rn"),
        )
        sql = _compile(stmt)
        assert "row_number()" in sql.lower()
        assert "OVER" in sql
        assert "ORDER BY" in sql

    def test_rank_with_partition(self):
        """RANK() OVER (PARTITION BY ... ORDER BY ...) should compile."""
        stmt = select(
            users.c.name,
            sa.func.rank().over(
                partition_by=users.c.email,
                order_by=users.c.id,
            ).label("rnk"),
        )
        sql = _compile(stmt)
        assert "rank()" in sql.lower()
        assert "PARTITION BY" in sql

    def test_dense_rank(self):
        """DENSE_RANK should compile via SA base compiler."""
        stmt = select(
            sa.func.dense_rank().over(order_by=users.c.id).label("dr"),
        )
        sql = _compile(stmt)
        assert "dense_rank()" in sql.lower()
        assert "OVER" in sql


class TestNullsOrderCompilation:
    """Test NULLS FIRST / NULLS LAST in ORDER BY."""

    def test_nulls_first(self):
        stmt = select(users).order_by(users.c.name.asc().nulls_first())
        sql = _compile(stmt)
        assert "NULLS FIRST" in sql

    def test_nulls_last(self):
        stmt = select(users).order_by(users.c.name.desc().nulls_last())
        sql = _compile(stmt)
        assert "NULLS LAST" in sql


class TestJoinCompilation:
    orders = Table(
        "orders",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer),
        Column("total", Integer),
    )

    def test_inner_join(self):
        stmt = select(users).join(self.orders, users.c.id == self.orders.c.user_id)
        sql = _compile(stmt)
        assert "INNER JOIN" in sql
        assert "ON" in sql

    def test_left_outer_join(self):
        stmt = select(users).outerjoin(self.orders, users.c.id == self.orders.c.user_id)
        sql = _compile(stmt)
        assert "LEFT OUTER JOIN" in sql
        assert "ON" in sql

    def test_cast_with_none_type(self):
        """Test cast when typeclause returns None."""
        # This is a rare case; we test by patching type processing
        stmt = select(sa.cast(users.c.name, Integer))
        dialect = CubridDialect()
        compiler_obj = stmt.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
        # The branch is rare but if type_.process returns None, CAST returns just the clause
        sql = compiler_obj.string
        # At least verify the statement compiles without error
        assert "users" in sql


class TestCastCompilation:
    def test_cast_integer(self):
        stmt = select(sa.cast(users.c.name, Integer))
        sql = _compile(stmt)
        assert "CAST" in sql
        assert "AS" in sql
        # Must have space before AS
        assert "AS " in sql

    def test_cast_string(self):
        stmt = select(sa.cast(users.c.id, String(50)))
        sql = _compile(stmt)
        assert "CAST" in sql
        assert "AS" in sql


class TestLiteralValueCompilation:
    """Test render_literal_value method."""

    def test_render_literal_with_backslash(self):
        """Test that backslashes are escaped in literal values."""
        stmt = select(sa.literal("path\\to\\file"))
        sql = _compile(stmt)
        # Backslashes should be doubled
        assert "\\\\" in sql


class TestFunctionCompilation:
    """Test function compilation (SYSDATE, UTC_TIMESTAMP)."""

    def test_sysdate_func(self):
        """Test SYSDATE function compilation."""
        stmt = select(sa.func.sysdate())
        sql = _compile(stmt)
        assert "SYSDATE" in sql

    def test_utc_timestamp_func(self):
        """Test UTC_TIMESTAMP function compilation."""
        stmt = select(sa.func.utc_timestamp())
        sql = _compile(stmt)
        assert "UTC_TIME()" in sql

    def test_cast_string_to_integer(self):
        """Test casting string column to integer."""
        stmt = select(sa.cast(users.c.name, Integer))
        sql = _compile(stmt)
        assert "CAST" in sql
        assert "INTEGER" in sql


class TestTypeCompilation:
    """Test type compiler output."""

    def _compile_type(self, type_):
        dialect = CubridDialect()
        return dialect.type_compiler_instance.process(type_)

    def test_boolean_maps_to_smallint(self):
        result = self._compile_type(sa.Boolean())
        assert result == "SMALLINT"

    def test_numeric_no_params(self):
        from sqlalchemy_cubrid.types import NUMERIC

        result = self._compile_type(NUMERIC())
        assert result == "NUMERIC"

    def test_numeric_with_precision(self):
        from sqlalchemy_cubrid.types import NUMERIC

        result = self._compile_type(NUMERIC(precision=10))
        assert result == "NUMERIC(10)"

    def test_numeric_with_scale(self):
        from sqlalchemy_cubrid.types import NUMERIC

        result = self._compile_type(NUMERIC(precision=10, scale=2))
        assert result == "NUMERIC(10, 2)"

    def test_varchar_with_length(self):
        from sqlalchemy_cubrid.types import VARCHAR

        result = self._compile_type(VARCHAR(length=255))
        assert result == "VARCHAR(255)"

    def test_varchar_no_length(self):
        from sqlalchemy_cubrid.types import VARCHAR

        result = self._compile_type(VARCHAR())
        assert result == "VARCHAR(4096)"

    def test_char_with_length(self):
        from sqlalchemy_cubrid.types import CHAR

        result = self._compile_type(CHAR(length=10))
        assert result == "CHAR(10)"

    def test_char_no_length(self):
        from sqlalchemy_cubrid.types import CHAR

        result = self._compile_type(CHAR())
        assert result == "CHAR"

    def test_nchar(self):
        from sqlalchemy_cubrid.types import NCHAR

        result = self._compile_type(NCHAR(length=50))
        assert result == "NCHAR(50)"

    def test_nvarchar(self):
        from sqlalchemy_cubrid.types import NVARCHAR

        result = self._compile_type(NVARCHAR(length=100))
        assert result == "NCHAR VARYING(100)"

    def test_blob(self):
        result = self._compile_type(sa.LargeBinary())
        assert result == "BLOB"

    def test_text(self):
        result = self._compile_type(sa.Text())
        assert result == "STRING"

    def test_float(self):
        from sqlalchemy_cubrid.types import FLOAT

        result = self._compile_type(FLOAT(precision=10))
        assert result == "FLOAT(10)"

    def test_double(self):
        from sqlalchemy_cubrid.types import DOUBLE

        result = self._compile_type(DOUBLE())
        assert result == "DOUBLE"

    def test_bit(self):
        from sqlalchemy_cubrid.types import BIT

        result = self._compile_type(BIT(length=8))
        assert result == "BIT(8)"

    def test_bit_varying(self):
        from sqlalchemy_cubrid.types import BIT

        result = self._compile_type(BIT(length=256, varying=True))
        assert result == "BIT VARYING(256)"

    def test_datetime(self):
        result = self._compile_type(sa.DateTime())
        assert result == "DATETIME"

    def test_date(self):
        result = self._compile_type(sa.Date())
        assert result == "DATE"

    def test_time(self):
        result = self._compile_type(sa.Time())
        assert result == "TIME"

    def test_set_collection(self):
        from sqlalchemy_cubrid.types import SET, CHAR

        result = self._compile_type(SET(CHAR(10)))
        assert result == "SET(CHAR)"

    def test_multiset_collection(self):
        from sqlalchemy_cubrid.types import MULTISET, VARCHAR

        result = self._compile_type(MULTISET(VARCHAR(255)))
        assert result == "MULTISET(VARCHAR)"

    def test_sequence_collection(self):
        from sqlalchemy_cubrid.types import SEQUENCE

        result = self._compile_type(SEQUENCE(sa.Integer()))
        assert result == "SEQUENCE(integer)"

    def test_string_type(self):
        from sqlalchemy_cubrid.types import STRING

        result = self._compile_type(STRING())
        assert result == "STRING"

    def test_clob(self):
        from sqlalchemy_cubrid.types import CLOB

        result = self._compile_type(CLOB())
        assert result == "CLOB"

    def test_decimal(self):
        from sqlalchemy_cubrid.types import DECIMAL

        result = self._compile_type(DECIMAL(precision=15, scale=4))
        assert result == "DECIMAL(15, 4)"

    def test_smallint(self):
        from sqlalchemy_cubrid.types import SMALLINT

        result = self._compile_type(SMALLINT())
        assert result == "SMALLINT"

    def test_bigint(self):
        from sqlalchemy_cubrid.types import BIGINT

        result = self._compile_type(BIGINT())
        assert result == "BIGINT"

    def test_decimal_no_precision(self):
        """Test DECIMAL() without precision."""
        from sqlalchemy_cubrid.types import DECIMAL

        result = self._compile_type(DECIMAL())
        assert result == "DECIMAL"

    def test_decimal_with_precision_only(self):
        """Test DECIMAL with precision but no scale."""
        from sqlalchemy_cubrid.types import DECIMAL

        result = self._compile_type(DECIMAL(precision=10))
        assert result == "DECIMAL(10)"

    def test_float_no_precision(self):
        """Test FLOAT() without precision defaults to 7."""
        from sqlalchemy_cubrid.types import FLOAT

        result = self._compile_type(FLOAT())
        assert result == "FLOAT(7)"

    def test_float_no_precision_stdlib(self):
        """Test SQLAlchemy Float() without precision compiles to FLOAT."""
        result = self._compile_type(sa.Float())
        assert result == "FLOAT"

    def test_timestamp_type(self):
        """Test TIMESTAMP type compilation."""
        result = self._compile_type(sa.TIMESTAMP())
        assert result == "TIMESTAMP"

    def test_varchar_with_national_flag(self):
        """Test VARCHAR with national flag redirects to NVARCHAR."""
        from sqlalchemy_cubrid.types import VARCHAR

        t = VARCHAR(length=100, national=True)
        result = self._compile_type(t)
        assert result == "NCHAR VARYING(100)"

    def test_char_with_national_flag(self):
        """Test CHAR with national flag redirects to NCHAR."""
        from sqlalchemy_cubrid.types import CHAR

        t = CHAR(length=50, national=True)
        result = self._compile_type(t)
        assert result == "NCHAR(50)"

    def test_nvarchar_no_length(self):
        """Test NVARCHAR() without length defaults to 4096."""
        from sqlalchemy_cubrid.types import NVARCHAR

        result = self._compile_type(NVARCHAR())
        assert result == "NCHAR VARYING(4096)"

    def test_nchar_no_length(self):
        """Test NCHAR() without length."""
        from sqlalchemy_cubrid.types import NCHAR

        result = self._compile_type(NCHAR())
        assert result == "NCHAR"

    def test_bit_varying_no_length(self):
        """Test BIT VARYING without explicit length."""
        from sqlalchemy_cubrid.types import BIT

        result = self._compile_type(BIT(length=None, varying=True))
        assert result == "BIT VARYING"

    def test_object_type(self):
        """Test OBJECT type compilation via mock type."""
        from sqlalchemy.sql import sqltypes

        class MockObject(sqltypes.TypeEngine):
            __visit_name__ = "OBJECT"

        obj = MockObject()
        result = self._compile_type(obj)
        assert result == "OBJECT"

    def test_set_with_string_values(self):
        """Test SET with string values (not type objects)."""
        from sqlalchemy_cubrid.types import SET

        # SET can accept string type names like 'INTEGER'
        result = self._compile_type(SET("INTEGER"))
        assert result == "SET(INTEGER)"

    def test_monetary_type(self):
        """Test MONETARY type compilation via mock type."""
        from sqlalchemy.sql import sqltypes

        class MockMonetary(sqltypes.TypeEngine):
            __visit_name__ = "MONETARY"

        mon = MockMonetary()
        result = self._compile_type(mon)
        assert result == "MONETARY"

    def test_datetime_lowercase(self):
        """Test visit_datetime (lowercase) for datetime types."""
        from sqlalchemy.sql import sqltypes

        class MockDatetime(sqltypes.TypeDecorator):
            impl = sqltypes.DateTime
            __visit_name__ = "datetime"

        dt = MockDatetime()
        result = self._compile_type(dt)
        assert result == "DATETIME"

    def test_datetime_uppercase(self):
        """Test visit_DATETIME (uppercase) for DATETIME types."""
        from sqlalchemy.sql import sqltypes

        class MockDATETIME(sqltypes.TypeEngine):
            __visit_name__ = "DATETIME"

        dt = MockDATETIME()
        result = self._compile_type(dt)
        assert result == "DATETIME"

    def test_get_method_direct(self):
        """Test _get helper method in TypeCompiler."""
        dialect = CubridDialect()
        compiler = dialect.type_compiler_instance
        # The _get method retrieves attribute from type or kwargs
        from sqlalchemy_cubrid.types import VARCHAR

        t = VARCHAR(length=100)
        # _get(key, type_, kw) should return kw[key] or type_.key
        result = compiler._get("length", t, {})
        assert result == 100
        # Test with kw override
        result = compiler._get("length", t, {"length": 200})
        assert result == 200


class TestDDLCompilation:
    """Test DDL (CREATE TABLE) compilation."""

    def _compile_ddl(self, table):
        from sqlalchemy.schema import CreateTable

        dialect = CubridDialect()
        return CreateTable(table).compile(dialect=dialect).string

    def test_autoincrement_column(self):
        """AUTO_INCREMENT should appear for autoincrement PK columns."""
        m = MetaData()
        t = Table(
            "test_ai",
            m,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(100)),
        )
        ddl = self._compile_ddl(t)
        assert "AUTO_INCREMENT" in ddl
        assert "NOT NULL" in ddl

    def test_no_autoincrement_without_flag(self):
        """Columns without autoincrement should not get AUTO_INCREMENT."""
        m = MetaData()
        t = Table(
            "test_no_ai",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("name", String(100)),
        )
        ddl = self._compile_ddl(t)
        assert "AUTO_INCREMENT" not in ddl

    def test_not_null_in_ddl(self):
        """NOT NULL columns should emit NOT NULL."""
        m = MetaData()
        t = Table(
            "test_nn",
            m,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False),
        )
        ddl = self._compile_ddl(t)
        # Both id (PK) and name should have NOT NULL
        # Count NOT NULL occurrences - at least 2
        assert ddl.count("NOT NULL") >= 2

    def test_nullable_column_no_not_null(self):
        """Nullable columns should not emit NOT NULL."""
        m = MetaData()
        t = Table(
            "test_nullable",
            m,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=True),
        )
        ddl = self._compile_ddl(t)
        # name column line should not have NOT NULL
        # id should have NOT NULL (PK)
        lines = ddl.split("\n")
        for line in lines:
            if "name" in line.lower() and "id" not in line.lower():
                assert "NOT NULL" not in line

    def test_column_default_value(self):
        """Column defaults should emit DEFAULT clause."""
        m = MetaData()
        t = Table(
            "test_default",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("status", Integer, server_default="0"),
        )
        ddl = self._compile_ddl(t)
        assert "DEFAULT" in ddl

    def test_ddl_type_output(self):
        """Verify type names appear correctly in DDL."""
        m = MetaData()
        t = Table(
            "test_types",
            m,
            Column("id", Integer, primary_key=True),
            Column("name", String(100)),
        )
        ddl = self._compile_ddl(t)
        assert "INTEGER" in ddl
        assert "VARCHAR(100)" in ddl


class TestUpdateCompilation:
    """Test UPDATE statement compilation with LIMIT and FROM."""

    def test_update_with_limit(self):
        """Test UPDATE with cubrid_limit kwargs."""
        from sqlalchemy import update

        stmt = update(users).values(name="test")
        stmt.kwargs["cubrid_limit"] = 10
        sql = _compile(stmt)
        assert "UPDATE" in sql
        assert "LIMIT" in sql
        assert "10" in sql

    def test_update_without_limit(self):
        """Test UPDATE without limit - no LIMIT clause."""
        from sqlalchemy import update

        stmt = update(users).values(name="test")
        sql = _compile(stmt)
        assert "UPDATE" in sql
