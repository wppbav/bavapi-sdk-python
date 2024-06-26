"""
bavapi
------
Python consumer for the WPPBAV Fount API.

With `bavapi` you can access the full BAV data catalog, the largest and
most comprehensive database of brand data in the world.

Queries are validated thanks to `pydantic` and retrieved asynchronously
through to the `httpx` package.

For more information, go to the WPPBAV Fount website at <https:/fount.wppbav.com>.

Examples
--------
Use top-level endpoint functions for quickly downloading BAV data:

>>> import bavapi
>>> res = bavapi.brands("TOKEN", name="Facebook")

For more advanced usage (and async compatibility), use the `bavapi.Client` class:

>>> import bavapi
>>> async with bavapi.Client("TOKEN") as bav:
...     result = await bav.brands(name="Facebook")
"""

# pylint: disable=R0801

from bavapi import filters
from bavapi import tools
from bavapi.client import Client
from bavapi.exceptions import APIError, DataNotFoundError, RateLimitExceededError
from bavapi.query import Query
from bavapi.sync import (
    audiences,
    audience_groups,
    brand_metric_groups,
    brand_metrics,
    brands,
    brandscape_data,
    categories,
    cities,
    collections,
    companies,
    countries,
    raw_query,
    regions,
    sectors,
    studies,
    years,
)

__all__ = (
    "audiences",
    "audience_groups",
    "brand_metrics",
    "brand_metric_groups",
    "brands",
    "brandscape_data",
    "categories",
    "cities",
    "collections",
    "companies",
    "countries",
    "regions",
    "raw_query",
    "sectors",
    "studies",
    "years",
    "Client",
    "Query",
    "filters",
    "tools",
    "APIError",
    "DataNotFoundError",
    "RateLimitExceededError",
)
