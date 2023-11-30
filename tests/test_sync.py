# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=protected-access

import asyncio
from typing import Any, Dict
from unittest import mock

import pytest

from bavapi import sync
from bavapi.query import Query

from .helpers import wraps


@mock.patch("bavapi.sync.asyncio.new_event_loop", return_value=asyncio.new_event_loop())
def test_coro_new_loop(mock_new_loop: mock.AsyncMock):
    @sync._coro
    async def mock_func():
        pass

    with mock.patch(
        "bavapi.sync.asyncio.get_event_loop_policy", wraps=wraps(raises=RuntimeError)
    ) as mock_get_loop:
        mock_func()

    mock_get_loop.assert_called_once()
    mock_new_loop.assert_called_once()


@mock.patch("bavapi.sync.patch_loop")
@mock.patch("bavapi.sync.running_in_jupyter", return_value=True)
def test_coro_jupyter(mock_running_in_jupyter: mock.Mock, mock_patch_loop: mock.Mock):
    @sync._coro
    async def mock_func():
        pass

    mock_func()

    mock_patch_loop.assert_called_once()
    mock_running_in_jupyter.assert_called_once()


def test_raw_query(mock_async_client: mock.MagicMock):
    with mock.patch("bavapi.sync.Client.raw_query", wraps=wraps()) as mock_raw_query:
        sync.raw_query("TOKEN", "companies", Query(), timeout=10.0, retries=4)

    mock_raw_query.assert_called_with("companies", Query())
    mock_async_client.assert_called_once()


@pytest.mark.parametrize(
    ("endpoint", "filters"),
    (
        ("audiences", {}),
        ("brand_metrics", {}),
        ("brand_metric_groups", {}),
        ("brands", {}),
        ("brandscape_data", {"studies": 1}),
        ("categories", {}),
        ("collections", {}),
        ("sectors", {}),
        ("studies", {}),
    ),
)
def test_function(
    endpoint: str, filters: Dict[str, Any], mock_async_client: mock.MagicMock
):
    with mock.patch(f"bavapi.sync.Client.{endpoint}", wraps=wraps()) as mock_endpoint:
        getattr(sync, endpoint)("TOKEN", filters=filters, timeout=10.0, retries=4)

    mock_endpoint.assert_called_once()
    mock_async_client.assert_called_once()
