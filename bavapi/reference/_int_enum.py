"""Patch string representation of pre-3.11 Python to provide a string of the code integers.

Read more at <https://peps.python.org/pep-0663/>."""

# pylint: disable=useless-import-alias

import sys
from enum import IntEnum as IntEnum

__all__ = ("IntEnum",)

if sys.version_info < (3, 11):

    def _int_enum_str(self: IntEnum) -> str:
        return str(self.value)

    IntEnum.__str__ = _int_enum_str
