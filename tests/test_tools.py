# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from typing import Any, Dict, Iterator
from unittest import mock

import pandas as pd
import pytest

from bavapi.exceptions import APIError
from bavapi.tools import ToolsClient, _raise_if_fails
from tests.helpers import MockAsyncClient


@pytest.fixture(scope="module")
def client(http_instance: MockAsyncClient) -> Iterator[ToolsClient]:
    with http_instance as isntance:
        yield ToolsClient(client=isntance)


def test_client_init_with_client(http: MockAsyncClient):
    client = ToolsClient(client=http)

    assert client.client is http


def test_client_init_with_headers(mock_async_client: mock.Mock):
    _ = ToolsClient(headers={"test": "headers"}, base_url="test.com")

    mock_async_client.assert_called_once_with(
        headers={"test": "headers"}, timeout=30.0, verify=True, base_url="test.com"
    )


@pytest.mark.anyio
async def test_context_manager(http: MockAsyncClient):
    async with ToolsClient(client=http) as client:
        assert isinstance(client, ToolsClient)

    assert client.client.is_closed


@pytest.mark.anyio
async def test_aclose(client: ToolsClient, http: MockAsyncClient):
    await client.aclose()

    assert http.is_closed


@pytest.mark.anyio
async def test_get(client: ToolsClient, http: MockAsyncClient):
    http.add_response(data={"test": 1})

    resp = await client._get("request", params={})

    assert resp == {"test": 1}

    http.mock_get.assert_awaited_once_with("request", params={})


@pytest.mark.anyio
async def test_get_fails(client: ToolsClient, http: MockAsyncClient):
    http.add_response(400, "bad")

    with pytest.raises(APIError) as exc_info:
        await client._get("request", params={})

    assert exc_info.value.args == ("Error 400:\nbad\nurl=http://test_url/request",)


@pytest.mark.anyio
async def test_get_fails_to_parse(client: ToolsClient, http: MockAsyncClient):
    http.add_response(400, {"data": "bad"})

    with pytest.raises(APIError) as exc_info:
        await client._get("request", params={})

    assert exc_info.value.args == (
        "Error 400:\nAn error occurred with the Fount.\nurl=http://test_url/request",
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"brands": 1, "studies": [1, 2], "categories": 1, "collections": 1},
        {"brands": 1, "studies": [1, 2]},
    ),
)
async def test_archetypes_bad_params(kwargs: Dict[str, Any], client: ToolsClient):
    with pytest.raises(ValueError) as exc_info:
        await client.archetypes(**kwargs)

    assert exc_info.value.args == (
        "Either categories OR collections must be specified.",
    )


@pytest.mark.anyio
async def test_archetypes(client: ToolsClient, http: MockAsyncClient):
    pass


@pytest.mark.anyio
async def test_brand_personality_match(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": [{"test": 1, "metric1": 1, "metric2": 2}],
        }
    )

    resp = await client.brand_personality_match(brands=1, studies=[1, 2])

    pd.testing.assert_frame_equal(
        resp,
        pd.DataFrame({"test": [1], "metric1": [1], "metric2": [2]}).astype("int32"),
    )
    http.mock_get.assert_called_once_with(
        "brand-personality-match", params={"brands": 1, "studies": "1,2"}
    )


@pytest.mark.anyio
async def test_brand_vulnerability_map(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": [{"test": 1, "metric1": 1, "metric2": 2}],
        }
    )

    resp = await client.brand_vulnerability_map(brand=1)

    pd.testing.assert_frame_equal(
        resp,
        pd.DataFrame({"test": [1], "metric1": [1], "metric2": [2]}).astype("int32"),
    )
    http.mock_get.assert_called_once_with(
        "brand-vulnerability-map", params={"brand": 1}
    )


@pytest.mark.anyio
async def test_brand_worth_map(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": {
                "test": 1,
                "data": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
            }
        }
    )

    meta, data = await client.brand_worth_map(brands=1, studies=[1, 2])

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame({"key": ["A", "B"], "value": [1, 2]}).astype({"value": "int32"}),
    )
    assert meta == {"test": 1}
    http.mock_get.assert_called_once_with(
        "brand-worth-map", params={"brands": 1, "studies": "1,2"}
    )


@pytest.mark.anyio
async def test_category_worth_map(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": {
                "test": 1,
                "data": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
            }
        }
    )

    meta, data = await client.category_worth_map(categories=1, studies=[1, 2])

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame({"key": ["A", "B"], "value": [1, 2]}).astype({"value": "int32"}),
    )
    assert meta == {"test": 1}
    http.mock_get.assert_called_once_with(
        "category-worth-map", params={"categories": 1, "studies": "1,2"}
    )


@pytest.mark.anyio
async def test_commitment_funnel(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": [
                {
                    "test": 1,
                    "metrics": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
                }
            ]
        }
    )

    resp = await client.commitment_funnel(brands=1, studies=[1, 2])

    pd.testing.assert_frame_equal(resp, pd.DataFrame({"test": [1], "A": [1], "B": [2]}))
    http.mock_get.assert_called_once_with(
        "commitment-funnel", params={"brands": 1, "studies": "1,2"}
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"brand": 1, "study": 1, "categories": 1, "collections": 1},
        {"brand": 1, "study": 1},
    ),
)
async def test_cost_of_entry_bad_params(kwargs: Dict[str, Any], client: ToolsClient):
    with pytest.raises(ValueError) as exc_info:
        await client.cost_of_entry(**kwargs)

    assert exc_info.value.args == (
        "Either categories OR collections must be specified.",
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"brand": 1, "study": 1, "collections": 1},
        {"brand": 1, "study": 1, "categories": 1},
    ),
)
async def test_cost_of_entry(
    kwargs: Dict[str, Any], client: ToolsClient, http: MockAsyncClient
):
    http.add_response(
        data={
            "data": {
                "test": 1,
                "data": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
            }
        }
    )

    meta, data = await client.cost_of_entry(**kwargs)

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame({"key": ["A", "B"], "value": [1, 2]}).astype({"value": "int32"}),
    )
    assert meta == {"test": 1}
    http.mock_get.assert_called_once_with("cost-of-entry", params=kwargs)


@pytest.mark.anyio
async def test_love_plus(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": [
                {
                    "test": 1,
                    "data": {
                        "A": {"blah": "blah", "value": 1},
                        "B": {"blah": "blah", "value": 2},
                    },
                }
            ]
        }
    )

    data = await client.love_plus(brands=1, studies=[1, 2])

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame([{"test": 1, "A": 1, "B": 2}]),
    )
    http.mock_get.assert_called_once_with(
        "love-plus", params={"brands": 1, "studies": "1,2"}
    )


@pytest.mark.anyio
async def test_partnership_exchange_map(client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": {
                "test": 1,
                "data": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
            }
        }
    )

    meta, data = await client.partnership_exchange_map(
        brands=1, studies=[1, 2], comparison_brands=2
    )

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame({"key": ["A", "B"], "value": [1, 2]}).astype({"value": "int32"}),
    )
    assert meta == {"test": 1}
    http.mock_get.assert_called_once_with(
        "partnership-exchange-map",
        params={"brands": 1, "studies": "1,2", "comparison_brands": 2},
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"brands": 1, "studies": [1, 2], "categories": 1, "collections": 1},
        {"brands": 1, "studies": [1, 2]},
    ),
)
async def test_swot_bad_params(kwargs: Dict[str, Any], client: ToolsClient):
    with pytest.raises(ValueError) as exc_info:
        await client.swot(**kwargs)

    assert exc_info.value.args == (
        "Either categories OR collections must be specified.",
    )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "kwargs",
    (
        {"brands": 1, "studies": 1, "collections": 1},
        {"brands": 1, "studies": 1, "categories": 1},
    ),
)
async def test_swot(kwargs: Dict[str, Any], client: ToolsClient, http: MockAsyncClient):
    http.add_response(
        data={
            "data": {
                "test": 1,
                "data": [{"key": "A", "value": 1}, {"key": "B", "value": 2}],
            }
        }
    )

    meta, data = await client.swot(**kwargs)

    pd.testing.assert_frame_equal(
        data,
        pd.DataFrame({"key": ["A", "B"], "value": [1, 2]}).astype({"value": "int32"}),
    )
    assert meta == {"test": 1}
    http.mock_get.assert_called_once_with("swot", params=kwargs)


@pytest.mark.anyio
async def test_toplist_market(client: ToolsClient, http: MockAsyncClient):
    pass


def test_raise_if_fails_passes():
    with _raise_if_fails():
        pass


def test_raise_if_fails_raises():
    with pytest.raises(APIError) as exc_info:
        with _raise_if_fails():
            raise ValueError

    assert exc_info.value.args == ("Could not parse response",)
