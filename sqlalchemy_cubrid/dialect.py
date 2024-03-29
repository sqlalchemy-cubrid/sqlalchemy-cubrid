# sqlalchemy_cubrid/dialect.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from cmd import IDENTCHARS
import re
from sqlalchemy.sql import text
from sqlalchemy.sql import util
from sqlalchemy.engine import reflection
from sqlalchemy.engine import default
from sqlalchemy_cubrid.base import CubridExecutionContext
from sqlalchemy_cubrid.base import CubridIdentifierPreparer
from sqlalchemy_cubrid.compiler import CubridCompiler
from sqlalchemy_cubrid.compiler import CubridDDLCompiler
from sqlalchemy_cubrid.compiler import CubridTypeCompiler

from sqlalchemy import types as sqltypes
from sqlalchemy_cubrid.types import SMALLINT
from sqlalchemy.types import INTEGER
from sqlalchemy_cubrid.types import BIGINT
from sqlalchemy_cubrid.types import NUMERIC
from sqlalchemy_cubrid.types import DECIMAL
from sqlalchemy_cubrid.types import FLOAT
from sqlalchemy_cubrid.types import DOUBLE
from sqlalchemy_cubrid.types import DOUBLE_PRECISION
from sqlalchemy.types import DATE
from sqlalchemy.types import DATETIME
from sqlalchemy.types import TIME
from sqlalchemy.types import TIMESTAMP
from sqlalchemy_cubrid.types import BIT
from sqlalchemy_cubrid.types import CHAR
from sqlalchemy_cubrid.types import VARCHAR
from sqlalchemy_cubrid.types import NCHAR
from sqlalchemy_cubrid.types import NVARCHAR
from sqlalchemy_cubrid.types import STRING
from sqlalchemy_cubrid.types import BLOB
from sqlalchemy_cubrid.types import CLOB
from sqlalchemy_cubrid.types import SET
from sqlalchemy_cubrid.types import MULTISET
from sqlalchemy_cubrid.types import SEQUENCE


colspecs = {
    sqltypes.Numeric: NUMERIC,
    sqltypes.Float: FLOAT,
    sqltypes.Time: TIME,
}

# ischema names is used for reflecting columns (get_columns)
# see: https://www.cubrid.org/manual/en/9.3.0/sql/datatype.html
ischema_names = {
    # Numeric Types
    "SHORT": SMALLINT,
    "SMALLINT": SMALLINT,
    "INTEGER": INTEGER,
    "BIGINT": BIGINT,
    "NUMERIC": NUMERIC,
    "DECIMAL": DECIMAL,
    "FLOAT": FLOAT,
    # REAL
    "DOUBLE": DOUBLE,
    "DOUBLE PRECISION": DOUBLE_PRECISION,
    # Date/Time Types
    "DATE": DATE,
    "TIME": TIME,
    "TIMESTAMP": TIMESTAMP,
    "DATETIME": DATETIME,
    # Bit Strings
    "BIT": BIT,  # BIT(n)
    "BIT VARYING": BIT,  # BIT VARYING(n)
    # Character Strings
    "CHAR": CHAR,  # CHAR(n)
    "VARCHAR": VARCHAR,  # VARCHAR(n)
    "NCHAR": NCHAR,
    "CHAR VARYING": NVARCHAR,
    "STRING": STRING,
    # BLOB/CLOB Data Types
    "BLOB": BLOB,
    "CLOB": CLOB,
    # Collection Types
    "SET": SET,
    "MULTISET": MULTISET,
    "SEQUENCE": SEQUENCE,
    "SEQUENCE": SEQUENCE,
}


class CubridDialect(default.DefaultDialect):
    name = "cubrid"
    driver = "CUBRID-Python"

    statement_compiler = CubridCompiler
    ddl_compiler = CubridDDLCompiler
    type_compiler = CubridTypeCompiler
    preparer = CubridIdentifierPreparer
    execution_ctx_cls = CubridExecutionContext

    # see: https://www.cubrid.org/manual/en/9.3.0/api/python.html
    default_paramstyle = "qmark"

    colspecs = colspecs
    ischema_names = ischema_names

    # see: https://www.cubrid.org/manual/en/9.3.0/sql/identifier.html
    max_identifier_length = 254
    max_index_name_length = 254
    max_constraint_name_length = 254

    def __init__(self, isolation_level=None, **kwargs):
        super(CubridDialect, self).__init__(**kwargs)
        self.isolation_level = isolation_level

    # Data Type
    supports_native_enum = False
    supports_native_boolean = True
    supports_native_decimal = True

    # Column options
    supports_sequences = False

    # DDL
    supports_alter = True

    # DML
    supports_default_values = False
    """dialect supports INSERT... DEFAULT VALUES syntax"""

    supports_default_metavalue = False
    """dialect supports INSERT... VALUES (DEFAULT) syntax"""

    supports_empty_insert = False
    """dialect supports INSERT () VALUES ()"""

    supports_multivalues_insert = True
    postfetch_lastrowid = False

    requires_name_normalize = True

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

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        """
        Return information about columns in `table_name`.

        :param connection: DBAPI connection
        :param table_name: table name to query
        :param schema: schema name to query, if not the default schema.
        :rtype: list[dict]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_columns`.
        """
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/query/show.html#show-columns
        columns = []

        result = connection.execute(text(f"SHOW COLUMNS IN {table_name}"))
        for row in result:
            colname = row[0]
            coltype_ = row[1]
            nullable = not row[2] == "YES"
            default = row[4]
            autoincrement = "auto_increment" in row[5]

            # TODO: Need to check other types.
            if coltype_ in ("CHAR", "VARCHAR", "VARCHAR", "CHAR VARYING"):
                coltype = re.sub(r"\(\d+\)", "", coltype_)
                length = int(re.search("\(([\d,]+)\)", coltype_).group(1))
                coltype = self.ischema_names.get(coltype)(length)
            else:
                coltype = re.sub(r"\(\d+\)", "", coltype_)
                try:
                    coltype = self.ischema_names[coltype]
                except KeyError:
                    util.warn(
                        "Did not recognize type '%s' of column '%s'"
                        % (coltype, colname)
                    )
                    coltype = sqltypes.NULLTYPE

            cdit = {
                "name": colname,
                "type": coltype,
                "nullable": nullable,
                "default": default,
                "autoincrement": autoincrement,
            }
            columns.append(cdit)
        return columns

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        """
        Return information about the primary key constraint on table_name`

        :param connection: DBAPI connection
        :param table_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: dict[str, list[str]]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_pk_constraint`.
        """
        pk_constraint = {}
        result = connection.execute("SHOW COLUMNS IN '{table_name}'")
        constraint_name = None
        constrained_columns = []
        for row in result:
            if row[3] == "PRI":
                constrained_columns.append(row[0])
                # TODO: get constraint_name
        pk_constraint["name"] = constraint_name
        pk_constraint["constrained_columns"] = constrained_columns
        return pk_constraint

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        """
        Return information about the primary key constraint on table_name`

        :param connection: DBAPI connection
        :param table_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: list[dict]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_foreign_keys`.
        """
        foreign_keys = []

        return foreign_keys

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        """
        Return a list of table names for `schema`.

        :param connection: DBAPI connection
        :param schema: schema name to query, if not the default schema.
        :rtype: list[str]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_table_names`.
        """
        table_names = []
        if schema is None:
            result = connection.execute(
                text(
                    "SELECT * FROM db_class WHERE class_type = 'CLASS' AND is_system_class='NO'"
                )
            )
            table_names = [row[0] for row in result]

        return table_names

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        """Return a list of all view names available in the database.

        :param connection: DBAPI connection
        :param schema: schema name to query, if not the default schema.
        :rtype: list[str]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_view_names`.
        """
        view_names = []
        result = connection.execute(
            text("SELECT * FROM db_class WHERE class_type = 'VCLASS'")
        )
        view_names = [row[0] for row in result]
        return view_names

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        """Return view definition.

        :param connection: DBAPI connection
        :param view_name: view_name name to query
        :param schema: schema name to query, if not the default schema.
        :rtype: str

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_view_definition`.
        """
        view_definition = ""
        result = connection.execute(text(f"SHOW CREATE VIEW {view_name}"))
        view_definition = result.fetchone()[1]
        return view_definition

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        """Return information about indexes in `table_name`.

        :param connection: DBAPI connection
        :param table_name: table name to query
        :param schema: schema name to query, if not the default schema.
        :rtype: list[dict]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_indexes`.
        """
        # https://www.cubrid.org/manual/en/9.3.0/sql/query/show.html#show-index
        indexes = []
        idict = {}
        result = connection.execute(text(f"SHOW INDEXES IN {table_name}"))
        for row in result:
            name = row[2]
            result = connection.execute(
                text(f"SELECT * from _db_index WHERE index_name = '{name}'")
            )
            is_primary_key = result.fetchone()[6]

            if not is_primary_key:
                if name in idict:
                    idict[name]["column_name"].append(row[4])
                else:
                    idict[name] = {
                        "column_name": [row[4]],
                        "unique": row[1] == 0,
                        "type": row[10],
                    }

        for key, value in idict.items():
            value["name"] = key
            indexes.append(value)

        return indexes

    def get_unique_constraints(
        self, connection, table_name, schema=None, **kw
    ):
        """Return information about unique constraints in `table_name`.

        :param connection: DBAPI connection
        :param view_name:
        :param schema: schema name to query, if not the default schema.
        :rtype: list[]

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_unique_constraints`.
        """
        unique_constraints = []
        return unique_constraints

    def has_table(self, connection, table_name, schema=None, **kw):
        """Check the existence of a particular table in the database.

        :param connection: DBAPI connection
        :param table_name: table name to query
        :param schema: schema name to query, if not the default schema.
        :rtype: bool

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.has_table`.
        """
        have = False

        result = connection.execute(
            text(
                f"SELECT * FROM db_class WHERE class_type = 'CLASS' AND is_system_class='NO' AND class_name='{table_name}'"
            )
        )
        have = result.fetchone() is not None
        return have

    def has_index(self, connection, table_name, index_name, schema=None):
        """
        Check the existence of a particular index name in the database.

        :param connection: DBAPI connection
        :param view_name:
        :param schema: schema name to query, if not the default schema.

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.has_index`.
        """
        return None

    def on_connect(self):
        """
        Return a callable which sets up a newly created DBAPI connection.

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.on_connect`.
        """
        # see: https://docs.sqlalchemy.org/en/14/core/internals.html?highlight=on_connect#sqlalchemy.engine.default.DefaultDialect.on_connect
        if self.isolation_level is not None:

            def connect(conn):
                self.set_isolation_level(conn, self.isolation_level)

            return connect
        else:
            return None

    def _get_server_version_info(self, connection):
        """Retrieve the server version info from the given connection.

        Returns a tuple of (`major`, `minor`, `build`, 'patch version'), four integers
        representing the version of the attached server.
        """
        versions = connection.execute(text("SELECT VERSION()")).scalar()
        m = re.match(r"(\d+).(\d+).(\d+).(\d+)", versions)
        if m:
            return tuple(int(x) for x in m.group(1, 2, 3, 4))
        else:
            return None

    def _get_default_schema_name(self, connection):
        """Return the string name of the currently selected schema from
        the given connection.
        """
        return connection.execute(text("SELECT SCHEMA()")).scalar()

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
        if hasattr(dbapi_conn, "connection"):
            dbapi_conn = dbapi_conn.connection

        cursor = dbapi_conn.cursor()
        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
        cursor.execute("COMMIT")
        cursor.close()

    def get_isolation_level_spec(self, dbapi_conn):
        return (
            "SERIALIZABLE",  # 6
            "REPEATABLE READ SCHEMA, REPETABLE READ INSTANCES",  # 5
            "REPEATABLE READ SCHEMA, READ COMMITTED INSTANCES",  # 4
            "CURSOR STABILITY",  # 4
            "REPEATABLE READ SCHEMA, READ UNCOMMITTED INSTANCES",  # 3
            "READ COMMITTED SCHEMA, READ COMMITTED INSTANCES",  # 2
            "READ COMMITTED SCHEMA, READ UNCOMMITTED INSTANCES",  # 1
        )

    def get_isolation_level(self, dbapi_conn):
        """Given a DBAPI connection, return its isolation level.

        :param dbapi_conn:

        Overrides interface
        :meth:`~sqlalchemy.engine.interfaces.Dialect.get_isolation_level`.
        """
        # see: https://www.cubrid.org/manual/en/9.3.0/sql/transaction.html?highlight=isolation%20level#transaction-isolation-level

        cursor = dbapi_conn.cursor()
        cursor.execute("GET TRANSACTION ISOLATION LEVEL TO X")
        cursor.execute("SELECT X")
        val = cursor.fetchone()[0]
        cursor.close()
        return val


dialect = CubridDialect
