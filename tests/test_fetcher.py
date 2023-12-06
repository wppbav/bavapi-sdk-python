# pylint: disable=missing-function-docstring, missing-module-docstring, missing-class-docstring
# pylint: disable=protected-access

import asyncio
import warnings
from dataclasses import dataclass
from typing import Optional
from unittest import mock

import pytest
from tqdm import tqdm

from bavapi._fetcher import Error, PageFetcher, aretry


@dataclass
class Q:
    page: Optional[int]


def test_init():
    fetcher = PageFetcher()
    assert isinstance(fetcher.errors, list)
    assert isinstance(fetcher.results, list)

    lst = [1]

    fetcher = PageFetcher(_results=lst, _errors=lst)  # type: ignore

    assert fetcher._errors == lst
    assert fetcher._results == lst


@pytest.mark.anyio
async def test_fetch_page():
    async def _test(_str: str, _query: Q):
        return 1

    fetcher: PageFetcher[int] = PageFetcher()
    await fetcher.fetch_page(_test, "test_endpoint", Q(1))

    assert len(fetcher.results) == 1
    assert fetcher.results[0] == 1
    assert not fetcher.errors


@pytest.mark.anyio
async def test_fetch_page_fails():
    async def _test(_str: str, _query: Q):
        raise ValueError("test error")

    fetcher = PageFetcher()
    await fetcher.fetch_page(_test, "test_endpoint", Q(1))

    assert not fetcher.results
    assert len(fetcher.errors) == 1

    page, exc = fetcher._errors[0]
    assert page == 1
    assert isinstance(exc, ValueError)
    assert exc.args == ("test error",)


@pytest.mark.anyio
async def test_fetch_page_with_pbar():
    async def _test(_str: str, _query: Q):
        return 1

    mock_tqdm = mock.MagicMock(spec=tqdm)

    fetcher = PageFetcher(mock_tqdm)
    await fetcher.fetch_page(_test, "test_endpoint", Q(1))

    mock_tqdm.update.assert_called_once()


@pytest.mark.anyio
async def test_fetch_page_with_pbar_fails():
    async def _test(_str: str, _query: Q):
        raise ValueError("test error")

    mock_tqdm = mock.MagicMock(spec=tqdm)

    fetcher = PageFetcher(mock_tqdm)
    await fetcher.fetch_page(_test, "test_endpoint", Q(1))

    mock_tqdm.update.assert_called_once()


@pytest.mark.anyio
async def test_worker():
    fetcher = PageFetcher()
    queue = asyncio.Queue()

    queue.put_nowait([Q(i) for i in range(1, 11)])

    async def _test(_str: str, _query: Q):
        return 1

    await fetcher.worker(_test, "test endpoint", queue)

    assert fetcher.results == [1] * 10


def test_warn_if_errors_warns():
    fetcher = PageFetcher(_errors=[Error(1, ValueError())])
    warning_pat = r"Could not get pages: \[Error\(page=1, exception=ValueError\(\)\)\]"
    with pytest.warns(UserWarning, match=warning_pat):
        fetcher.warn_if_errors()


def test_warn_if_errors_no_errors():
    fetcher = PageFetcher(_errors=[])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fetcher.warn_if_errors()


@pytest.mark.anyio
async def test_aretry():
    mock_coro = mock.AsyncMock()
    retry_func = aretry(mock_coro)

    await retry_func()

    assert mock_coro.await_count == 1


@pytest.mark.anyio
async def test_aretry_fails():
    mock_coro = mock.AsyncMock()
    mock_coro.side_effect = [ValueError, None]
    retry_func = aretry(mock_coro, 1)

    await retry_func()

    assert mock_coro.await_count == 2


@pytest.mark.anyio
async def test_aretry_fails_and_raises():
    mock_coro = mock.AsyncMock()
    mock_coro.side_effect = [ValueError, ValueError]
    retry_func = aretry(mock_coro, 1)

    with pytest.raises(ValueError):
        await retry_func()

    assert mock_coro.await_count == 2


@pytest.mark.anyio
async def test_aretry_no_iter():
    mock_coro = mock.AsyncMock()
    retry_func = aretry(mock_coro, -1)

    await retry_func()

    assert mock_coro.await_count == 1
