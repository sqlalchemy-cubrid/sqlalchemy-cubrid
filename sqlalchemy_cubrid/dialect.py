# sqlalchemy_cubrid/dialect.py
# Copyright (C) 2021-2022 by Curbrid
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.engine import default
from sqlalchemy_cubrid.base import CubridExecutionContext
from sqlalchemy_cubrid.base import CubridIdentifierPreparer
from sqlalchemy_cubrid.compiler import CubridCompiler
from sqlalchemy_cubrid.compiler import CubridDDLCompiler
from sqlalchemy_cubrid.compiler import CubridTypeCompiler


class CubridDialect(default.DefaultDialect):
    name = "cubrid"
    driver = "CUBRID-Python"

    statement_compiler = CubridCompiler
    ddl_compiler = CubridDDLCompiler
    type_compiler = CubridTypeCompiler

    preparer = CubridIdentifierPreparer
    execution_ctx_cls = CubridExecutionContext

    def __init__(self, **kwargs):
        super(CubridDialect, self).__init__(**kwargs)

    @classmethod
    def dbapi(cls):
        """Hook to the dbapi2.0 implementation's module"""
        try:
            import CUBRIDdb as cubrid_dbapi
        except ImportError as e:
            raise e
        return cubrid_dbapi

    def create_connect_args(self, url):
        """
        Build DB-API compatible connection arguments.
        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.create_connect_args`.
        """

        # Connection to CUBRID database is made through connect() method.
        # Syntax:
        # connect (url, user, password])
        #    url - CUBRID:host:port:db_name:db_user:db_password:::
        #    user - Authorized username.
        #    password - Password associated with the username.

        if url is not None:
            params = super(CubridDialect, self).create_connect_args(url)[1]
            print(params)

            args = ("CUBRID:localhost:33000:testdb:::", "dba", "1234")
            kwargs = {}
            return args, kwargs


dialect = CubridDialect
