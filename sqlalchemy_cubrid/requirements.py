# sqlalchemy_cubrid/requirements.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""CUBRID test-suite requirement flags.

These tell SQLAlchemy's built-in test suite which features this dialect
supports so tests are automatically skipped when the feature is absent.

Reference: https://github.com/sqlalchemy/sqlalchemy/blob/main/README.dialects.rst
"""

from __future__ import annotations

from sqlalchemy.testing import exclusions
from sqlalchemy.testing.requirements import SuiteRequirements


class Requirements(SuiteRequirements):
    """CUBRID-specific requirement flags for the SA test suite."""

    # ----- RETURNING -----

    @property
    def returning(self):
        """CUBRID does not support INSERT/UPDATE/DELETE … RETURNING."""
        return exclusions.closed()

    @property
    def insert_returning(self):
        return exclusions.closed()

    @property
    def update_returning(self):
        return exclusions.closed()

    @property
    def delete_returning(self):
        return exclusions.closed()

    # ----- Booleans -----

    @property
    def nullable_booleans(self):
        """CUBRID maps BOOLEAN to SMALLINT which is nullable."""
        return exclusions.open()

    @property
    def non_native_boolean_unconstrained(self):
        """The SMALLINT emulation has no CHECK constraint."""
        return exclusions.open()

    # ----- Sequences -----

    @property
    def sequences(self):
        """CUBRID does not support sequences."""
        return exclusions.closed()

    @property
    def sequences_optional(self):
        return exclusions.closed()

    # ----- Schema / DDL -----

    @property
    def schemas(self):
        """CUBRID does not support multiple schemas."""
        return exclusions.closed()

    @property
    def temp_table_names(self):
        return exclusions.closed()

    @property
    def temporary_tables(self):
        return exclusions.closed()

    @property
    def temporary_views(self):
        return exclusions.closed()

    @property
    def table_ddl_if_exists(self):
        """CUBRID supports IF NOT EXISTS / IF EXISTS in DDL."""
        return exclusions.open()

    @property
    def comment_reflection(self):
        """CUBRID supports table and column comments."""
        return exclusions.open()

    @property
    def check_constraint_reflection(self):
        return exclusions.closed()

    # ----- DML -----

    @property
    def empty_inserts(self):
        """CUBRID supports INSERT INTO t DEFAULT VALUES."""
        return exclusions.open()

    @property
    def insert_from_select(self):
        return exclusions.open()

    @property
    def ctes(self):
        """CUBRID 11 supports CTEs."""
        return exclusions.open()

    @property
    def ctes_on_dml(self):
        return exclusions.closed()

    # ----- SELECT features -----

    @property
    def window_functions(self):
        """CUBRID supports window functions (ROW_NUMBER, RANK, etc.) with OVER()."""
        return exclusions.open()

    @property
    def intersect(self):
        return exclusions.open()

    @property
    def except_(self):
        return exclusions.open()

    @property
    def fetch_no_order(self):
        return exclusions.open()

    @property
    def order_by_col_from_union(self):
        return exclusions.open()

    # ----- Type support -----

    @property
    def unicode_ddl(self):
        return exclusions.open()

    @property
    def datetime_literals(self):
        return exclusions.closed()

    @property
    def date(self):
        return exclusions.open()

    @property
    def time(self):
        return exclusions.open()

    @property
    def datetime(self):
        return exclusions.open()

    @property
    def timestamp(self):
        return exclusions.open()

    @property
    def text_type(self):
        return exclusions.open()

    @property
    def json_type(self):
        """CUBRID does not support JSON type."""
        return exclusions.closed()

    @property
    def array_type(self):
        return exclusions.closed()

    @property
    def uuid_data_type(self):
        return exclusions.closed()

    # ----- Misc -----

    @property
    def views(self):
        return exclusions.open()

    @property
    def savepoints(self):
        return exclusions.open()

    @property
    def foreign_keys(self):
        return exclusions.open()

    @property
    def self_referential_foreign_keys(self):
        return exclusions.open()

    @property
    def unique_constraint_reflection(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_reflection(self):
        return exclusions.open()

    @property
    def index_reflection(self):
        return exclusions.open()

    @property
    def primary_key_constraint_reflection(self):
        return exclusions.open()

    @property
    def on_update_cascade(self):
        return exclusions.open()

    @property
    def on_delete_cascade(self):
        return exclusions.open()

    @property
    def server_side_cursors(self):
        return exclusions.closed()

    @property
    def independent_connections(self):
        return exclusions.open()

    # ----- Binary / LOB -----

    @property
    def binary_comparisons(self):
        """CUBRID BLOB roundtrip has driver-level issues."""
        return exclusions.closed()

    @property
    def binary_literals(self):
        """CUBRID does not support binary literal syntax."""
        return exclusions.closed()

    # ----- Identifier quoting -----

    @property
    def unusual_column_name_characters(self):
        """CUBRID has limited support for special characters in identifiers."""
        return exclusions.closed()

    @property
    def implicitly_named_constraints(self):
        """CUBRID FK reflection has issues with special-character table names."""
        return exclusions.closed()

    # ----- SELECT FOR UPDATE -----

    @property
    def update_nowait(self):
        """CUBRID does not support SELECT ... FOR UPDATE NOWAIT."""
        return exclusions.closed()

    @property
    def for_update(self):
        """CUBRID supports SELECT ... FOR UPDATE [OF col1, col2]."""
        return exclusions.open()
