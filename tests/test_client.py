# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from typing import List, Optional, Set, TypeVar, Union
from unittest import mock

import pytest

from bavapi.client import Client, _default_brandscape_include
from bavapi.http import HTTPClient
from bavapi.query import Query

from .helpers import wraps

T = TypeVar("T")

# CLASS INIT TESTS


def test_init():
    fount = Client("test_token")
    assert isinstance(fount._client, HTTPClient)


def test_init_with_client(client: HTTPClient):
    fount = Client(client=client)
    assert fount._client is client


def test_init_no_token():
    with pytest.raises(ValueError) as excinfo:
        Client()

    assert excinfo.value.args[0] == "You must provide `auth_token` or `client`."


# PUBLIC TESTS


def test_per_page():
    _fount = Client("token")
    assert _fount.per_page == 100
    _fount.per_page = 1000
    assert _fount._client.per_page == 1000


@pytest.mark.anyio
async def test_context_manager():
    _fount = Client(client=HTTPClient())
    async with _fount as fount_ctx:
        assert isinstance(fount_ctx, Client)

    assert _fount._client.client.is_closed


@pytest.mark.anyio
async def test_aclose(fount: Client):
    with mock.patch("bavapi.client.HTTPClient.aclose", wraps=wraps()) as mock_aclose:
        await fount.aclose()

    mock_aclose.assert_called_once()


@pytest.mark.anyio
async def test_raw_query(fount: Client):
    with mock.patch.object(
        fount._client, "query", wraps=wraps([{"t": 1}])
    ) as mock_base_query:
        assert await fount.raw_query("request", Query()) == [{"t": 1}]

    mock_base_query.assert_awaited_once_with("request", Query())


@pytest.mark.anyio
async def test_audiences(fount: Client):
    with mock.patch.object(
        fount._client, "query", wraps=wraps([{"1": 1}])
    ) as mock_base_query:
        assert (await fount.audiences(audience_id=1)).shape == (1, 1)

    mock_base_query.assert_awaited_once_with("audiences", Query(id=1))


@pytest.mark.anyio
async def test_brands(fount: Client):
    with mock.patch.object(
        fount._client, "query", wraps=wraps([{"1": 1}])
    ) as mock_base_query:
        assert (await fount.brands(brand_id=1)).shape == (1, 1)

    mock_base_query.assert_awaited_once_with("brands", Query(id=1))


@pytest.mark.anyio
async def test_brandscape_data(fount: Client):
    with mock.patch.object(
        fount._client, "query", wraps=wraps([{"1": 1, "2": 2}])
    ) as mock_base_query:
        res = await fount.brandscape_data(fields="")
        assert res.shape == (1, 2)

    mock_base_query.assert_awaited_once_with(
        "brandscape-data",
        Query(fields="", include=["study", "brand", "category", "audience"]),
    )


@pytest.mark.anyio
async def test_studies(fount: Client):
    with mock.patch.object(
        fount._client, "query", wraps=wraps([{"1": 1, "2": 2}])
    ) as mock_base_query:
        assert (await fount.studies(study_id=1)).shape == (1, 2)

    mock_base_query.assert_awaited_once_with("studies", Query(id=1))


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("test", {"brand", "study", "category", "audience", "test"}),
        (None, {"brand", "study", "category", "audience"}),
        (["test"], {"brand", "study", "category", "audience", "test"}),
    ),
)
def test_brandscape_query_default_include(
    value: Optional[Union[str, List[str]]], expected: Set[str]
):
    assert set(_default_brandscape_include(value)) == expected  # type: ignore


def test_brandscape_query_default_include_partial():
    assert _default_brandscape_include("brand") == "brand"


def test_brandscape_query_no_default_include():
    assert _default_brandscape_include("no_default") is None
