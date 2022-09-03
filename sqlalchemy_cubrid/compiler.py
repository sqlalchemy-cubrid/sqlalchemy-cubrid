# sqlalchemy_cubrid/compiler.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.sql import compiler
from sqlalchemy import exc
from sqlalchemy import types as sqltypes

# ToDo: Need to implement the function through the method below
# from sqlalchemy import exc
# from sqlalchemy import schema as sa_schema
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.sql.expression import Select
# from sqlalchemy import exc, sql
# from sqlalchemy import create_engine


class CubridCompiler(compiler.SQLCompiler):
    """CubridCompiler implementation of"""

    def __init__(
        self, dialect, statement, column_keys=None, inline=False, **kwargs
    ):
        super(CubridCompiler, self).__init__(
            dialect, statement, column_keys, inline, **kwargs
        )

    def visit_sysdate_func(self, fn, **kw):
        return "SYSDATE"

    def visit_utc_timestamp_func(self, fn, **kw):
        return "UTC_TIME()"

    def visit_cast(self, cast, **kw):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/function/typecast_fn.html#cast
        type_ = self.process(cast.typeclause)
        if type_ is None:
            return self.process(cast.clause.self_group())

        return f"CAST({self.process(cast.clause)}AS {type_})"

    def render_literal_value(self, value, type_):
        value = super(CubridCompiler, self).render_literal_value(value, type_)
        value = value.replace("\\", "\\\\")
        return value

    def get_select_precolumns(self, select, **kw):
        # TODO
        if select._distinct:
            return "DISTINCT "
        else:
            return ""

    def visit_join(self, join, asfrom=False, **kwargs):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/query/select.html#join-query
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
        return ""

    def limit_clause(self, select):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/query/select.html#limit-clause
        limit, offset = select._limit, select._offset
        if (limit, offset) == (None, None):
            return ""
        elif limit is None and offset is not None:
            return " \n LIMIT %s, 1073741823" % (
                self.process(sql.literal(offset))
            )
        elif offset is not None:
            return " \n LIMIT %s, %s" % (
                self.process(sql.literal(offset)),
                self.process(sql.literal(limit)),
            )
        else:
            return " \n LIMIT %s" % (self.process(sql.literal(limit)),)

    def update_limit_clause(self, update_stmt):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/query/update.html
        limit = update_stmt.kwargs.get(f"{self.dialect.name}_limit", None)
        if limit:
            return f"LIMIT {limit}"
        else:
            return None

    def update_tables_clause(self, update_stmt, from_table, extra_froms, **kw):

        return ", ".join(
            t._compiler_dispatch(self, asfrom=True, **kw)
            for t in [from_table] + list(extra_froms)
        )

    def update_from_clause(
        self, update_stmt, from_table, extra_froms, from_hints, **kw
    ):
        return None


class CubridDDLCompiler(compiler.DDLCompiler):
    def define_constraint_cascades(self, constraint):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/schema/table.html#foreign-key
        # ON DELETE CASCADE | RESTRICT | NO ACTION | SET NULL
        text = ""
        if constraint.ondelete:
            text += f" ON DELTE {constraint.onupdate}"
        else:
            text += " ON DELETE RESTRICT"

        if constraint.onupdate:
            text += f" ON UPDATE {constraint.onupdate}"
        else:
            text += " ON UPDATE RESTRICT"

    def get_column_specification(self, column, **kw):
        """Builds column DDL."""
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/schema/table.html?highlight=auto_increment#column-definition
        colspec = [
            self.preparer.format_column(column),
            self.dialect.type_compiler.process(column.type),
        ]
        default = self.get_column_default_string(column)
        if default is not None:
            colspec.append("DEFAULT " + default)

        is_timestamp = isinstance(column.type, sqltypes.TIMESTAMP)
        if not column.nullable and not is_timestamp:
            colspec.append("NOT NULL")
        elif column.nullable and is_timestamp and default is None:
            colspec.append("NULL")

        if (
            column is column.table._autoincrement_column
            and column.server_default is None
        ):
            colspec.append("AUTO_INCREMENT")

        return " ".join(colspec)

    def _verify_index_table(self, index):
        if index.table is None:
            raise exc.CompileError(
                "Index '%s' is not associated " "with any table." % index.name
            )

    def visit_create_index(self, create):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/schema/index.html#create-index
        index = create.element
        self._verify_index_table(index)
        preparer = self.preparer

        text = "CREATE "
        if index.unique:
            text += "UNIQUE "
        if index.name is None:
            raise exc.CompileError(
                "CREATE INDEX requires that the index have a name"
            )
        text += f"{self._prepared_index_name(index, include_schema=False)} ON {preparer.format_table(index.table)} "

        # TODO: index_col_desc
        return text

    def visit_drop_index(self, drop):
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/schema/index.html#drop-index
        index = drop.element

        text = "\nDROP"
        if index.unique:
            text += "UNIQUE "
        text += (
            f"INDEX {self._prepared_index_name(index, include_schema=False)} "
        )

        if index.table is not None:
            text += f"ON {self.preparer.format_table(index.table)}"


class CubridTypeCompiler(compiler.GenericTypeCompiler):
    def _get(self, key, type_, kw):
        return kw.get(key, getattr(type_, key, None))

    def visit_BOOLEAN(self, type_, **kw):
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
            return f"CHAR({type_.length}"
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
        return self.visit_list(type_, "SET")

    def visit_MULTISET(self, type_, **kw):
        return self.visit_list(type_, "MULTISET")

    def visit_SEQUENCE(self, type_, **kw):
        return self.visit_list(type_, "SEQUENCE")

    def visit_list(self, type_, list_type, **kw):
        """CUBRID support Collection Types (SET, MULTISET, LIST or SEQUENCE)
        see: https://www.cubrid.org/manual/en/9.3.0/sql/datatype.html#collection-types
        """
        first = True
        compiled = list_type + "("
        for value in type_._ddl_values:
            if not first:
                compiled += ","
            if isinstance(value, basestring):
                compiled += value
            else:
                compiled += value.__visit_name__
            first = False
        compiled += ")"
        return compiled
