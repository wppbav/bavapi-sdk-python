# pylint: disable=broad-exception-caught, too-few-public-methods

import asyncio
import functools
from typing import (
    Callable,
    Coroutine,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Optional,
    ParamSpec,
    Protocol,
    TypeVar,
)

from tqdm import tqdm

T = TypeVar("T")
Q = TypeVar("Q", bound="_Query")
P = ParamSpec("P")

AsyncCallable = Callable[P, Coroutine[None, None, T]]


class _Query(Protocol):
    page: Optional[int]


class ErrorRecord(NamedTuple):
    page: int
    exception: Exception


class ResultRecord(NamedTuple, Generic[T]):
    page: int
    result: T


class PageFetcher(Generic[T]):
    __slots__ = ("pbar", "_results", "_errors")

    def __init__(
        self,
        pbar: Optional[tqdm] = None,
        results: Optional[List[ResultRecord[T]]] = None,
        errors: Optional[List[ErrorRecord]] = None,
    ) -> None:
        self.pbar = pbar
        self._results = list(results) if results else []
        self._errors = list(errors) if errors else []

    async def fetch_page(
        self, func: AsyncCallable[[str, Q], T], endpoint: str, query: Q
    ) -> None:
        page = query.page or (len(self._results) + 1)
        try:
            self._results.append(ResultRecord(page, await func(endpoint, query)))
        except Exception as exc:
            self._errors.append(ErrorRecord(page, exc))

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
    def errors(self) -> List[int]:
        return [page for page, _ in self._errors]

    @property
    def results(self) -> List[T]:
        return [res for _, res in sorted(self._results, key=lambda x: x.page)]


def aretry(func: AsyncCallable[P, T], retries: int = 3) -> AsyncCallable[P, T]:
    # pylint: disable=no-member
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  # type: ignore[ret-type]
        for retry_count in range(retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                if retry_count == retries:
                    raise exc
                await asyncio.sleep(1)

    return wrapper
