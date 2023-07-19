# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from typing import Set
from unittest import mock

import pytest

from bavapi import filters
from bavapi.client import Client, _default_brandscape_include
from bavapi.http import HTTPClient
from bavapi.query import Query
from bavapi.typing import OptionalListOr

from .helpers import wraps

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


# PRIVATE TESTS


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("test", {"brand", "study", "category", "audience", "test"}),
        (None, {"brand", "study", "category", "audience"}),
        (["test"], {"brand", "study", "category", "audience", "test"}),
    ),
)
def test_brandscape_query_default_include(
    value: OptionalListOr[str], expected: Set[str]
):
    assert set(_default_brandscape_include(value)) == expected  # type: ignore


def test_brandscape_query_default_include_partial():
    assert _default_brandscape_include("brand") == "brand"


def test_brandscape_query_no_default_include():
    assert _default_brandscape_include("no_default") is None


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
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1}]))
async def test_raw_query(mock_query: mock.AsyncMock, fount: Client):
    await fount.raw_query("request", Query())

    mock_query.assert_awaited_once_with("request", Query())


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1}]))
async def test_audiences(mock_query: mock.AsyncMock, fount: Client):
    await fount.audiences(active=1, include="test")

    mock_query.assert_awaited_once_with(
        "audiences", Query(filters=filters.AudiencesFilters(active=1), include="test")
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brands(mock_query: mock.AsyncMock, fount: Client):
    await fount.brands(country_codes="test", fields="test")

    mock_query.assert_awaited_once_with(
        "brands",
        Query(filters=filters.BrandsFilters(country_codes="test"), fields="test"),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brandscape_data(mock_query: mock.AsyncMock, fount: Client):
    await fount.brandscape_data(studies=1, metric_keys="test")

    mock_query.assert_awaited_once_with(
        "brandscape-data",
        Query(
            filters=filters.BrandscapeFilters(studies=1),
            metric_keys="test",
            include=["study", "brand", "category", "audience"],
        ),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_studies(mock_query: mock.AsyncMock, fount: Client):
    await fount.studies(include="test", full_year=1)

    mock_query.assert_awaited_once_with(
        "studies", Query(filters=filters.StudiesFilters(full_year=1), include="test")
    )
