# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=redefined-outer-name, too-few-public-methods

import asyncio
import sys
from types import ModuleType
from typing import Callable, Optional
from unittest import mock

import pytest

from bavapi import _jupyter

SetIpythonFunc = Callable[[Optional[bool]], None]


class IPython(ModuleType):
    """Mock IPython module attributes and functions"""

    def __init__(self, kernel: Optional[bool] = None) -> None:
        self.kernel = kernel
        self.get_ipython = self._get_ipython
        super().__init__(self.__class__.__name__)

    def _get_ipython(self) -> "IPython":
        return self


@pytest.fixture(scope="function")
def set_ipython():
    def _set_ipython(kernel: Optional[bool] = None) -> None:
        sys.modules["IPython"] = IPython(kernel)

    yield _set_ipython

    del sys.modules["IPython"]


def test_running_in_jupyter(set_ipython: SetIpythonFunc):
    set_ipython(True)

    assert _jupyter.running_in_jupyter()


def test_not_running_in_jupyter(set_ipython: SetIpythonFunc):
    set_ipython(None)

    assert not _jupyter.running_in_jupyter()


@mock.patch("bavapi._jupyter.nest_asyncio.apply")
def test_enabled_nested(mock_apply: mock.Mock):
    loop = asyncio.new_event_loop()

    _jupyter.patch_loop(loop)

    mock_apply.assert_called_once_with(loop)
