"""Patch string representation of pre-3.11 Python to provide a string of the code integers.

Read more at <https://peps.python.org/pep-0663/>."""

# pylint: disable=useless-import-alias

import sys
from enum import IntEnum as _IntEnum

__all__ = ("IntEnum",)

if sys.version_info < (3, 11):

    class IntEnum(_IntEnum):
        """Patched IntEnum pre Python 3.11."""

        def __str__(self) -> str:
            return str(self.value)

else:
    IntEnum = _IntEnum
