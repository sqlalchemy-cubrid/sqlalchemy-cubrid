# sqlalchemy_cubrid/compiler.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""CUBRID SQL, DDL, and type compilers for SQLAlchemy 2.0."""

from __future__ import annotations

from sqlalchemy.sql import compiler


class CubridCompiler(compiler.SQLCompiler):
    """SQLCompiler subclass for CUBRID."""

    def visit_sysdate_func(self, fn, **kw):
        return "SYSDATE"

    def visit_utc_timestamp_func(self, fn, **kw):
        return "UTC_TIME()"

    def visit_cast(self, cast, **kw):
        # https://www.cubrid.org/manual/en/11.0/sql/function/typecast_fn.html#cast
        type_ = self.process(cast.typeclause)
        if type_ is None:
            return self.process(cast.clause.self_group())
        return f"CAST({self.process(cast.clause)} AS {type_})"

    def render_literal_value(self, value, type_):
        value = super().render_literal_value(value, type_)
        value = value.replace("\\", "\\\\")
        return value

    def get_select_precolumns(self, select, **kw):
        if bool(select._distinct):
            return "DISTINCT "
        return ""

    def visit_join(self, join, asfrom=False, **kwargs):
        # https://www.cubrid.org/manual/en/11.0/sql/query/select.html#join-query
        return "".join(
            (
                self.process(join.left, asfrom=True, **kwargs),
                (join.isouter and " LEFT OUTER JOIN " or " INNER JOIN "),
                self.process(join.right, asfrom=True, **kwargs),
                " ON ",
                self.process(join.onclause, **kwargs),
            )
        )

    def for_update_clause(self, select, **kw):
        """Render FOR UPDATE clause.

        CUBRID supports::

            SELECT ... FOR UPDATE
            SELECT ... FOR UPDATE OF col1, col2

        CUBRID does NOT support NOWAIT or SKIP LOCKED.
        """
        if select._for_update_arg is None:
            return ""
        text = " FOR UPDATE"
        if select._for_update_arg.of:
            text += " OF " + ", ".join(
                self.process(col, **kw) for col in select._for_update_arg.of
            )
        return text

    def limit_clause(self, select, **kw):
        # https://www.cubrid.org/manual/en/11.0/sql/query/select.html#limit-clause
        # SA 2.0: _limit_clause / _offset_clause are ClauseElements, not raw ints.
        limit_clause = select._limit_clause
        offset_clause = select._offset_clause
        if limit_clause is None and offset_clause is None:
            return ""
        elif limit_clause is None and offset_clause is not None:
            return " \n LIMIT %s, 1073741823" % (self.process(offset_clause, **kw),)
        elif offset_clause is not None:
            return " \n LIMIT %s, %s" % (
                self.process(offset_clause, **kw),
                self.process(limit_clause, **kw),
            )
        else:
            return " \n LIMIT %s" % (self.process(limit_clause, **kw),)

    def update_limit_clause(self, update_stmt):
        # https://www.cubrid.org/manual/en/11.0/sql/query/update.html
        limit = update_stmt.kwargs.get(f"{self.dialect.name}_limit", None)
        if limit:
            return f"LIMIT {limit}"
        return None

    def update_tables_clause(self, update_stmt, from_table, extra_froms, **kw):
        return ", ".join(
            t._compiler_dispatch(self, asfrom=True, **kw) for t in [from_table] + list(extra_froms)
        )

    def update_from_clause(self, update_stmt, from_table, extra_froms, from_hints, **kw):
        return None


class CubridDDLCompiler(compiler.DDLCompiler):
    """DDLCompiler subclass for CUBRID.

    Handles AUTO_INCREMENT for autoincrement columns and column defaults.
    """

    def get_column_specification(self, column, **kw):
        """Build column DDL specification.

        CUBRID syntax::

            column_name TYPE [NOT NULL] [AUTO_INCREMENT] [DEFAULT value]
        """
        colspec = [
            self.preparer.format_column(column),
            self.dialect.type_compiler_instance.process(column.type, type_expression=column),
        ]

        if not column.nullable:
            colspec.append("NOT NULL")

        if (
            column.table is not None
            and column is column.table._autoincrement_column
            and (column.server_default is None)
        ):
            colspec.append("AUTO_INCREMENT")
        else:
            default = self.get_column_default_string(column)
            if default is not None:
                colspec.append("DEFAULT " + default)

        return " ".join(colspec)


class CubridTypeCompiler(compiler.GenericTypeCompiler):
    """TypeCompiler for CUBRID data types."""

    def _get(self, key, type_, kw):
        return kw.get(key, getattr(type_, key, None))

    def visit_BOOLEAN(self, type_, **kw):
        # CUBRID has no native BOOLEAN; map to SMALLINT.
        return self.visit_SMALLINT(type_)

    def visit_NUMERIC(self, type_, **kw):
        if type_.precision is None:
            return "NUMERIC"
        elif type_.scale is None:
            return f"NUMERIC({type_.precision})"
        else:
            return f"NUMERIC({type_.precision}, {type_.scale})"

    def visit_DECIMAL(self, type_, **kw):
        if type_.precision is None:
            return "DECIMAL"
        elif type_.scale is None:
            return f"DECIMAL({type_.precision})"
        else:
            return f"DECIMAL({type_.precision}, {type_.scale})"

    def visit_FLOAT(self, type_, **kw):
        if type_.precision is None:
            return "FLOAT"
        else:
            return f"FLOAT({type_.precision})"

    def visit_DOUBLE(self, type_, **kw):
        return "DOUBLE"

    def visit_MONETARY(self, type_, **kw):
        return "MONETARY"

    def visit_SMALLINT(self, type_, **kw):
        return "SMALLINT"

    def visit_BIGINT(self, type_, **kw):
        return "BIGINT"

    def visit_BIT(self, type_, **kw):
        if type_.varying:
            compiled = "BIT VARYING"
            if type_.length is not None:
                compiled += f"({type_.length})"
        else:
            compiled = f"BIT({type_.length})"
        return compiled

    def visit_datetime(self, type_, **kw):
        return "DATETIME"

    def visit_DATETIME(self, type_, **kw):
        return "DATETIME"

    def visit_DATE(self, type_, **kw):
        return "DATE"

    def visit_TIME(self, type_, **kw):
        return "TIME"

    def visit_TIMESTAMP(self, type_, **kw):
        return "TIMESTAMP"

    def visit_VARCHAR(self, type_, **kw):
        if hasattr(type_, "national") and type_.national:
            return self.visit_NVARCHAR(type_)
        elif type_.length:
            return "VARCHAR(%d)" % type_.length
        else:
            return "VARCHAR(4096)"

    def visit_CHAR(self, type_, **kw):
        if hasattr(type_, "national") and type_.national:
            return self.visit_NCHAR(type_)
        elif type_.length:
            return f"CHAR({type_.length})"
        else:
            return "CHAR"

    def visit_NVARCHAR(self, type_, **kw):
        if type_.length:
            return f"NCHAR VARYING({type_.length})"
        else:
            return "NCHAR VARYING(4096)"

    def visit_NCHAR(self, type_, **kw):
        if type_.length:
            return f"NCHAR({type_.length})"
        else:
            return "NCHAR"

    def visit_OBJECT(self, type_, **kw):
        return "OBJECT"

    def visit_large_binary(self, type_, **kw):
        return self.visit_BLOB(type_)

    def visit_text(self, type_, **kw):
        return self.visit_STRING(type_)

    def visit_BLOB(self, type_, **kw):
        return "BLOB"

    def visit_CLOB(self, type_, **kw):
        return "CLOB"

    def visit_STRING(self, type_, **kw):
        return "STRING"

    def visit_SET(self, type_, **kw):
        return self._visit_collection(type_, "SET")

    def visit_MULTISET(self, type_, **kw):
        return self._visit_collection(type_, "MULTISET")

    def visit_SEQUENCE(self, type_, **kw):
        return self._visit_collection(type_, "SEQUENCE")

    def _visit_collection(self, type_, collection_type, **kw):
        """Compile CUBRID collection types (SET, MULTISET, LIST/SEQUENCE).

        See: https://www.cubrid.org/manual/en/11.0/sql/datatype.html#collection-types
        """
        parts = []
        for value in type_._ddl_values:
            if isinstance(value, str):
                parts.append(value)
            else:
                parts.append(value.__visit_name__)
        return f"{collection_type}({','.join(parts)})"
