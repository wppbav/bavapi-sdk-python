# pylint: disable=redefined-outer-name, missing-function-docstring, missing-module-docstring
# pylint: disable=protected-access

import pytest

from bavapi.client import Client
from bavapi.http import HTTPClient


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def client() -> HTTPClient:
    return HTTPClient("test")


@pytest.fixture(scope="session")
def fount(client: HTTPClient) -> Client:
    return Client(client=client)
