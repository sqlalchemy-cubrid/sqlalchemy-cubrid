from sqlalchemy.dialects import registry
import pytest

registry.register("cubrid", "sqlalchemy_cubrid.dialect", "CubridDialect")
registry.register(
    "cubrid.cubrid", "sqlalchemy_cubrid.dialect", "CubridDialect"
)

pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *
