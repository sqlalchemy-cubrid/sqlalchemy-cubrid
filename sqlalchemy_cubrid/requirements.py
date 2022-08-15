# sqlalchemy_cubrid/requirements.py
# Copyright (C) 2021-2022 by sqlalchemy-cubrid authors and contributors
# <see AUTHORS file>
#
# This module is part of sqlalchemy-cubrid and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

# Requirements specifies the features this dialect does/does not support for testing purposes
# Reference: https://github.com/zzzeek/sqlalchemy/blob/master/README.dialects.rst
from sqlalchemy.testing.requirements import SuiteRequirements

from sqlalchemy.testing import exclusions


class Requirements(SuiteRequirements):
    @property
    def nullable_booleans(self):
        """Target database allows boolean columns to store NULL."""
        # Access Yes/No doesn't allow null
        return exclusions.closed()

    @property
    def returning(self):
        return exclusions.open()
