# pylint: disable=missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access, redefined-outer-name

from dataclasses import asdict, dataclass
from typing import Dict, Optional
from unittest import mock

import httpx
import pytest

from bavapi.exceptions import APIError, DataNotFoundError, RateLimitExceededError
from bavapi.http import HTTPClient
from bavapi.query import Query
from bavapi.typing import JSONData, JSONDict

from .helpers import wraps

# HELPERS


@dataclass
class QueryResult:
    """Model for WPPBAV Fount query results"""

    data: JSONData
    links: Dict[str, str]
    meta: JSONDict

    def dict(self) -> JSONDict:
        return asdict(self)


def response(
    status_code: int = 200,
    message: str = "ok",
    *,
    json: Optional[JSONData] = None,
    request_url: str = "http://test_url/request",
    headers: Optional[httpx.Headers] = None,
) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json if json is not None else {"message": message},
        request=httpx.Request("GET", url=request_url),
        headers=headers
        or httpx.Headers({"x-ratelimit-remaining": "500", "x-ratelimit-limit": "500"}),
    )


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


def empty_response() -> httpx.Response:
    return response(json=sample_data([{}]))


def rate_limited_response() -> httpx.Response:
    return response(
        200,
        json=sample_data([{}]),
        headers=httpx.Headers(
            {"x-ratelimit-remaining": "1", "x-ratelimit-limit": "500"}
        ),
    )


# TESTS


def test_client_init_with_client():
    httpx_client = httpx.AsyncClient()

    client = HTTPClient(client=httpx_client)

    assert client.client is httpx_client


@pytest.mark.anyio
async def test_context_manager():
    client = HTTPClient()
    async with client as client:
        assert isinstance(client, HTTPClient)

    assert client.client.is_closed


@pytest.mark.anyio
@mock.patch("bavapi.http.httpx.AsyncClient.aclose", wraps=wraps())
async def test_aclose(mock_aclose: mock.AsyncMock, client: HTTPClient):
    await client.aclose()

    mock_aclose.assert_called_once()


@pytest.mark.anyio
@mock.patch("bavapi.http.httpx.AsyncClient.get", wraps=wraps(response()))
async def test_get(mock_get: mock.AsyncMock, client: HTTPClient):
    resp = await client.get("request", Query())

    assert resp.status_code == 200
    assert resp.json() == {"message": "ok"}

    mock_get.assert_awaited_once_with("request", params={})


@pytest.mark.anyio
@mock.patch("bavapi.http.httpx.AsyncClient.get", wraps=wraps(response()))
async def test_get_with_id(mock_get: mock.AsyncMock, client: HTTPClient):
    assert await client.get("request", Query(id=1))

    mock_get.assert_awaited_once_with("request/1")


@pytest.mark.anyio
@mock.patch("bavapi.http.httpx.AsyncClient.get", wraps=wraps(response(400, "bad")))
async def test_get_bad_request_with_error_msg(
    mock_get: mock.AsyncMock, client: HTTPClient
):
    with pytest.raises(APIError) as excinfo:
        await client.get("request", Query())

    mock_get.assert_awaited_once_with("request", params={})

    assert excinfo.value.args == ("Error 400:\nbad\nurl=http://test_url/request",)


@pytest.mark.anyio
@mock.patch(
    "bavapi.http.httpx.AsyncClient.get",
    wraps=wraps(response(400, json={"data": "bad"})),
)
async def test_get_bad_request_with_unformatted_error(
    mock_get: mock.AsyncMock, client: HTTPClient
):
    with pytest.raises(APIError) as excinfo:
        await client.get("request", Query())

    mock_get.assert_awaited_once_with("request", params={})

    assert excinfo.value.args == (
        "Error 400:\nAn error occurred with the Fount.\nurl=http://test_url/request",
    )


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(["page"]))
async def test_get_pages(
    mock_get: mock.AsyncMock, client: HTTPClient, capsys: pytest.CaptureFixture
):
    res = await client.get_pages("request", Query(), 1)
    captured = capsys.readouterr()

    assert res == [["page"]]
    assert captured.err
    mock_get.assert_awaited_once_with("request", Query(page=1, per_page=100))


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(["page"]))
async def test_get_pages_no_pbar(
    mock_get: mock.AsyncMock, capsys: pytest.CaptureFixture
):
    client = HTTPClient("test", verbose=False)
    res = await client.get_pages("request", Query(), 1)
    captured = capsys.readouterr()

    assert res == [["page"]]
    assert not captured.err
    mock_get.assert_awaited_once_with("request", Query(page=1, per_page=100))


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(raises=ValueError))
async def test_get_pages_fails(mock_get: mock.AsyncMock, client: HTTPClient):
    with pytest.raises(ValueError):  # raised from mocked `get` method
        await client.get_pages("request", Query(), 1)

    mock_get.assert_awaited_once()


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get_pages", wraps=wraps([empty_response()]))
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(empty_response()))
async def test_query(
    mock_get: mock.AsyncMock,
    mock_get_pages: mock.AsyncMock,
    client: HTTPClient,
):
    assert len(tuple(await client.query("request", Query()))) == 1

    mock_get.assert_awaited_once_with("request", params=Query())
    mock_get_pages.assert_awaited_once_with("request", Query(), 20)


@pytest.mark.anyio
@mock.patch(
    "bavapi.http.HTTPClient.get_pages",
    wraps=wraps([response(json=sample_data([{"a": 1}]))]),
)
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(empty_response()))
async def test_query_per_page(
    mock_get: mock.AsyncMock, mock_get_pages: mock.AsyncMock, client: HTTPClient
):
    assert len(tuple(await client.query("request", Query(per_page=25)))) == 1

    mock_get.assert_awaited_once()
    mock_get_pages.assert_awaited_once_with("request", Query(per_page=25), 80)


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get_pages", wraps=wraps())
@mock.patch(
    "bavapi.http.HTTPClient.get",
    wraps=wraps(response(json=sample_data([{"t": 1}], total=1, on_page=1))),
)
async def test_query_one_page(
    mock_get: mock.AsyncMock, mock_get_pages: mock.AsyncMock, client: HTTPClient
):
    # should be a list of dictionaries
    assert list(await client.query("request", Query())) == [{"t": 1}]

    mock_get.assert_awaited_once()
    mock_get_pages.assert_not_awaited()


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get_pages", wraps=wraps())
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(response(json=sample_data({}))))
async def test_query_no_results(
    mock_get: mock.AsyncMock, mock_get_pages: mock.AsyncMock, client: HTTPClient
):
    with pytest.raises(DataNotFoundError) as excinfo:
        await client.query("request", Query())

    mock_get.assert_awaited_once()
    mock_get_pages.assert_not_awaited()
    assert excinfo.value.args[0] == "Your query returned no results."


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get_pages", wraps=wraps())
@mock.patch(
    "bavapi.http.HTTPClient.get",
    wraps=wraps(response(json=sample_data({"t": 1}))),
)
async def test_query_by_id(
    mock_get: mock.AsyncMock, mock_get_pages: mock.AsyncMock, client: HTTPClient
):
    assert list(await client.query("request", Query(id=1))) == [{"t": 1}]

    mock_get.assert_awaited_once()
    mock_get_pages.assert_not_awaited()


@pytest.mark.anyio
@mock.patch("bavapi.http.HTTPClient.get_pages", wraps=wraps())
@mock.patch("bavapi.http.HTTPClient.get", wraps=wraps(rate_limited_response()))
async def test_query_rate_limit(
    mock_get: mock.AsyncMock, mock_get_pages: mock.AsyncMock, client: HTTPClient
):
    with pytest.raises(RateLimitExceededError) as excinfo:
        await client.query("request", Query())

    mock_get.assert_awaited_once()
    mock_get_pages.assert_not_awaited()
    assert excinfo.value.args[0] == (
        "Number of pages (20) for this request "
        "exceeds the rate limit (1, "
        "total=500)."
    )
