# sqlalchemy_cubrid/compiler.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.sql import compiler

# ToDo: Need to implement the function through the method below
# from sqlalchemy import exc
# from sqlalchemy import schema as sa_schema
# from sqlalchemy.types import Unicode
# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.sql.expression import Select
# from sqlalchemy import exc, sql
# from sqlalchemy import create_engine


class CubridCompiler(compiler.SQLCompiler):
    def __init__(
        self, dialect, statement, column_keys=None, inline=False, **kwargs
    ):
        super(CubridCompiler, self).__init__(
            dialect, statement, column_keys, inline, **kwargs
        )


class CubridDDLCompiler(compiler.DDLCompiler):
    pass


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
