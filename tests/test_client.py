# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from typing import Set
from unittest import mock

import pytest

from bavapi import filters
from bavapi.client import Client, _default_include
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


def test_init_user_agent():
    fount = Client("test_token", user_agent="TEST_AGENT")

    assert fount._client.client.headers["User-Agent"] == "TEST_AGENT"


# PRIVATE TESTS


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("test", {"brand", "study", "test"}),
        (None, {"brand", "study"}),
        (["test"], {"brand", "study", "test"}),
    ),
)
def test_default_include(value: OptionalListOr[str], expected: Set[str]):
    defaults = ["brand", "study"]
    assert set(_default_include(value, defaults)) == expected  # type: ignore


def test_default_include_partial():
    assert _default_include("brand", ["brand", "study"]) == "brand"


def test_no_default_include():
    assert _default_include("no_default", ["brand", "study"]) is None


# PUBLIC TESTS


def test_per_page():
    _fount = Client("token")
    assert _fount.per_page == 100
    _fount.per_page = 1000
    assert _fount._client.per_page == 1000


def test_verbose():
    _fount = Client("token")
    assert _fount.verbose
    _fount.verbose = False
    assert not _fount._client.verbose


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
async def test_brand_metrics(mock_query: mock.AsyncMock, fount: Client):
    await fount.brand_metrics(active=1, fields="test")

    mock_query.assert_awaited_once_with(
        "brand-metrics",
        Query(filters=filters.BrandMetricsFilters(active=1), fields="test"),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brand_metric_groups(mock_query: mock.AsyncMock, fount: Client):
    await fount.brand_metric_groups(active=1, fields="test")

    mock_query.assert_awaited_once_with(
        "brand-metric-groups",
        Query(filters=filters.BrandMetricGroupsFilters(active=1), fields="test"),
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
async def test_categories(mock_query: mock.AsyncMock, fount: Client):
    await fount.categories(sector=1, fields="test")

    mock_query.assert_awaited_once_with(
        "categories",
        Query(
            filters=filters.CategoriesFilters(sector=1),
            fields="test",
            include=["sector"],
        ),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_collections(mock_query: mock.AsyncMock, fount: Client):
    await fount.collections(public=1, fields="test")

    mock_query.assert_awaited_once_with(
        "collections",
        Query(filters=filters.CollectionsFilters(public=1), fields="test"),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_sectors(mock_query: mock.AsyncMock, fount: Client):
    await fount.sectors(in_most_influential=1, fields="test")

    mock_query.assert_awaited_once_with(
        "sectors",
        Query(filters=filters.SectorsFilters(in_most_influential=1), fields="test"),
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_studies(mock_query: mock.AsyncMock, fount: Client):
    await fount.studies(include="test", full_year=1)

    mock_query.assert_awaited_once_with(
        "studies", Query(filters=filters.StudiesFilters(full_year=1), include="test")
    )
