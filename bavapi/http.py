"""Class for interacting with paginated APIs over HTTP."""

# pylint: disable=too-many-arguments, too-few-public-methods

import asyncio
import math
from json import JSONDecodeError
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import httpx
from tqdm.asyncio import tqdm

from bavapi.exceptions import APIError, DataNotFoundError, RateLimitExceededError
from bavapi.typing import BaseParamsMapping, JSONData, JSONDict

if TYPE_CHECKING:
    from types import TracebackType

__all__ = ("HTTPClient",)


class _Query(Protocol):
    """Protocol for Query objects with pagination support"""

    item_id: Optional[int]
    max_pages: Optional[int]
    per_page: Optional[int]
    page: Optional[int]

    def to_params(self, endpoint: str) -> BaseParamsMapping:
        """HTTP-compatible params dictionary"""
        raise NotImplementedError

    def paginated(
        self, n_pages: int, per_page: Optional[int] = None
    ) -> Iterator["_Query"]:
        """Yields Query objects with page parameters for paginated queries"""
        raise NotImplementedError

    def is_single_page(self) -> bool:
        """True if query is for a single page, False for multiple"""
        raise NotImplementedError

    def with_page(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> "_Query":
        """Returns Query with new pagination parameters"""
        raise NotImplementedError


class HTTPClient:
    """HTTP client for interacting with paginated API.

    Parameters
    ----------
    base_url : str
        The base URL of the API.
    per_page : int, optional
        Default number of entries per page, by default 100
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 5.0
    verify : bool or str, optional
        Verify SSL credentials, by default True

        Also accepts a path string to an SSL certificate file.
    headers : dict[str, str], optional
        Collection of headers to send with each request, by default None
    client : httpx.AsyncClient, optional
        Authenticated `httpx.AsyncClient`, by default None
    verbose : bool, optional
        Set to False to disable progress bar, by default True
    """

    __slots__ = ("client", "per_page", "verbose")

    C = TypeVar("C", bound="HTTPClient")

    @overload
    def __init__(
        self,
        base_url: str,
        per_page: int = 100,
        timeout: float = 5.0,
        verify: Union[bool, str] = True,
        *,
        headers: Optional[Dict[str, str]] = None,
        verbose: bool = True,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        client: httpx.AsyncClient = ...,
        per_page: int = 100,
        verbose: bool = True,
    ) -> None:
        ...

    def __init__(
        self,
        base_url: str = "",
        per_page: int = 100,
        timeout: float = 5.0,
        verify: Union[bool, str] = True,
        *,
        headers: Optional[Dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
        verbose: bool = True,
    ) -> None:
        self.per_page = per_page
        self.verbose = verbose

        if client is not None:
            self.client = client
        else:
            self.client = httpx.AsyncClient(
                headers=headers,
                timeout=timeout,
                verify=verify,
                base_url=base_url,
            )

    async def __aenter__(self: C) -> C:
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: "Optional[TracebackType]" = None,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def aclose(self) -> None:
        """Asynchronously close all client connections."""
        return await self.client.aclose()

    async def get(self, endpoint: str, query: _Query) -> httpx.Response:
        """Perform GET request on the given endpoint.

        Parameters
        ----------
        endpoint : str
            Path to endpoint.
        query : Query
            Request parameters.

        Returns
        -------
        httpx.Response
            Requested response object.

        Raises
        ------
        APIError
            If request fails.
        """
        url = f"{endpoint}/{query.item_id}" if query.item_id is not None else endpoint

        resp = await self.client.get(url, params=query.to_params(endpoint))

        if resp.status_code != 200:
            try:
                message = resp.json()["message"]
            except (KeyError, JSONDecodeError):
                message = "An error occurred with the Fount."

            raise APIError(f"Error {resp.status_code}:\n{message}\nurl={resp.url}")

        return resp

    async def get_pages(
        self, endpoint: str, query: _Query, n_pages: int
    ) -> List[httpx.Response]:
        """Perform GET requests for a given number of pages on an endpoint.

        Parameters
        ----------
        endpoint : str
            Path to endpoint.
        query : Query
            Request parameters.
        n_pages : int
            Number of pages to request.

        Returns
        -------
        list[httpx.Response]
            List of response objects.
        """
        tasks = [
            asyncio.create_task(self.get(endpoint, page))
            for page in query.paginated(n_pages)
        ]
        try:
            return await tqdm.gather(
                *tasks, desc=f"{endpoint} query", disable=not self.verbose
            )
        except Exception as exc:
            for task in tasks:
                task.cancel()

            raise exc

    async def query(self, endpoint: str, query: _Query) -> Iterator[JSONDict]:
        """Perform a paginated GET request on the given endpoint.

        Parameters
        ----------
        endpoint : str
            Path to endpoint.
        query : Query
            Request parameters.

        Returns
        -------
        Iterator[JSONDict]
            An iterator of JSONDict objects.

        Raises
        ------
        APIError
            If any request fails.
        DataNotFoundError
            If response data is empty.
        RateLimitExceededError
            If response would exceed the rate limit.
        """
        per_page = query.per_page or self.per_page
        resp = await self.get(endpoint, query.with_page(per_page=per_page))

        payload: Dict[str, JSONData] = resp.json()
        data: JSONData = payload["data"]

        if not data:
            raise DataNotFoundError("Your query returned no results.")

        if isinstance(data, dict):
            return iter((data,))

        meta = cast(JSONDict, payload["meta"])
        total = cast(int, meta["total"])

        if query.is_single_page() or len(data) == total:
            return iter(data)

        n_pages = _calculate_pages(query.page, per_page, query.max_pages, total)

        if n_pages > (limit_remaining := int(resp.headers["x-ratelimit-remaining"])):
            raise RateLimitExceededError(
                f"Number of pages ({n_pages}) for this request "
                f"exceeds the rate limit ({limit_remaining}, "
                f"total={resp.headers['x-ratelimit-limit']})."
            )

        pages = await self.get_pages(
            endpoint, query.with_page(per_page=per_page), n_pages
        )

        return (i for page in pages for i in page.json()["data"])


def _calculate_pages(
    page: Optional[int], per_page: int, max_pages: Optional[int], total: int
) -> int:
    total_pages = math.ceil(total / per_page) - (page - 1 if page else 0)
    if max_pages and max_pages <= total_pages:
        return max_pages
    return total_pages
