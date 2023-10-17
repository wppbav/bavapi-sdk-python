# pylint: disable=missing-class-docstring, missing-module-docstring, missing-function-docstring

from bavapi._reference.int_enum import IntEnum


def test_int_enum_str():
    class MockRef(IntEnum):
        A = 1

    assert str(MockRef.A) == "1"
