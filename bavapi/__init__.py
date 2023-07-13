"""
bavapi
------
Python consumer for the WPPBAV Fount API.

With `bavapi` you can access the full BAV data catalog, the largest and
most comprehensive database of brand data in the world.

Queries are validated thanks to `pydantic` and retrieved asynchronously
through to the `httpx` package.

For more information, go to the WPPBAV Fount website at <https:/fount.wppbav.com>.

Example usage
-------------

>>> import bavapi
>>> async with bavapi.Client("API_TOKEN") as client:
...     result = await client.brands(name="Facebook")
"""

from importlib.metadata import PackageNotFoundError, version

from bavapi import filters
from bavapi.client import Client
from bavapi.exceptions import APIError, DataNotFoundError, RateLimitExceededError
from bavapi.query import Query
from bavapi.sync import audiences, brands, brandscape_data, raw_query, studies

__all__ = (
    "audiences",
    "brands",
    "brandscape_data",
    "raw_query",
    "studies",
    "Client",
    "Query",
    "filters",
    "APIError",
    "DataNotFoundError",
    "RateLimitExceededError",
)

try:
    __version__ = version(__package__ or __name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "not_found"
