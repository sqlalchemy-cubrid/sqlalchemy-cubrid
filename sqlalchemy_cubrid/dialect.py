# sqlalchemy_cubrid/dialect.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
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

    # https://www.cubrid.org/manual/en/9.3.0/sql/identifier.html
    max_identifier_length = 254
    max_index_name_length = 254
    max_constraint_name_length = 254

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

        if url is None:
            raise ValueError(f"Unexpected database format")

        params = super(CubridDialect, self).create_connect_args(url)[1]
        url = (
            f'CUBRID:{params["host"]}:{params["port"]}:{params["database"]}:::'
        )
        args = (url, params["username"], params["password"])
        kwargs = {}
        return args, kwargs

    def initialize(self, connection):
        default.DefaultDialect.initialize(self, connection)

    def get_columns(self, connection, table_name, schema=None, **kw):
        """
        Return information about columns in `table_name`.

        :param connection:
        :param table_name:
        :param schema:
        :rtype: list[str]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_columns`.
        """
        columns = []
        return columns

    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        """
        Return information about the primary key constraint on table_name`

        :param connection:
        :param table_name:
        :param schema:
        :rtype: dict[str, list[str]]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_pk_constraint`.
        """
        pk_constraint = {}
        return pk_constraint

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        """
        Return information about the primary key constraint on table_name`

        :param connection:
        :param table_name:
        :param schema:
        :rtype: list[]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_foreign_keys`.
        """
        foreign_keys = []
        return foreign_keys

    def get_table_names(self, connection, schema=None, **kw):
        """
        Return a list of table names for `schema`.

        :param connection:
        :param schema:
        :rtype: list[str]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_table_names`.
        """
        table_names = []
        return table_names

    def get_view_names(self, connection, schema=None, **kw):
        """Return a list of all view names available in the database.

        :param connection:
        :param schema: schema name to query, if not the default schema.
        :rtype: list[str]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_view_names`.
        """
        view_names = []
        return view_names

    def get_view_definition(self, connection, view_name, schema=None, **kw):
        """Return view definition.

        :param connection:
        :param view_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: str

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_view_definition`.
        """
        view_definition = ""
        return view_definition

    def get_indexes(self, connection, table_name, schema=None, **kw):
        """Return information about indexes in `table_name`.

        :param connection:
        :param view_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: list[]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_indexes`.
        """
        indexes = []
        return indexes

    def get_unique_constraints(
        self, connection, table_name, schema=None, **kw
    ):
        """Return information about unique constraints in `table_name`.

        :param connection:
        :param view_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: list[]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_unique_constraints`.
        """
        unique_constraints = []
        return unique_constraints

    def has_table(self, connection, table_name, schema=None, **kw):
        """Return information about unique constraints in `table_name`.

        :param connection:
        :param view_name:
        :param schema: schema name to query, if not the default schema.

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.has_table`.
        """
        return None

    def has_index(self, connection, table_name, index_name, schema=None):
        """
        Check the existence of a particular index name in the database.

        :param connection:
        :param view_name:
        :param schema: schema name to query, if not the default schema.

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.has_index`.
        """
        return None

    def on_connect(self):
        """
        Return a callable which sets up a newly created DBAPI connection.

        see: https://docs.sqlalchemy.org/en/14/core/internals.html?highlight=on_connect#sqlalchemy.engine.default.DefaultDialect.on_connect

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.on_connect`.
        """
        return None

    def reset_isolation_level(self, dbapi_conn):
        """
        Given a DBAPI connection, revert its isolation to the default.

        :param dbapi_conn:

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.reset_isolation_level`.
        """
        return None

    def set_isolation_level(self, dbapi_conn, level):
        """Given a DBAPI connection, set its isolation level.

        :param dbapi_conn:
        :param level:

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.set_isolation_level`.
        """
        return None

    def get_isolation_level(self, dbapi_conn):
        """Given a DBAPI connection, return its isolation level.

        :param dbapi_conn:

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_isolation_level`.
        """
        return None


dialect = CubridDialect
