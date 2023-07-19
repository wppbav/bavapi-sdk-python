"""
Convenience functions to perform queries to the Fount synchronously.

Can be used directly without `asyncio`.

Meant for experimentation, Jupyter notebooks, one-off scripts, etc.

Use `bavapi.Client` for more advanced usage and performance benefits.
"""

# pylint: disable=redefined-outer-name, too-many-arguments

import asyncio
import functools
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    List,
    Literal,
    Optional,
    TypeVar,
)

from bavapi import filters as _filters
from bavapi.client import Client, OptionalFiltersOrMapping
from bavapi.jupyter import patch_loop, running_in_jupyter
from bavapi.query import Query
from bavapi.typing import BaseListOrValues, JSONDict, OptionalListOr

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

if TYPE_CHECKING:
    from pandas import DataFrame

__all__ = ("raw_query", "audiences", "brands", "brandscape_data", "studies")

T = TypeVar("T")
P = ParamSpec("P")
F = TypeVar("F", bound=_filters.FountFilters)


def _coro(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        try:
            loop = asyncio.get_event_loop_policy().get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        coro = func(*args, **kwargs)

        if running_in_jupyter():
            patch_loop(loop)

        return loop.run_until_complete(coro)

    return wrapper


@_coro
async def raw_query(token: str, endpoint: str, params: Query[F]) -> List[JSONDict]:
    """Perform a raw GET query to the Fount API, returning the response JSON data
    instead of a `pandas` DataFrame.

    Parameters
    ----------
    token : str
        Fount API token
    endpoint : str
        Endpoint name
    params : Query
        Query `pydantic` model with query parameters.

    Returns
    -------
    list[dict[str, Any]]
        List of JSON response data
    """

    async with Client(token) as fount:
        return await fount.raw_query(endpoint, params)


@_coro
async def audiences(
    token: str,
    name: Optional[str] = None,
    audience_id: Optional[int] = None,
    active: Literal[0, 1] = 0,
    inactive: Literal[0, 1] = 0,
    public: Literal[0, 1] = 0,
    private: Literal[0, 1] = 0,
    groups: OptionalListOr[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.AudiencesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    **kwargs: BaseListOrValues,
) -> "DataFrame":
    """Query the Fount `audiences` endpoint.

    Parameters
    ----------
    token : str
        Fount API token
    name : str, optional
        Search audiences by name, by default None
    audience_id : int, optional
        Fount audience ID, by default None

        If an audience ID is provided, only that audience will be returned
    active : Literal[0, 1]
        Return active audiences only if set to `1`, by default 0
    inactive : Literal[0, 1]
        Return inactive audiences only if set to `1`, by default 0
    public : Literal[0, 1]
        Return active audiences only if set to `1`, by default 0
    private : Literal[0, 1]
        Return inactive audiences only if set to `1`, by default 0
    groups : int or list[int], optional
        Audience group ID or list of audience group IDs, by default None
    filters : AudiencesFilters or dict of filters, optional
        AudiencesFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, by default None
    per_page : int, optional
        Number of results per page, by default None
    max_pages : int, optional
        Max number of results to return, by default None
    sort : str, optional
        Sort response by field, by default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brands` endpoint results
    """

    async with Client(token) as fount:
        return await fount.audiences(
            name,
            audience_id,
            active,
            inactive,
            public,
            private,
            groups,
            filters=filters,
            fields=fields,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def brands(
    token: str,
    name: Optional[str] = None,
    country_codes: OptionalListOr[str] = None,
    year_numbers: OptionalListOr[int] = None,
    brand_id: Optional[int] = None,
    studies: OptionalListOr[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.BrandsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    **kwargs: BaseListOrValues,
) -> "DataFrame":
    """Query the Fount `brands` endpoint

    Parameters
    ----------
    token : str
        Fount API token
    name : str, optional
        Search brands by name, by default None
    country_codes: str or list[str], optional
        ISO-3166-1 alpha-2 country codes, by default None
    year_numbers : int or list[int], optional
        Study years, by default None
    brand_id : int, optional
        Fount brand ID, by default None

        If a brand ID is provided, only that brand will be returned
    studies : int or list[int], optional
        Fount study IDs, by default None
    filters : BrandsFilters or dict of filters, optional
        BrandsFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, by default None
    per_page : int, optional
        Number of results per page, by default None
    max_pages : int, optional
        Max number of results to return, by default None
    sort : str, optional
        Sort response by field, by default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brands` endpoint results
    """

    async with Client(token) as fount:
        return await fount.brands(
            name,
            country_codes,
            year_numbers,
            brand_id,
            studies,
            filters=filters,
            fields=fields,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def brandscape_data(
    token: str,
    country_code: OptionalListOr[str] = None,
    year_number: OptionalListOr[int] = None,
    audiences: OptionalListOr[int] = None,
    brand_name: Optional[str] = None,
    studies: OptionalListOr[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.BrandscapeFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    metric_keys: OptionalListOr[str] = None,
    stack_data: bool = False,
    **kwargs: BaseListOrValues,
) -> "DataFrame":
    """Query the Fount `brandscape-data` endpoint.

    This endpoint requires at least one of the following combinations of parameters:

    - `studies`
    - `brand_name` or `brands`
    - `country_code` or `countries` and `brands` or `brand_name`
    - `year_number` or `years` and `country_code` or `countries`

    An audience filter is also highly recommended, as otherwise the API will return
    data for all audiences (there are more than 30 standard audiences).

    The `Audiences` class is provided to make it easier to filter audiences.

    Note that this endpoint has a default set of `include` resources:
    - `brand`
    - `study`
    - `category`

    Any additional valid includes will be added to the default set.

    If any of the default includes are used in `include`, then only that resource
    will be retrieved. This is to allow requesting individual includes if they are
    part of the default.

    Parameters
    ----------
    token : str
        Fount API token
    country_code : str or list[str], optional
        ISO-3166-1 alpha-2 country codes, by default None
    year_number : int or list[int], optional
        Study years, by default None
    audiences : int or list[int], optional
        Audiences to retrieve by audience ID, by default None

        The `Audiences` class can help with this filter.
    brand_name : str, optional
        Search by brand name, by default None
    studies : int or list[int], optional
        Fount studies IDs, by default None
    filters : BrandscapeFilters or dict of filters, optional
        BrandscapeFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    metric_keys: str or list[str], optional
        Key or list of keys for the metrics included in the response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, by default None
    per_page : int, optional
        Number of results per page, by default None
    max_pages : int, optional
        Max number of results to return, by default None
    sort : str, optional
        Sort response by field, by default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brandscape-data` endpoint results

    Raises
    ------
    ValidationError
        If used with an invalid combination of parameters (see above)
    """

    async with Client(token) as fount:
        return await fount.brandscape_data(
            country_code,
            year_number,
            audiences,
            brand_name,
            studies,
            filters=filters,
            fields=fields,
            metric_keys=metric_keys,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def studies(
    token: str,
    country_codes: OptionalListOr[str] = None,
    year_numbers: OptionalListOr[int] = None,
    full_year: Literal[0, 1] = 0,
    study_id: Optional[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.StudiesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    **kwargs: BaseListOrValues,
) -> "DataFrame":
    """Query the Fount `studies` endpoint.

    Parameters
    ----------
    token : str
        Fount API token
    country_codes: str or list[str], optional
        ISO-3166-1 alpha-2 country codes, by default None
    year_numbers : int or list[int], optional
        Study years, by default None
    full_year : Literal[0, 1], optional
        Include or exclude studies which are not "full year" studies,
        such as US quarterly studies or special studies, by default 0

        A value of 1 will filter non-full-year studies.
    study_id : int, optional
        Fount study ID, by default None
        If a study ID is provided, only that study will be returned
    filters : StudiesFilters or dict of filters, optional
        StudiesFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, by default None
    per_page : int, optional
        Number of results per page, by default None
    max_pages : int, optional
        Max number of results to return, by default None
    sort : str, optional
        Sort response by field, by default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `studies` endpoint results
    """

    async with Client(token) as fount:
        return await fount.studies(
            country_codes,
            year_numbers,
            full_year,
            study_id,
            filters=filters,
            fields=fields,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )
