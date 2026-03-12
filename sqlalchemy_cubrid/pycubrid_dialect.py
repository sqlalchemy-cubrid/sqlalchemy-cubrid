# sqlalchemy_cubrid/pycubrid_dialect.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""CUBRID dialect variant using the pycubrid pure-Python DB-API 2.0 driver."""

from __future__ import annotations


from sqlalchemy_cubrid.base import CubridExecutionContext
from sqlalchemy_cubrid.dialect import CubridDialect


class PyCubridExecutionContext(CubridExecutionContext):
    """Execution context for pycubrid connections.

    pycubrid exposes ``cursor.lastrowid`` as a proper ``int | None``,
    so we use it directly instead of the CUBRIDdb workaround.
    """

    def get_lastrowid(self):
        """Return the last inserted row ID from pycubrid's cursor."""
        try:
            return self.cursor.lastrowid
        except AttributeError:
            pass

        # Fallback: use SQL function
        cursor = self.create_server_side_cursor()
        try:
            cursor.execute("SELECT LAST_INSERT_ID()")
            row = cursor.fetchone()
            if row:
                return int(row[0])
        finally:
            cursor.close()
        return None


class PyCubridDialect(CubridDialect):
    """SQLAlchemy dialect for CUBRID using the pycubrid pure-Python driver.

    Connection URL: ``cubrid+pycubrid://user:password@host:port/dbname``

    This dialect subclasses :class:`CubridDialect` and overrides only
    the driver-specific methods: ``import_dbapi``, ``create_connect_args``,
    ``on_connect``, and ``do_ping``.  All SQL compilation, type mapping,
    and schema reflection is inherited unchanged.
    """

    driver = "pycubrid"
    supports_statement_cache = True
    execution_ctx_cls = PyCubridExecutionContext

    # pycubrid uses qmark paramstyle natively
    default_paramstyle = "qmark"

    @classmethod
    def import_dbapi(cls):
        """Import and return the pycubrid DBAPI module."""
        try:
            import pycubrid as dbapi_module
        except ImportError as e:
            raise e
        return dbapi_module

    # Keep legacy dbapi() for SA 1.x compat
    @classmethod
    def dbapi(cls):
        return cls.import_dbapi()

    def create_connect_args(self, url):
        """Build DB-API connection arguments for pycubrid.

        pycubrid accepts keyword arguments directly::

            pycubrid.connect(host=..., port=..., database=..., user=..., password=...)
        """
        if url is None:
            raise ValueError("Unexpected database URL format")

        opts = url.translate_connect_args(username="user", database="database")
        return (), {
            "host": opts.get("host", "localhost"),
            "port": opts.get("port", 33000),
            "database": opts.get("database", ""),
            "user": opts.get("user", "dba"),
            "password": opts.get("password", ""),
        }

    def on_connect(self):
        """Return a callable to set up a new pycubrid connection.

        Disables autocommit so that SQLAlchemy manages transactions.
        """
        isolation_level = self.isolation_level

        def connect(conn):
            # pycubrid uses a property setter for autocommit
            conn.autocommit = False
            if isolation_level is not None:
                self.set_isolation_level(conn, isolation_level)

        return connect

    def do_ping(self, dbapi_connection):
        """Ping the server to check connection liveness.

        pycubrid does not expose a native ``ping()`` method, so we
        execute a lightweight query instead.
        """
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            cursor.close()
        return True


dialect = PyCubridDialect
