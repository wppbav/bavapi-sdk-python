# pylint: disable=broad-exception-caught, too-few-public-methods

# Enabling future annotations to enable polymorphism on ParamSpec
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
    page: int
    exception: Exception


# Cannot use Generic NamedTuple until 3.11
# Cannot use dataclass slots until 3.11
# Cannot use generic dataclasses until 3.10
class Result(Generic[T]):
    __slots__ = ("_page", "_result")

    def __init__(self, page: int, result: T) -> None:
        self._page = page
        self._result = result

    @property
    def page(self) -> int:
        return self._page

    @property
    def result(self) -> T:
        return self._result


class PageFetcher(Generic[T]):
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
        while not queue.empty():
            batch = await queue.get()

            tasks = [
                asyncio.create_task(self.fetch_page(func, endpoint, query))
                for query in batch
            ]

            await asyncio.gather(*tasks)

    @property
    def errors(self) -> List[Error]:
        return sorted(self._errors, key=lambda x: x.page)

    @property
    def results(self) -> List[T]:
        return [res.result for res in sorted(self._results, key=lambda x: x.page)]

    def warn_if_errors(self) -> None:
        if self._errors:
            warnings.warn(f"Could not get pages: {self._errors}", stacklevel=4)


def aretry(
    func: AsyncCallable[P, T], retries: int = 3, delay: float = 0
) -> AsyncCallable[P, T]:
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
