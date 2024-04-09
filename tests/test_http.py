# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from dataclasses import asdict, dataclass
from typing import Dict, Optional
from unittest import mock

import httpx
import pytest

from bavapi.exceptions import APIError, DataNotFoundError, RateLimitExceededError
from bavapi.http import HTTPClient, _calculate_pages
from bavapi.query import Query
from bavapi.typing import JSONData, JSONDict

from .helpers import MockAsyncClient

# HELPERS


@dataclass
class QueryResult:
    """Model for WPPBAV Fount query results"""

    data: JSONData
    links: Dict[str, str]
    meta: JSONDict

    def dict(self) -> JSONDict:
        return asdict(self)


def sample_data(
    data: Optional[JSONData] = None,
    per_page: int = 25,
    on_page: int = 25,
    total: int = 2000,
) -> JSONDict:
    return QueryResult(
        data=data if data is not None else {},
        links={},
        meta={
            "per_page": per_page,
            "to": on_page,
            "total": total,
        },
    ).dict()


def rate_limited_response() -> httpx.Response:
    return MockAsyncClient.build_response(
        200,
        data=sample_data([{}]),
        headers=httpx.Headers(
            {"x-ratelimit-remaining": "1", "x-ratelimit-limit": "500"}
        ),
    )


# TESTS


def test_client_init_with_client(http: MockAsyncClient):
    client = HTTPClient(client=http)

    assert client.client is http


@pytest.mark.anyio
async def test_context_manager(http: MockAsyncClient):
    async with HTTPClient(client=http) as client:
        assert isinstance(client, HTTPClient)

    assert client.client.is_closed


@pytest.mark.anyio
async def test_aclose(client: HTTPClient, http: MockAsyncClient):
    await client.aclose()

    assert http.is_closed


@pytest.mark.anyio
async def test_get(client: HTTPClient, http: MockAsyncClient):
    http.add_response()

    resp = await client.get("request", Query())

    assert resp.status_code == 200
    assert resp.json() == {"message": "ok"}

    http.mock_get.assert_awaited_once_with("request", params={})


@pytest.mark.anyio
async def test_get_with_id(client: HTTPClient, http: MockAsyncClient):
    http.add_response()

    assert await client.get("request", Query(id=1, fields="test"))

    http.mock_get.assert_awaited_once_with(
        "request/1", params={"fields[request]": "test"}
    )


@pytest.mark.anyio
async def test_get_bad_request_with_error_msg(
    client: HTTPClient, http: MockAsyncClient
):
    http.add_response(400, "bad")
    with pytest.raises(APIError) as excinfo:
        await client.get("request", Query())

    http.mock_get.assert_awaited_once_with("request", params={})

    assert excinfo.value.args == ("Error 400:\nbad\nurl=http://test_url/request",)


@pytest.mark.anyio
async def test_get_bad_request_with_unformatted_error(
    client: HTTPClient, http: MockAsyncClient
):
    http.add_response(400, {"data": "bad"})

    with pytest.raises(APIError) as excinfo:
        await client.get("request", Query())

    http.mock_get.assert_awaited_once_with("request", params={})

    assert excinfo.value.args == (
        "Error 400:\nAn error occurred with the Fount.\nurl=http://test_url/request",
    )


@pytest.mark.anyio
@pytest.mark.parametrize("verbose", (True, False))
async def test_get_pages(
    verbose: bool, http: MockAsyncClient, capsys: pytest.CaptureFixture[str]
):
    http.add_response(data={"data": ["page"]})
    client = HTTPClient(client=http, verbose=verbose)
    res = await client.get_pages("request", Query(page=1, per_page=100), 1)
    captured = capsys.readouterr()

    assert [r.json() for r in res] == [{"data": ["page"]}]
    assert captured.err if verbose else not captured.err
    http.mock_get.assert_awaited_once_with(
        "request", params={"page": 1, "per_page": 100}
    )


@pytest.mark.anyio
async def test_get_pages_fails_warns(http: MockAsyncClient):
    http.add_response(raises=ValueError)
    client = HTTPClient(client=http, retries=0)
    warning_pat = r"Could not get pages: \[Error\(page=1, exception=ValueError\(\)\)\]"

    with pytest.warns(UserWarning, match=warning_pat):  # warns from get request
        await client.get_pages("request", Query(per_page=100), 1)


@pytest.mark.anyio
async def test_get_pages_fails_raises(http: MockAsyncClient):
    http.add_response(raises=ValueError)
    client = HTTPClient(client=http, retries=0, on_errors="raise")

    with pytest.raises(ValueError):  # raised from get request
        await client.get_pages("request", Query(per_page=100), 1)


@pytest.mark.anyio
async def test_query(client: HTTPClient, http: MockAsyncClient):
    http.default_response = http.build_response(data=sample_data([{}]))

    assert len(tuple(await client.query("request", Query()))) == 20  # 2000 / 100
    assert http.mock_get.call_args_list[:3] == [
        mock.call("request", params={"per_page": 1}),  # handshake
        mock.call("request", params={"page": 1, "per_page": 100}),  # full request
        mock.call("request", params={"page": 2, "per_page": 100}),  # full request
    ]
    assert http.mock_get.call_args_list[-1] == mock.call(
        "request", params={"page": 20, "per_page": 100}
    )


@pytest.mark.anyio
async def test_query_per_page(client: HTTPClient, http: MockAsyncClient):
    http.default_response = http.build_response(data=sample_data([{"a": 1}]))

    # tot: 2000, per_page: 25 = 80 pages
    assert len(tuple(await client.query("request", Query(per_page=25)))) == 80


@pytest.mark.anyio
async def test_query_one_page(client: HTTPClient, http: MockAsyncClient):
    http.add_response(data=sample_data([{"t": 1}], total=1, on_page=1))

    # should be a list of dictionaries
    assert list(await client.query("request", Query())) == [{"t": 1}]
    http.mock_get.assert_awaited_once()


@pytest.mark.anyio
async def test_query_no_results(client: HTTPClient, http: MockAsyncClient):
    http.add_response(data=sample_data({}))

    with pytest.raises(DataNotFoundError) as excinfo:
        await client.query("request", Query())

    http.mock_get.assert_awaited_once()
    assert excinfo.value.args[0] == "Your query returned no results."


@pytest.mark.anyio
async def test_query_by_id(client: HTTPClient, http: MockAsyncClient):
    http.add_response(data=sample_data({"t": 1}))

    assert list(await client.query("request", Query(id=1))) == [{"t": 1}]
    http.mock_get.assert_awaited_once()


@pytest.mark.anyio
async def test_query_rate_limit(client: HTTPClient, http: MockAsyncClient):
    http.default_response = rate_limited_response()

    with pytest.raises(RateLimitExceededError) as excinfo:
        await client.query("request", Query())

    http.mock_get.assert_awaited_once()
    assert excinfo.value.args[0] == (
        "Number of pages (20) for this request "
        "exceeds the rate limit (1, "
        "total=500)."
    )


def test_calculate_pages_return_max():
    # 100 / 9 = 11 pages, but because max=10, returns 10
    assert _calculate_pages(None, 9, 10, 100) == 10


@pytest.mark.parametrize("max_pages", (None, 100))
def test_calculate_pages_return_total(max_pages: Optional[int]):
    assert _calculate_pages(None, 50, max_pages, 100) == 2  # 100 / 50 = 2 pages


def test_calculate_pages_starting_page():
    # 100 / 10 = 10 pages, but because (start) page=2, returns 9 (2->10)
    assert _calculate_pages(2, 10, 100, 100) == 9


def test_calculate_pages_starting_page_is_one():
    # 100 / 10 = 10 pages, but because (start) page=2, returns 9 (2->10)
    assert _calculate_pages(1, 10, 100, 100) == 10
