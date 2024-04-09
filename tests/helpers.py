# pylint: disable=missing-module-docstring, missing-function-docstring

import copy
import warnings
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)
from unittest import mock

import httpx

from bavapi.http import _Query
from bavapi.typing import AsyncClientType, JSONData, JSONDict

T = TypeVar("T")
ASGIApp = Callable[..., "ASGIApp"]


def wraps(
    return_value: Optional[T] = None,
    *,
    raises: Optional[Union[Type[Exception], Exception]] = None,
) -> Callable[..., Optional[T]]:
    def _wraps(*_, **__) -> Optional[T]:
        if raises is not None:
            raise raises
        return return_value

    return _wraps


def mock_app(*_, **__) -> ASGIApp:
    ...  # pragma: no cover


@dataclass
class Result(Generic[T]):
    """Generic result type with a generic value and an optional exception"""

    value: T
    exc: Optional[Union[Exception, Type[Exception]]] = None


C = TypeVar("C", bound="MockAsyncClient")


class MockAsyncClient:
    """Mock AsyncClient class for testing.

    Replaces used httpx.AsyncClient methods and functionality
    enabling the inspection of calls performed on the get function.

    Usage
    -----
    1. Create a fixture for the session that returns an instantiated MockClient

    >>> @pytest.fixture(scope="session")
    >>> def mock_client():
    >>>     return MockClient()

    2. Create a fixture that yields the MockClient inside a with block

    >>> @pytest.fixture
    >>> def http(mock_client):
    >>>     with mock_client as c:
    >>>         yield c

    3. Create a fixture that returns the class that contains httpx.AsyncClient:

    >>> @pytest.fixture
    >>> def client(mock_client):
    >>> return HTTPClient(client=mock_client)

    Request the client and the http fixtures to perform method calls and define
    each response values:

    >>> def test_client(client, http):
    >>>     http.add_response(200, "ok")
    >>>     response = client.get("test")
    >>>     http.mock_get.assert_awaited_once_with("test")

    If an exception or exception type is passed as the raises argument to the
    add_response method, the exception will be raised when the get call is performed

    >>> def test_client(client, http):
    >>>     http.add_response(200, "ok", raises=ValueError)
    >>>     with pytest.raises(ValueError):
    >>>         response = client.get("test")  # will raise ValueError
    >>>     http.mock_get.assert_awaited_once_with("test")
    """

    def __init__(
        self,
        responses: Optional[List[Result[httpx.Response]]] = None,
        base_url: str = "http://test_url/",
    ) -> None:
        self.responses = responses or []
        self.base_url = base_url
        self.is_closed: bool = False
        self._it = iter(self.responses)  # can still append to responses after init
        self.get: mock.AsyncMock = mock.AsyncMock(wraps=self._get)
        self.default_response = self.build_response()

    @property
    def mock_get(self) -> mock.AsyncMock:
        """Mock object for the get function"""
        return self.get

    def __enter__(self: C) -> C:
        self.is_closed = False
        self._it = iter(self.responses)
        self.get: mock.AsyncMock = mock.AsyncMock(wraps=self._get)
        return self

    def __exit__(self, *_, **__) -> None:
        return self.close()

    def close(self) -> None:
        self.is_closed = False
        self.default_response = self.build_response()
        responses = self.responses
        self.responses = []
        if not responses:
            return

        try:
            result = next(self._it)
        except StopIteration:
            # self._it should be exhausted at close time
            return

        not_returned = responses[responses.index(result) :]
        warnings.warn(
            "The following responses have not been "
            f"returned ({len(not_returned)}): {not_returned}",
            stacklevel=2,
        )

    async def __aenter__(self: C) -> C:
        self.is_closed = False
        return self

    async def __aexit__(self, *_, **__) -> None:
        return await self.aclose()

    async def aclose(self) -> None:
        self.is_closed = True
        return None

    @staticmethod
    def build_response(
        status_code: int = 200,
        data: Union[str, JSONData] = "ok",
        headers: Optional[Mapping[str, str]] = None,
    ) -> httpx.Response:
        """Build standard HTTP response value

        Parameters
        ----------
        status_code : int, optional
            HTTP status code, by default 200
        data : Union[str, JSONData], optional
            Data to include in the response, by default "ok"

            If the data is of string type, it will be placed in a dictionary under
            the key "message"
        raises : Optional[Union[Exception, Type[Exception]]], optional
            Raise the exception instead of returning data, by default None
        headers : Optional[Mapping[str, str]], optional
            Headers to include in the response, by default None

        Returns
        -------
        httpx.Response
            Response object with applied values
        """
        return httpx.Response(
            status_code,
            json={"message": data} if isinstance(data, str) else data,
            headers=headers
            or httpx.Headers(
                {"x-ratelimit-remaining": "500", "x-ratelimit-limit": "500"}
            ),
        )

    def add_response(
        self,
        status_code: int = 200,
        data: Union[str, JSONData] = "ok",
        raises: Optional[Union[Exception, Type[Exception]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        """Add response to the queue for mocked return values

        Parameters
        ----------
        status_code : int, optional
            HTTP status code, by default 200
        data : Union[str, JSONData], optional
            Data to include in the response, by default "ok"

            If the data is of string type, it will be placed in a dictionary under
            the key "message"
        raises : Optional[Union[Exception, Type[Exception]]], optional
            Raise the exception instead of returning data, by default None
        headers : Optional[Mapping[str, str]], optional
            Headers to include in the response, by default None
        """
        self.responses.append(
            Result(self.build_response(status_code, data, headers), raises)
        )

    async def _get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        **_,
    ) -> httpx.Response:
        try:
            result = next(self._it)
        except StopIteration:
            result = Result(self.default_response)
        else:
            # check exception if next returned a result, otherwise skip check
            if result.exc is not None:
                raise result.exc

        response = result.value

        response.request = httpx.Request(
            "GET", self.base_url + url, params=params, headers=headers
        )
        return response


H = TypeVar("H", bound="MockHTTPClient")


class MockHTTPClient(MockAsyncClient):
    per_page: int = 100
    verbose: bool = True
    batch_size: int = 10
    n_workers: int = 2
    retries: int = 3
    on_errors: Literal["warn", "raise"] = "warn"
    client: AsyncClientType

    def __init__(
        self,
        responses: Optional[List[Result[httpx.Response]]] = None,
        base_url: str = "http://test_url/",
    ) -> None:
        super().__init__(responses, base_url)
        self.query = mock.AsyncMock(wraps=self._query)
        self.client = copy.copy(self)

    @property
    def mock_query(self) -> mock.AsyncMock:
        """Mock object for the query function"""
        return self.query

    def __enter__(self: H) -> H:
        self.query: mock.AsyncMock = mock.AsyncMock(wraps=self._query)
        return super().__enter__()

    async def _query(
        self,
        endpoint: str,
        query: _Query,
    ) -> Iterator[JSONDict]:
        return iter(
            (await self._get(endpoint, params=query.to_params(endpoint))).json(),
        )
