# test/test_suite.py
import pytest

from sqlalchemy.testing.suite import *

from sqlalchemy.testing.suite import BooleanTest as _BooleanTest

class BooleanTest(_BooleanTest):
    @pytest.mark.skip(reason="Cubrid does not support boolean types.")
    def test_round_trip(self):
        pass
