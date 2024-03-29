# sqlalchemy_cubrid/base.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import re

from sqlalchemy.engine import default
from sqlalchemy.sql import compiler


AUTOCOMMIT_REGEXP = re.compile(
    r"\s*(?:UPDATE|INSERT|CREATE|DELETE|DROP|ALTER|MERGE)", re.I | re.UNICODE
)

# CUBRID Reserved words: https://www.cubrid.org/manual/en/9.3.0/sql/keyword.html
RESERVED_WORDS = set(
    [
        "absolute",
        "action",
        "add",
        "add_months",
        "after",
        "all",
        "allocate",
        "alter",
        "and",
        "any",
        "are",
        "as",
        "asc",
        "assertion",
        "at",
        "attach",
        "attribute",
        "avg",
        "before",
        "between",
        "bigint",
        "bit",
        "bit_length",
        "blob",
        "boolean",
        "both",
        "breadth",
        "by",
        "call",
        "cascade",
        "cascaded",
        "case",
        "cast",
        "catalog",
        "change",
        "char",
        "character",
        "check",
        "class",
        "classes",
        "clob",
        "close",
        "coalesce",
        "collate",
        "collation",
        "column",
        "commit",
        "connect",
        "connect_by_iscycle",
        "connect_by_isleaf",
        "connect_by_root",
        "connection",
        "constraint",
        "constraints",
        "continue",
        "convert",
        "corresponding",
        "count",
        "create",
        "cross",
        "current",
        "current_date",
        "current_datetime",
        "current_time",
        "current_timestamp",
        "current_user",
        "cursor",
        "cycle",
        "data",
        "data_type",
        "database",
        "date",
        "datetime",
        "day",
        "day_hour",
        "day_millisecond",
        "day_minute",
        "day_second",
        "deallocate",
        "dec",
        "decimal",
        "declare",
        "default",
        "deferrable",
        "deferred",
        "delete",
        "depth",
        "desc",
        "describe",
        "descriptor",
        "diagnostics",
        "difference",
        "disconnect",
        "distinct",
        "distinctrow",
        "div",
        "do",
        "domain",
        "double",
        "duplicate",
        "drop",
        "each",
        "else",
        "elseif",
        "end",
        "equals",
        "escape",
        "evaluate",
        "except",
        "exception",
        "exec",
        "execute",
        "exists",
        "external",
        "extract",
        "false",
        "fetch",
        "file",
        "first",
        "float",
        "for",
        "foreign",
        "found",
        "from",
        "full",
        "function",
        "general",
        "get",
        "global",
        "go",
        "goto",
        "grant",
        "group",
        "having",
        "hour",
        "hour_millisecond",
        "hour_minute",
        "hour_second",
        "identity",
        "if",
        "ignore",
        "immediate",
        "in",
        "index",
        "indicator",
        "inherit",
        "initially",
        "inner",
        "inout",
        "input",
        "insert",
        "int",
        "integer",
        "intersect",
        "intersection",
        "interval",
        "into",
        "is",
        "isolation",
        "join",
        "key",
        "language",
        "last",
        "leading",
        "leave",
        "left",
        "less",
        "level",
        "like",
        "limit",
        "list",
        "local",
        "local_transaction_id",
        "localtime",
        "localtimestamp",
        "loop",
        "lower",
        "match",
        "max",
        "method",
        "millisecond",
        "min",
        "minute",
        "minute_millisecond",
        "minute_second",
        "mod",
        "modify",
        "module",
        "month",
        "multiset",
        "multiset_of",
        "na",
        "names",
        "national",
        "natural",
        "nchar",
        "next",
        "no",
        "none",
        "not",
        "null",
        "nullif",
        "numeric",
        "object",
        "octet_length",
        "of",
        "off",
        "on",
        "only",
        "open",
        "optimization",
        "option",
        "or",
        "order",
        "out",
        "outer",
        "output",
        "overlaps",
        "parameters",
        "partial",
        "position",
        "precision",
        "prepare",
        "preserve",
        "primary",
        "prior",
        "privileges",
        "procedure",
        "query",
        "read",
        "real",
        "recursive",
        "ref",
        "references",
        "referencing",
        "relative",
        "rename",
        "replace",
        "resignal",
        "restrict",
        "return",
        "returns",
        "revoke",
        "right",
        "role",
        "rollback",
        "rollup",
        "routine",
        "row",
        "rownum",
        "rows",
        "savepoint",
        "schema",
        "scope",
        "scroll",
        "search",
        "second",
        "second_millisecond",
        "section",
        "select",
        "sensitive",
        "sequence",
        "sequence_of",
        "serializable",
        "session",
        "session_user",
        "set",
        "set_of",
        "seteq",
        "shared",
        "siblings",
        "signal",
        "similar",
        "size",
        "smallint",
        "some",
        "sql",
        "sqlcode",
        "sqlerror",
        "sqlexception",
        "sqlstate",
        "sqlwarning",
        "statistics",
        "string",
        "subclass",
        "subset",
        "subseteq",
        "substring",
        "sum",
        "superclass",
        "superset",
        "superseteq",
        "sys_connect_by_path",
        "sys_date",
        "sys_datetime",
        "sys_time",
        "sys_timestamp",
        "sysdate",
        "sysdatetime",
        "system_user",
        "systime",
        "table",
        "temporary",
        "then",
        "time",
        "timestamp",
        "timezone_hour",
        "timezone_minute",
        "to",
        "trailing",
        "transaction",
        "translate",
        "translation",
        "trigger",
        "trim",
        "true",
        "truncate",
        "under",
        "union",
        "unique",
        "unknown",
        "update",
        "upper",
        "usage",
        "use",
        "user",
        "using",
        "utime",
        "value",
        "values",
        "varchar",
        "variable",
        "varying",
        "vclass",
        "view",
        "when",
        "whenever",
        "where",
        "while",
        "with",
        "without",
        "work",
        "write",
        "xor",
        "year",
        "year_month",
        "zone",
    ]
)


class CubridIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = RESERVED_WORDS

    def __init__(
        self,
        dialect,
        initial_quote='"',
        final_quote=None,
        escape_quote='"',
        omit_schema=False,
    ):

        super(CubridIdentifierPreparer, self).__init__(
            dialect, initial_quote, final_quote, escape_quote, omit_schema
        )

    def _quote_free_identifiers(self, *ids):
        """Unilaterally identifier-quote any number of strings."""
        return tuple([self.quote_identifier(i) for i in ids if i is not None])


class CubridExecutionContext(default.DefaultExecutionContext):
    def __init__(self, dialect, connection, dbapi_connection, compiled_ddl):
        super(CubridExecutionContext, self).__init__(
            dialect, connection, dbapi_connection, compiled_ddl
        )

    def should_autocommit_text(self, statement):
        return AUTOCOMMIT_REGEXP.match(statement)
