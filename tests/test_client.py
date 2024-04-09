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

from .helpers import MockHTTPClient

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
async def test_context_manager(fount: Client, http_client: MockHTTPClient):
    async with fount as fount_ctx:
        assert isinstance(fount_ctx, Client)

    assert http_client.is_closed


@pytest.mark.anyio
async def test_aclose(fount: Client, http_client: MockHTTPClient):
    await fount.aclose()

    assert http_client.is_closed


@pytest.mark.anyio
async def test_raw_query(fount: Client, http_client: MockHTTPClient):
    http_client.add_response(data=[{"1": 1}])

    res = await fount.raw_query("request", Query())

    assert res == [{"1": 1}]
    http_client.mock_query.assert_awaited_once_with("request", Query())


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.AudiencesFilters(active=1), fields="test"))
)
async def test_audiences(
    fount: Client, query: Optional[Query], http_client: MockHTTPClient
):
    http_client.add_response(data=[{"1": 1}])

    await fount.audiences(active=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "audiences", Query(filters=filters.AudiencesFilters(active=1), fields="test")
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.AudienceGroupsFilters(name="a"), fields="test")),  # type: ignore
)
async def test_audience_groups(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.audience_groups(name="a", fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "audience-groups",
        Query(filters=filters.AudienceGroupsFilters(name="a"), fields="test"),  # type: ignore
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.BrandsFilters(country_codes="test"), fields="test")),
)
async def test_brands(
    fount: Client, query: Optional[Query], http_client: MockHTTPClient
):
    http_client.add_response(data=[{"1": 1}])

    await fount.brands(country_codes="test", fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "brands",
        Query(filters=filters.BrandsFilters(country_codes="test"), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.BrandMetricsFilters(active=1), fields="test"))
)
async def test_brand_metrics(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.brand_metrics(active=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "brand-metrics",
        Query(filters=filters.BrandMetricsFilters(active=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.BrandMetricGroupsFilters(active=1), fields="test")),
)
async def test_brand_metric_groups(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.brand_metric_groups(active=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
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
async def test_brandscape_data(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.brandscape_data(studies=1, metric_keys="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
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
            filters=filters.CategoriesFilters(sectors=1),
            fields="test",
            include=["sector"],
        ),
    ),
)
async def test_categories(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.categories(sectors=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "categories",
        Query(
            filters=filters.CategoriesFilters(sectors=1),
            fields="test",
            include=["sector"],
        ),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.CitiesFilters(countries=1), fields="test")),
)
async def test_cities(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.cities(countries=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "cities",
        Query(filters=filters.CitiesFilters(countries=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.CollectionsFilters(public=1), fields="test"))
)
async def test_collections(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.collections(public=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "collections",
        Query(filters=filters.CollectionsFilters(public=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.CompaniesFilters(public=1), fields="test")),
)
async def test_companies(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.companies(public=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "companies",
        Query(filters=filters.CompaniesFilters(public=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.CountriesFilters(active=1), fields="test")),
)
async def test_countries(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.countries(active=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "countries",
        Query(filters=filters.CountriesFilters(active=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.RegionsFilters(name="a"), fields="test")),  # type: ignore
)
async def test_regions(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.regions(name="a", fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "regions",
        Query(filters=filters.RegionsFilters(name="a"), fields="test"),  # type: ignore
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.SectorsFilters(in_most_influential=1), fields="test")),
)
async def test_sectors(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.sectors(in_most_influential=1, fields="test", query=query)

    http_client.mock_query.assert_awaited_once_with(
        "sectors",
        Query(filters=filters.SectorsFilters(in_most_influential=1), fields="test"),
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query", (None, Query(filters=filters.StudiesFilters(full_year=1), fields="test"))
)
async def test_studies(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.studies(fields="test", full_year=1, query=query)

    http_client.mock_query.assert_awaited_once_with(
        "studies", Query(filters=filters.StudiesFilters(full_year=1), fields="test")
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query",
    (None, Query(filters=filters.YearsFilters(year=2023), fields="test")),  # type: ignore
)
async def test_years(
    fount: Client,
    query: Optional[Query],
    http_client: MockHTTPClient,
):
    http_client.add_response(data=[{"1": 1}])

    await fount.years(fields="test", year=2023, query=query)

    http_client.mock_query.assert_awaited_once_with(
        "years",
        Query(filters=filters.YearsFilters(year=2023), fields="test"),  # type: ignore
    )
