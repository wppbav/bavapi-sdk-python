# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access

from typing import Iterator
from unittest import mock

import httpx
import pytest

from bavapi.client import Client
from bavapi.http import HTTPClient
from tests.helpers import MockAsyncClient, MockHTTPClient, mock_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def http_instance() -> MockAsyncClient:
    return MockAsyncClient()


@pytest.fixture
def http(http_instance: MockAsyncClient) -> Iterator[MockAsyncClient]:
    with http_instance as instance:
        yield instance


@pytest.fixture(scope="session")
def client(http_instance: MockAsyncClient) -> HTTPClient:
    return HTTPClient(client=http_instance)  # type: ignore


@pytest.fixture(scope="session")
def http_client_instance():
    return MockHTTPClient()


@pytest.fixture
def http_client(http_client_instance: MockHTTPClient) -> Iterator[MockAsyncClient]:
    with http_client_instance as instance:
        yield instance


@pytest.fixture(scope="session")
def fount(http_client_instance: MockHTTPClient) -> Client:
    return Client(client=http_client_instance)


@pytest.fixture
def mock_async_client() -> Iterator[httpx.AsyncClient]:
    async_client = httpx.AsyncClient(app=mock_app)
    with mock.patch("httpx.AsyncClient", return_value=async_client) as mock_client:
        yield mock_client
