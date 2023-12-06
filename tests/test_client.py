# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from typing import Optional, Set
from unittest import mock

import pytest

from bavapi import filters
from bavapi.client import BASE_URL, USER_AGENT, Client, _default_include
from bavapi.http import HTTPClient
from bavapi.query import Query
from bavapi.typing import OptionalListOr

from .helpers import wraps

# CLASS INIT TESTS


def test_init(mock_async_client: mock.MagicMock):
    fount = Client("test_token")
    mock_async_client.assert_called_once_with(
        headers={
            "Authorization": "Bearer test_token",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        timeout=30.0,
        verify=True,
        base_url=BASE_URL,
    )
    assert isinstance(fount._client, HTTPClient)


def test_init_no_token():
    with pytest.raises(ValueError) as excinfo:
        Client()

    assert excinfo.value.args[0] == "You must provide `auth_token` or `client`."


def test_init_user_agent(mock_async_client: mock.MagicMock):
    fount = Client("test_token", user_agent="test_agent")
    mock_async_client.assert_called_once_with(
        headers={
            "Authorization": "Bearer test_token",
            "Accept": "application/json",
            "User-Agent": "test_agent",
        },
        timeout=30.0,
        verify=True,
        base_url=BASE_URL,
    )
    assert isinstance(fount._client, HTTPClient)


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


def test_per_page(fount: Client):
    assert fount.per_page == 100
    fount.per_page = 1000
    assert fount._client.per_page == 1000

    fount.per_page = 100


def test_verbose(fount: Client):
    assert fount.verbose
    fount.verbose = False
    assert not fount._client.verbose

    fount.verbose = True


def test_batch_size(fount: Client):
    assert fount.batch_size == 10
    fount.batch_size = 100
    assert fount._client.batch_size == 100

    fount.batch_size = 10


def test_n_workers(fount: Client):
    assert fount.n_workers == 2
    fount.n_workers = 1
    assert fount._client.n_workers == 1

    fount.n_workers = 2


def test_retries(fount: Client):
    assert fount.retries == 3
    fount.retries = 2
    assert fount._client.retries == 2

    fount.retries = 3


def test_on_errors(fount: Client):
    assert fount.on_errors == "warn"
    fount.on_errors = "raise"
    assert fount._client.on_errors == "raise"

    fount.on_errors = "warn"


@pytest.mark.anyio
async def test_context_manager(mock_async_client: mock.MagicMock):
    _fount = Client(client=HTTPClient(client=mock_async_client))
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
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.AudiencesFilters(active=1), fields="test"))
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1}]))
async def test_audiences(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.audiences(active=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "audiences", Query(filters=filters.AudiencesFilters(active=1), fields="test")
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.BrandsFilters(country_codes="test"), fields="test")),
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brands(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.brands(country_codes="test", fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "brands",
        Query(filters=filters.BrandsFilters(country_codes="test"), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.BrandMetricsFilters(active=1), fields="test"))
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brand_metrics(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.brand_metrics(active=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "brand-metrics",
        Query(filters=filters.BrandMetricsFilters(active=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.BrandMetricGroupsFilters(active=1), fields="test")),
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brand_metric_groups(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.brand_metric_groups(active=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "brand-metric-groups",
        Query(filters=filters.BrandMetricGroupsFilters(active=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (
        None,
        Query(
            filters=filters.BrandscapeFilters(studies=1),
            metric_keys="test",
            include=["study", "brand", "category", "audience"],
        ),
    ),
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_brandscape_data(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.brandscape_data(studies=1, metric_keys="test", query=query)

    mock_query.assert_awaited_once_with(
        "brandscape-data",
        Query(
            filters=filters.BrandscapeFilters(studies=1),
            metric_keys="test",
            include=["study", "brand", "category", "audience"],
        ),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (
        None,
        Query(
            filters=filters.CategoriesFilters(sector=1),
            fields="test",
            include=["sector"],
        ),
    ),
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_categories(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.categories(sector=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "categories",
        Query(
            filters=filters.CategoriesFilters(sector=1),
            fields="test",
            include=["sector"],
        ),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.CollectionsFilters(public=1), fields="test"))
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_collections(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.collections(public=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "collections",
        Query(filters=filters.CollectionsFilters(public=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.SectorsFilters(in_most_influential=1), fields="test")),
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_sectors(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.sectors(in_most_influential=1, fields="test", query=query)

    mock_query.assert_awaited_once_with(
        "sectors",
        Query(filters=filters.SectorsFilters(in_most_influential=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.StudiesFilters(full_year=1), fields="test"))
)
@mock.patch("bavapi.http.HTTPClient.query", wraps=wraps([{"1": 1, "2": 2}]))
async def test_studies(
    mock_query: mock.AsyncMock, fount: Client, query: Optional[Query]
):
    await fount.studies(fields="test", full_year=1, query=query)

    mock_query.assert_awaited_once_with(
        "studies", Query(filters=filters.StudiesFilters(full_year=1), fields="test")
    )
