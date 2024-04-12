# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=redefined-outer-name, protected-access

import os
from typing import Any, Callable, Dict, Generator

import pandas as pd
import pytest
from dotenv import load_dotenv

import bavapi
from bavapi import filters
from bavapi.query import Query
from bavapi.tools import ToolsClient
from bavapi.typing import JSONDict


@pytest.fixture(scope="module", autouse=True)
def load_env() -> Generator[None, None, None]:
    load_dotenv()
    yield


@pytest.mark.e2e
def test_raw_query():
    result = bavapi.raw_query(
        os.environ["BAV_API_KEY"],
        "countries",
        Query(filters={"is_active": 1}, include="region", max_pages=2),
        retries=5,
    )

    assert result
    assert len(result) == 200
    assert "region" in result[0]


@pytest.mark.e2e
def test_with_filters_one_page():
    result = bavapi.studies(
        os.environ["BAV_API_KEY"],
        filters=filters.StudiesFilters(active=1),
        include="country",
        page=1,
        per_page=25,
        max_pages=1,
        retries=5,
    )

    assert "country_id" in result
    assert result["is_active"].unique()[0] == 1
    assert result.shape[0] == 25


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("endpoint", "filters"),
    (
        ("audiences", {}),
        ("audience_groups", {}),
        ("brand_metric_groups", {}),
        ("brand_metrics", {}),
        ("brands", {}),
        ("brandscape_data", {"studies": 546}),
        ("categories", {}),
        ("cities", {}),
        ("collections", {}),
        ("companies", {}),
        ("countries", {}),
        ("sectors", {}),
        ("studies", {}),
        ("years", {}),
    ),
)
def test_endpoints(endpoint: str, filters: Dict[str, Any]):
    func: Callable[..., pd.DataFrame] = getattr(bavapi, endpoint)

    result = func(
        os.environ["BAV_API_KEY"],
        filters=filters,
        max_pages=2,
        per_page=25,
        retries=5,
    )

    assert 0 < result.shape[0] <= 50
    assert "id" in result


@pytest.mark.e2e
@pytest.mark.anyio
@pytest.mark.parametrize(
    ("endpoint", "params"),
    (
        ("brand_personality_match", {"brands": 3100, "studies": 650}),
        ("brand_vulnerability_map", {"brand": 3100}),
        ("commitment_funnel", {"brands": 3100, "studies": 650}),
        ("love_plus", {"brands": 3100, "studies": 650}),
    ),
)
async def test_tools_no_metadata(endpoint: str, params: Dict[str, Any]):
    async with ToolsClient(os.environ["BAV_API_KEY"]) as client:
        result: pd.DataFrame = await getattr(client, endpoint)(**params)

    assert not result.empty


@pytest.mark.e2e
@pytest.mark.anyio
@pytest.mark.parametrize(
    ("endpoint", "params"),
    (
        ("brand_worth_map", {"brands": 3100, "studies": 650}),
        ("category_worth_map", {"categories": 1, "studies": 650}),
        ("cost_of_entry", {"brand": 3100, "study": 650, "categories": 1}),
        (
            "partnership_exchange_map",
            {"brands": 3100, "studies": 650, "comparison_brands": 31447},
        ),
        ("swot", {"brands": 3100, "studies": 650, "categories": 1}),
    ),
)
async def test_tools_with_metadata(endpoint: str, params: Dict[str, Any]):
    meta: JSONDict
    result: pd.DataFrame
    async with ToolsClient(os.environ["BAV_API_KEY"]) as client:
        meta, result = await getattr(client, endpoint)(**params)

    assert meta
    assert not result.empty
