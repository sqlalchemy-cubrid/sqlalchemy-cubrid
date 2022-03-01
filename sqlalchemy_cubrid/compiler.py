# sqlalchemy_cubrid/compiler.py
# Copyright (C) 2021-2022 by Curbrid
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.sql import compiler
from sqlalchemy import exc
from sqlalchemy import schema as sa_schema
from sqlalchemy.types import Unicode
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Select
from sqlalchemy import exc, sql
from sqlalchemy import create_engine


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

    def visit_BOOLEAN(self, type_):
        return self.visit_SMALLINT(type_)
