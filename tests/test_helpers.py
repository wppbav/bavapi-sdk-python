# pylint: disable=missing-module-docstring, missing-function-docstring

import httpx
import pytest

from bavapi.query import Query
from tests.helpers import MockAsyncClient, MockHTTPClient, wraps


def test_wraps():
    wrapped = wraps(1)
    assert wrapped() == 1


def test_wraps_raises():
    wrapped = wraps(raises=ValueError)
    with pytest.raises(ValueError):
        wrapped()


def test_mock_async_client_build_response_str_data():
    response = MockAsyncClient.build_response()

    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
    assert response.headers["x-ratelimit-remaining"] == "500"
    assert response.headers["x-ratelimit-limit"] == "500"


def test_mock_async_client_build_response_json_data():
    response = MockAsyncClient.build_response(data={"test": 1})

    assert response.status_code == 200
    assert response.json() == {"test": 1}
    assert response.headers["x-ratelimit-remaining"] == "500"
    assert response.headers["x-ratelimit-limit"] == "500"


def test_mock_async_client_build_response_custom_headers():
    response = MockAsyncClient.build_response(headers={"test": "1"})

    assert response.status_code == 200
    assert response.headers["test"] == "1"


def test_mock_async_client_add_response():
    mock_client = MockAsyncClient()

    mock_client.add_response(raises=ValueError)

    res = mock_client.responses[0]

    assert res.value.status_code == 200
    assert res.exc == ValueError


@pytest.mark.anyio
async def test_mock_async_client_context_manager():
    mock_client = MockAsyncClient()

    with mock_client as mc:
        mc.add_response()

        assert mc.responses

        await mc.get("str")

    assert not mock_client.responses
    mock_client.mock_get.assert_awaited_once_with("str")


def test_mock_async_client_warns_if_not_called_and_added_response():
    mock_client = MockAsyncClient()

    with pytest.warns(UserWarning):
        with mock_client as mc:
            mc.add_response()

            assert mc.responses

    assert not mock_client.responses


def test_mock_async_client_no_added_response():
    mock_client = MockAsyncClient()

    with mock_client:
        pass

    assert not mock_client.responses


@pytest.mark.anyio
async def test_mock_async_client_mocked_async_with():
    mock_client = MockAsyncClient()

    async with mock_client as mc:
        assert not mc.is_closed

    assert mock_client.is_closed


@pytest.mark.anyio
async def test_mock_async_client_get():
    mock_client = MockAsyncClient()
    mock_client.add_response()

    response: httpx.Response = await mock_client.get("test")

    assert response.request.url == "http://test_url/test"
    mock_client.mock_get.assert_awaited_once_with("test")


@pytest.mark.anyio
async def test_mock_async_client_get_default():
    mock_client = MockAsyncClient()

    assert await mock_client.get("test")
    mock_client.mock_get.assert_awaited_once_with("test")


@pytest.mark.anyio
async def test_mock_async_client_get_with_exc():
    mock_client = MockAsyncClient()
    mock_client.add_response(raises=ValueError)

    with pytest.raises(ValueError):
        assert await mock_client.get("test")

    mock_client.mock_get.assert_awaited_once_with("test")


@pytest.mark.anyio
async def test_mock_http_client_query():
    mock_client = MockHTTPClient()
    mock_client.add_response(data=[{"a": 1}])

    res = await mock_client.query("test", Query())

    assert list(res) == [{"a": 1}]
    mock_client.mock_query.assert_awaited_once_with("test", Query())
