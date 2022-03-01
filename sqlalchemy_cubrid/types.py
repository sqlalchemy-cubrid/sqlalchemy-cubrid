# sqlalchemy_cubrid/types.py
# Copyright (C) 2021-2022 by Curbrid
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.sql import sqltypes


class _NumericType(object):
    """Base for CUBRID numeric types."""

    def __init__(self, **kw):
        super(_NumericType, self).__init__(**kw)


class NUMERIC(_NumericType, sqltypes.NUMERIC):
    """CUBRID NUMERIC type.
    Default value is NUMERIC(15,0)
    """

    __visit_name__ = "NUMERIC"

    def __init__(self, precision=None, scale=None, **kw):
        super(NUMERIC, self).__init__(precision=precision, scale=scale, **kw)
