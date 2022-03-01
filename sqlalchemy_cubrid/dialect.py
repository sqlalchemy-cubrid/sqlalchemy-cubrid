# sqlalchemy_cubrid/dialect.py
# Copyright (C) 2021-2022 by Curbrid
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.engine import default
from sqlalchemy_cubrid.compiler import (
    CubridCompiler,
    CubridDDLCompiler,
    CubridTypeCompiler,
)
from sqlalchemy_cubrid.base import (
    CubridIdentifierPreparer,
    CubridExecutionContext,
)


class CubridDialect(default.DefaultDialect):
    name = "cubrid"
    driver = "cubrid"

    statement_compiler = CubridCompiler
    ddl_compiler = CubridDDLCompiler
    type_compiler = CubridTypeCompiler

    preparer = CubridIdentifierPreparer
    execution_ctx_cls = CubridExecutionContext

    def __init__(self, **kwargs):
        super(CubridDialect, self).__init__(**kwargs)


dialect = CubridDialect
