# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring

import datetime
from pathlib import Path
from typing import Callable, Dict, Optional, TypeVar
from unittest import mock

import pandas as pd
import pytest

from bavapi.client import Client
from bavapi.query import Query
from bavapi.reference import generate_reference as uref

TEST_DT = datetime.datetime(2023, 1, 1, 12, 0, 0)


T = TypeVar("T")


def wraps(return_value: Optional[T] = None) -> Callable[..., Optional[T]]:
    def _wraps(*_, **__):
        return return_value

    return _wraps


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def fount(monkeypatch: pytest.MonkeyPatch) -> Client:
    _fount = Client("TOKEN")

    async def mock_func(*_, **__):
        return [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]

    monkeypatch.setattr(_fount, "raw_query", mock_func)

    return _fount


def test_parse_reference():
    mock_data = pd.Series(("ITEM ONE", "ITEM 2"))

    parsed = uref.parse_reference(mock_data, {" ": "_"}, {"2": "TWO"})

    assert parsed == {"ITEM_ONE": "0", "ITEM_TWO": "1"}


@pytest.mark.anyio
async def test_get_references(fount: Client):
    def func(x: pd.Series) -> Dict[str, str]:
        return {str(k): str(v) for k, v in x.to_dict().items()}  # pragma: no cover

    items = await uref.get_references(fount, [uref.RefConfig("test", "", func)])

    assert items == [[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]]


def test_process_items():
    data = [
        {"id": 1, "name": "A", "is_active": 1},
        {"id": 2, "name": "B", "is_active": 0},
    ]
    config = uref.RefConfig(
        "test", "", lambda x: {str(k): str(v) for k, v in x.items()}
    )

    processed = uref.process_items(data, config)

    assert processed == {"1": "A"}


def test_generate_source():
    updated_source = (
        '"""Tests class for holding tests IDs."""\n\n'
        "# This file was generated from active tests in the Fount.\n"
        f"# Tests retrieved on {TEST_DT.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "from bavapi.reference._int_enum import IntEnum\n\n\n"
        'class Tests(IntEnum):\n    """Tests IDs for Fount API queries."""\n\n'
        "    A = 1\n"
    )

    assert (
        uref.generate_source("tests", {"A": "1"}, TEST_DT).splitlines()
        == updated_source.splitlines()
    )


@mock.patch("bavapi.reference.generate_reference.Path.exists", return_value=True)
def test_write_to_file(mock_exists: mock.MagicMock):
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open:
        uref.write_to_file("", Path("folder/blah.py"))

    mock_open.assert_called_once_with(Path("folder/blah.py"), "w", encoding="utf-8")
    mock_exists.assert_called_once()


@mock.patch("bavapi.reference.generate_reference.Path.mkdir")
def test_write_to_file_not_exists(mock_mkdir: mock.MagicMock):
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open:
        uref.write_to_file("", Path("folder/blah.py"))

    mock_open.assert_called_once_with(Path("folder/blah.py"), "w", encoding="utf-8")
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_parse_args_name():
    argv = ["-n", "audiences"]

    args = uref.parse_args(argv)

    assert not args.all
    assert args.name == "audiences"


def test_parse_args_all():
    argv = ["-a"]

    args = uref.parse_args(argv)

    assert args.all
    assert args.name == ""


def test_main_no_args():
    assert uref.main([]) == 1


@mock.patch(
    "bavapi.reference.generate_reference.Client.raw_query",
    wraps=wraps([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]),
)
@mock.patch("bavapi.reference.generate_reference.write_to_file")
def test_main(mock_write_to_file: mock.Mock, mock_raw_query: mock.AsyncMock):
    args = ["-n", "audiences"]

    uref.main(args)

    mock_write_to_file.assert_called_once()
    mock_raw_query.assert_awaited_once_with("audiences", Query())


@mock.patch(
    "bavapi.reference.generate_reference.Client.raw_query",
    wraps=wraps(
        [
            {"id": 1, "name": "A", "country_name": "A"},
            {"id": 2, "name": "B", "country_name": "B"},
        ]
    ),
)
@mock.patch("bavapi.reference.generate_reference.write_to_file")
def test_main_all(mock_write_to_file: mock.Mock, mock_raw_query: mock.AsyncMock):
    args = ["-a"]

    uref.main(args)

    assert len(mock_write_to_file.call_args_list) == 2
    assert len(mock_raw_query.call_args_list) == 2
