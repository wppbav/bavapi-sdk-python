# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring

import datetime
from pathlib import Path
from typing import Dict
from unittest import mock

import pandas as pd
import pytest

from bavapi._reference import generate_reference as uref
from bavapi.client import Client
from bavapi.query import Query

from ..helpers import MockHTTPClient, wraps

TEST_DT = datetime.datetime(2023, 1, 1, 12, 0, 0)


def test_parse_reference():
    mock_data = pd.Series(("ITEM ONE", "ITEM 2"))

    parsed = uref.parse_reference(mock_data, {" ": "_"}, {"2": "TWO"})

    assert parsed == {"ITEM_ONE": "0", "ITEM_TWO": "1"}


@pytest.mark.anyio
async def test_get_references(fount: Client, http_client: MockHTTPClient):
    http_client.add_response(data=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}])

    def func(val: pd.Series) -> Dict[str, str]:
        return {str(k): str(v) for k, v in val.to_dict().items()}  # pragma: no cover

    items = await uref.get_references(fount, [uref.RefConfig("test", "", func)])

    assert items == [[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]]
    http_client.mock_query.assert_awaited_once_with("test", Query())


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
        "from bavapi._reference.int_enum import IntEnum\n\n\n"
        'class Tests(IntEnum):\n    """Tests IDs for Fount API queries."""\n\n'
        "    A = 1\n"
    )

    assert (
        uref.generate_source("tests", {"A": "1"}, TEST_DT).splitlines()
        == updated_source.splitlines()
    )


@mock.patch(
    "bavapi._reference.generate_reference.Path.glob",
    return_value=[Path("test_module.py"), Path("__init__.py")],
)
def test_generate_init_source(mock_glob: mock.MagicMock):
    res = uref.generate_init_source(Path("test_path"))

    mock_glob.assert_called_once_with("*.py")
    assert res == (
        '"""`bavapi` Reference classes for holding Fount IDs.\n\n'
        'Use them in place of integers when filtering requests.\n"""\n\n'
        "from test_path.test_module import Test_module\n\n"
        '__all__ = ("Test_module",)\n'
    )


@mock.patch("bavapi._reference.generate_reference.Path.exists", return_value=True)
def test_write_to_file(mock_exists: mock.MagicMock):
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open:
        uref.write_to_file("", Path("folder/blah.py"))

    mock_open.assert_called_once_with(Path("folder/blah.py"), "w", encoding="utf-8")
    mock_exists.assert_called_once()


@mock.patch("bavapi._reference.generate_reference.Path.mkdir")
def test_write_to_file_not_exists(mock_mkdir: mock.MagicMock):
    with mock.patch("builtins.open", new_callable=mock.mock_open) as mock_open:
        uref.write_to_file("", Path("folder/blah.py"))

    mock_open.assert_called_once_with(Path("folder/blah.py"), "w", encoding="utf-8")
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_parse_args_name():
    args = uref.parse_args(["-n", "audiences"])

    assert not args.all
    assert args.name == "audiences"


def test_parse_args_all():
    args = uref.parse_args(["-a"])

    assert args.all
    assert args.name == ""


def test_parse_args_dest():
    args = uref.parse_args(["-d", "test/folder"])

    assert args.folder == Path("test/folder")


def test_parse_args_token():
    args = uref.parse_args(["-t", "TOKEN"])

    assert args.token == "TOKEN"


@mock.patch("bavapi._reference.generate_reference.os.getenv", return_value="test_token")
def test_main_no_args(mock_getenv: mock.Mock, mock_async_client: mock.MagicMock):
    with pytest.raises(ValueError) as exc_info:
        uref.main([])

    assert exc_info.value.args == (
        "You must use either the `-a`/`--all` or the `-n`/`--name` arguments. "
        "Run `bavapi-gen-refs -h for more details and instructions.",
    )
    mock_getenv.assert_called_once_with("BAV_API_KEY", "")
    mock_async_client.assert_called_once()


@mock.patch(
    "bavapi._reference.generate_reference.Client.raw_query",
    wraps=wraps([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]),
)
@mock.patch("bavapi._reference.generate_reference.write_to_file")
def test_main(
    mock_write_to_file: mock.Mock,
    mock_raw_query: mock.AsyncMock,
    mock_async_client: mock.MagicMock,
):
    args = ["-n", "audiences"]

    with mock.patch(
        "bavapi._reference.generate_reference.os.getenv", return_value="test_token"
    ) as mock_getenv:
        uref.main(args)

    assert len(mock_write_to_file.call_args_list) == 2
    mock_raw_query.assert_awaited_once_with("audiences", Query())
    mock_getenv.assert_called_once_with("BAV_API_KEY", "")
    mock_async_client.assert_called_once()


@mock.patch(
    "bavapi._reference.generate_reference.Client.raw_query",
    wraps=wraps(
        [
            {"id": 1, "name": "A", "country_name": "A"},
            {"id": 2, "name": "B", "country_name": "B"},
        ]
    ),
)
@mock.patch("bavapi._reference.generate_reference.write_to_file")
@mock.patch(
    "bavapi._reference.generate_reference.generate_init_source", return_value=""
)
def test_main_all(
    mock_gen_init_source: mock.Mock,
    mock_write_to_file: mock.Mock,
    mock_raw_query: mock.AsyncMock,
    mock_async_client: mock.MagicMock,
):
    args = ["-a"]

    with mock.patch(
        "bavapi._reference.generate_reference.os.getenv", return_value="test_token"
    ) as mock_getenv:
        uref.main(args)

    mock_gen_init_source.assert_called_once_with(Path("bavapi_refs"))
    assert len(mock_write_to_file.call_args_list) == 3
    assert len(mock_raw_query.call_args_list) == 2
    mock_getenv.assert_called_once_with("BAV_API_KEY", "")
    mock_async_client.assert_called_once()


@mock.patch("dotenv.load_dotenv", wraps=wraps(raises=ImportError))
def test_main_no_token_no_dotenv(mock_load_dotenv: mock.Mock):
    args = ["-a"]

    with pytest.raises(ValueError) as excinfo:
        uref.main(args)

    assert excinfo.value.args == (
        "You must specify a Fount API token with the `-t`/`--token` argument, "
        "or install `python-dotenv` and set `BAV_API_KEY` in a `.env` file.",
    )
    mock_load_dotenv.assert_called_once()


@mock.patch(
    "bavapi._reference.generate_reference.Client.raw_query",
    wraps=wraps([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]),
)
@mock.patch("dotenv.load_dotenv", wraps=wraps(raises=ImportError))
@mock.patch("bavapi._reference.generate_reference.write_to_file")
@mock.patch(
    "bavapi._reference.generate_reference.generate_init_source", return_value=""
)
def test_main_with_token_arg(
    mock_gen_init_source: mock.Mock,
    mock_write_to_file: mock.Mock,
    mock_load_dotenv: mock.Mock,
    mock_raw_query: mock.AsyncMock,
    mock_async_client: mock.MagicMock,
):
    args = ["-n", "audiences", "-t", "test_token"]

    with mock.patch(
        "bavapi._reference.generate_reference.os.getenv", return_value="test_token"
    ) as mock_getenv:
        uref.main(args)

    mock_gen_init_source.assert_called_once_with(Path("bavapi_refs"))
    assert len(mock_write_to_file.call_args_list) == 2
    mock_load_dotenv.assert_not_called()
    mock_getenv.assert_called_once_with("BAV_API_KEY", "test_token")
    mock_raw_query.assert_awaited_once_with("audiences", Query())
    mock_async_client.assert_called_once()
