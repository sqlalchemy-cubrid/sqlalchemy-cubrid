# test/test_alembic.py
# Copyright (C) 2021-2026 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""Tests for Alembic migration support (sqlalchemy_cubrid.alembic_impl).

These tests verify that the CubridImpl class is correctly configured and
can be discovered by Alembic via the entry-point mechanism.
"""

from __future__ import annotations

import importlib
import sys
from unittest import mock

import pytest

try:
    import tomllib as toml_mod
except ModuleNotFoundError:
    import tomli as toml_mod


def _load_pyproject():
    """Load pyproject.toml."""
    import pathlib

    pyproject = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        return toml_mod.load(f)


class TestCubridImpl:
    """Tests for the CubridImpl Alembic implementation class."""

    def test_import(self):
        """CubridImpl can be imported from the alembic_impl module."""
        from sqlalchemy_cubrid.alembic_impl import CubridImpl

        assert CubridImpl is not None

    def test_dialect_name(self):
        """CubridImpl.__dialect__ is set to 'cubrid'."""
        from sqlalchemy_cubrid.alembic_impl import CubridImpl

        assert CubridImpl.__dialect__ == "cubrid"

    def test_transactional_ddl_false(self):
        """CUBRID auto-commits DDL, so transactional_ddl must be False."""
        from sqlalchemy_cubrid.alembic_impl import CubridImpl

        assert CubridImpl.transactional_ddl is False

    def test_subclass_of_default_impl(self):
        """CubridImpl inherits from alembic.ddl.impl.DefaultImpl."""
        from alembic.ddl.impl import DefaultImpl

        from sqlalchemy_cubrid.alembic_impl import CubridImpl

        assert issubclass(CubridImpl, DefaultImpl)

    def test_class_registered_in_impl_registry(self):
        """Alembic's DefaultImpl registry should know about 'cubrid'."""
        from alembic.ddl.impl import _impls

        # Import triggers class registration via metaclass
        from sqlalchemy_cubrid.alembic_impl import CubridImpl

        # _impls is the internal registry keyed by dialect name
        assert "cubrid" in _impls
        assert _impls["cubrid"] is CubridImpl

    def test_entry_point_registered(self):
        """Verify the entry point is declared in pyproject.toml."""
        config = _load_pyproject()

        entry_points = config["project"]["entry-points"]
        assert "alembic.ddl" in entry_points
        assert entry_points["alembic.ddl"]["cubrid"] == (
            "sqlalchemy_cubrid.alembic_impl:CubridImpl"
        )

    def test_optional_dependency_declared(self):
        """Verify the [alembic] optional dependency is declared in pyproject.toml."""
        config = _load_pyproject()

        optional_deps = config["project"]["optional-dependencies"]
        assert "alembic" in optional_deps
        assert any("alembic" in dep for dep in optional_deps["alembic"])


class TestAlembicImportError:
    """Test that a clear error is raised when alembic is not installed."""

    def test_import_error_without_alembic(self):
        """If alembic is not installed, importing alembic_impl raises ImportError."""
        # Remove alembic_impl from cache so we can re-import it
        module_key = "sqlalchemy_cubrid.alembic_impl"
        saved = sys.modules.pop(module_key, None)

        try:
            with mock.patch.dict(
                sys.modules,
                {"alembic": None, "alembic.ddl": None, "alembic.ddl.impl": None},
            ):
                # Force re-import
                if module_key in sys.modules:
                    del sys.modules[module_key]
                with pytest.raises(ImportError, match="Alembic is required"):
                    importlib.import_module(module_key)
        finally:
            # Restore
            if saved is not None:
                sys.modules[module_key] = saved
            elif module_key in sys.modules:
                del sys.modules[module_key]
