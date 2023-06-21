# pylint: disable=missing-class-docstring, missing-module-docstring, missing-function-docstring

import sys

import pytest

from bavapi.reference._int_enum import IntEnum


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="not needed after python 3.11")
def test_int_enum_str():
    class MockRef(IntEnum):
        A = 1

    assert str(MockRef.A) == "1"
    assert MockRef.A.__str__.__name__ == "_int_enum_str"
