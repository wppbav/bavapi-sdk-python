# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=redefined-outer-name, protected-access

import os
import ssl
from typing import Any, AsyncGenerator, Callable, Coroutine, Dict, List

import pandas as pd
import pytest
from dotenv import load_dotenv

from bavapi import filters
from bavapi.client import Client
from bavapi.query import Query


@pytest.mark.anyio
@pytest.fixture(scope="module")
async def fount() -> AsyncGenerator[Client, None]:
    load_dotenv()

    async with Client(os.environ["FOUNT_API_KEY"]) as _fount:
        yield _fount


@pytest.mark.e2e
@pytest.mark.anyio
async def test_raw_query(fount: Client):
    result: List[Dict[str, Any]] = []
    for _ in range(5):  # pragma: no cover
        try:
            result = await fount.raw_query(
                "countries",
                Query(filters={"is_active": 1}, include="region", max_pages=2),
            )
            break
        except ssl.SSLError:
            print("Failed due to SSL error...")
            continue

    assert result
    assert len(result) == 200
    assert "region" in result[0]


@pytest.mark.e2e
@pytest.mark.anyio
async def test_with_filters_one_page(fount: Client):
    result: pd.DataFrame = pd.DataFrame()
    for _ in range(5):  # pragma: no cover
        try:
            result = await fount.studies(
                filters=filters.StudiesFilters(active=1),
                include="country",
                page=1,
                per_page=25,
            )
            break
        except ssl.SSLError:
            print("Failed due to SSL error...")
            continue

    assert "country_id" in result
    assert result["is_active"].unique()[0] == 1
    assert result.shape[0] == 25


@pytest.mark.e2e
@pytest.mark.anyio
@pytest.mark.parametrize(
    ("endpoint", "filters"),
    (
        ("audiences", {}),
        ("brands", {}),
        ("brandscape_data", {"studies": 546}),
        ("studies", {}),
    ),
)
async def test_endpoints(fount: Client, endpoint: str, filters: Dict[str, Any]):
    func: Callable[..., Coroutine[Any, Any, pd.DataFrame]] = getattr(fount, endpoint)

    result = await func(filters=filters, max_pages=2, per_page=25)

    assert result.shape[0] == 50
    assert "id" in result
