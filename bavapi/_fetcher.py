"""Module to handle batching and retrieval of paginated requests.

Provides a `PageFetcher` class with `fetch_page` and `worker` methods to
perform batched paginated requests.

This class keeps track of successful and failed requests with `Result` and `Error`
classes, similar to rust monads, but only used for record-keeping.

An asynchronous "retry" `aretry` function is also provided to handle multiple retries
of requests upon failures and exceptions.
"""

# pylint: disable=broad-exception-caught, too-few-public-methods

# Enabling future annotations for polymorphism on ParamSpec in older Python versions
from __future__ import annotations

import asyncio
import functools
import warnings
from typing import (
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    Literal,
    NamedTuple,
    Optional,
    Protocol,
    TypeVar,
)

from tqdm import tqdm

from bavapi.typing import ParamSpec

T = TypeVar("T")
Q = TypeVar("Q", bound="_Query")
P = ParamSpec("P")

AsyncCallable = Callable[P, Coroutine[None, None, T]]


class _Query(Protocol):
    page: Optional[int]


class Error(NamedTuple):
    """Error record object with failed page number and exception

    Attributes
    ----------
    page : int
        The page number that failed
    exception : Exception
        The exception that was raised during the failure
    """

    page: int
    exception: Exception


# Cannot use Generic NamedTuple until 3.11
# Cannot use dataclass slots until 3.11
# Cannot use generic dataclasses until 3.10
class Result(Generic[T]):
    """Result record object with associated page number and result value

    Attributes
    ----------
    page : int
        The page number that succeeded
    result : T
        The result associated with the successful page retrieval
    """

    __slots__ = ("_page", "_result")

    def __init__(self, page: int, result: T) -> None:
        self._page = page
        self._result = result

    @property
    def page(self) -> int:
        """The page number that succeeded"""
        return self._page

    @property
    def result(self) -> T:
        """The result associated with the successful page retrieval"""
        return self._result


class PageFetcher(Generic[T]):
    """Class for fetching results from a paginated API with support for batching and
    asynchronous workers

    Parameters
    ----------
    pbar : tqdm.tqdm, optional
        Progress bar to use for reporting retrieval progress, default None
    on_errors : Literal["warn", "raise"], optional
        Raise on request failure or warns about failed requests, default `"warn"`
    """

    __slots__ = ("pbar", "on_errors", "_results", "_errors")

    def __init__(
        self,
        pbar: Optional[tqdm] = None,
        on_errors: Literal["warn", "raise"] = "warn",
        *,
        _results: Optional[List[Result[T]]] = None,
        _errors: Optional[List[Error]] = None,
    ) -> None:
        self.pbar = pbar
        self.on_errors = on_errors
        self._results = list(_results) if _results else []
        self._errors = list(_errors) if _errors else []

    async def fetch_page(
        self, func: AsyncCallable[[str, Q], T], endpoint: str, query: Q
    ) -> None:
        """Fetch a page from the API using the specified function, endpoint and query

        Parameters
        ----------
        func : AsyncCallable[[str, Q], T]
            Asynchronous function to be executed
        endpoint : str
            API endpoint of the request
        query : Q
            Query instance to perform the page request

        Raises
        ------
        Exception
            Raises if `on_errors` is set to `"raise"`
        """
        page = query.page or (len(self._results) + 1)
        try:
            self._results.append(Result(page, await func(endpoint, query)))
        except Exception as exc:
            self._errors.append(Error(page, exc))
            if self.on_errors == "raise":
                raise exc

        if self.pbar is not None:
            self.pbar.update()

    async def worker(
        self,
        func: AsyncCallable[[str, Q], T],
        endpoint: str,
        queue: asyncio.Queue[Iterable[Q]],
    ) -> None:
        """Worker coroutine to execute API requests in batches

        Parameters
        ----------
        func : AsyncCallable[[str, Q], T]
            Asynchronous function to be executed
        endpoint : str
            API endpoint of the request
        queue : asyncio.Queue[Iterable[Q]]
            Queue of batches of queries to be executed by the worker(s)
        """
        while not queue.empty():
            batch = await queue.get()

            tasks = [
                asyncio.create_task(self.fetch_page(func, endpoint, query))
                for query in batch
            ]

            await asyncio.gather(*tasks)

    @property
    def errors(self) -> List[Error]:
        """List of errors containing failed page numbers and correspondign exceptions"""
        return sorted(self._errors, key=lambda x: x.page)

    @property
    def results(self) -> List[T]:
        """List of result values, sorted by page number"""
        return [res.result for res in sorted(self._results, key=lambda x: x.page)]

    def warn_if_errors(self) -> None:
        """Warn if any errors have been registered by the instance"""
        if self._errors:
            warnings.warn(f"Could not get pages: {self._errors}", stacklevel=4)


def aretry(
    func: AsyncCallable[P, T], retries: int = 3, delay: float = 0
) -> AsyncCallable[P, T]:
    """Retry an asynchronous function upon failure a number of times.

    If the number of retries is exceeded, the last exception will be raised.

    Parameters
    ----------
    func : AsyncCallable[P, T]
        The asynchronous function to retry
    retries : int, optional
        Number of retries to attempt, default 3

        If the value is 0 or negative, the function will only be tried once
    delay : float, optional
        Time to wait between retries, default 0
    Returns
    -------
    AsyncCallable[P, T]
        Wrapper for asynchronous function that will retry upon failure

    Raises
    ------
    Exception
        If all retry attempts failed, the last exception will be raised
    """

    # pylint: disable=no-member
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for retry_count in range(retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                if retry_count == retries:
                    raise exc
                await asyncio.sleep(delay)

        # if retries < 0
        return await func(*args, **kwargs)

    return wrapper
