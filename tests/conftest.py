# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access

from typing import Iterator
from unittest import mock

import httpx
import pytest

from bavapi.client import Client
from bavapi.http import HTTPClient
from tests.helpers import mock_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def http_client():
    return httpx.AsyncClient(app=mock_app)


@pytest.fixture(scope="session")
def client(http_client: httpx.AsyncClient) -> HTTPClient:
    return HTTPClient(client=http_client)


@pytest.fixture(scope="session")
def fount(client: HTTPClient) -> Client:
    return Client(client=client)


@pytest.fixture
def mock_async_client() -> Iterator[httpx.AsyncClient]:
    async_client = httpx.AsyncClient(app=mock_app)
    with mock.patch("httpx.AsyncClient", return_value=async_client) as mock_client:
        yield mock_client
