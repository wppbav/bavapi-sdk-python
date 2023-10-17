"""
Top level functions to perform queries to the Fount.

You will need your BAV API token to use these functions.

Examples
--------

Use top level functions for one-off downloads:

>>> import bavapi
>>> result = bavapi.brands("TOKEN", "Facebook")  # Replace TOKEN with your API key

A more complex query:

>>> from bavapi_refs.audiences import Audiences
>>> bss = bavapi.brandscape_data(
...     "TOKEN",  # Replace TOKEN with your API key
...     country_code="UK",
...     year_number=2022,
...     audiences=Audiences.ALL_ADULTS,
... )

Use `bavapi.raw_query` (with `bavapi.Query`) for endpoints that aren't fully supported:

>>> query = bavapi.Query(filters=bavapi.filters.FountFilters(name="Meta"))
>>> result = bavapi.raw_query("companies", params=query)

If you want to make multiple requests or embed `bavapi` into applications,
consider using the `bavapi.Client` interface.
"""

# pylint: disable=redefined-outer-name, too-many-arguments, too-many-locals

import asyncio
import functools
from typing import TYPE_CHECKING, Awaitable, Callable, List, Literal, Optional, TypeVar

from bavapi import filters as _filters
from bavapi._jupyter import patch_loop, running_in_jupyter
from bavapi.client import Client, OptionalFiltersOrMapping
from bavapi.query import Query
from bavapi.typing import CommonQueryParams, JSONDict, OptionalListOr, ParamSpec, Unpack

if TYPE_CHECKING:
    from pandas import DataFrame

__all__ = (
    "brand_metrics",
    "brand_metric_groups",
    "brands",
    "brandscape_data",
    "categories",
    "collections",
    "raw_query",
    "sectors",
)

T = TypeVar("T")
P = ParamSpec("P")
F = TypeVar("F", bound=_filters.FountFilters)


def _coro(func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
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
async def raw_query(
    token: str,
    endpoint: str,
    params: Query[F],
    timeout: float = 30.0,
    *,
    verbose: bool = True,
) -> List[JSONDict]:
    """Perform a raw GET query to the Fount API, returning the response JSON data
    instead of a `pandas` DataFrame.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    endpoint : str
        Endpoint name
    params : Query
        Query `pydantic` model with query parameters.
    timeout : float
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True

    Returns
    -------
    list[dict[str, Any]]
        List of JSON response data
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.raw_query(endpoint, params)


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
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `audiences` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search audiences by name, by default None
    audience_id : int, optional
        Fount audience ID, by default None

        If an audience ID is provided, only that audience will be returned
    active : Literal[0, 1], optional
        Return active audiences only if set to `1`, by default 0
    inactive : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, by default 0
    public : Literal[0, 1], optional
        Return active audiences only if set to `1`, by default 0
    private : Literal[0, 1], optional
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
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.audiences(
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
async def brand_metrics(
    token: str,
    name: Optional[str] = None,
    metric_id: Optional[int] = None,
    active: Literal[0, 1] = 0,
    inactive: Literal[0, 1] = 0,
    public: Literal[0, 1] = 0,
    private: Literal[0, 1] = 0,
    groups: OptionalListOr[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.BrandMetricsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brand-metrics` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search brand metrics by name, by default None
    metric_id : int, optional
        Fount metric ID, by default None

        If an metric ID is provided, only that metric will be returned
    active : Literal[0, 1], optional
        Return active brand metrics only if set to `1`, by default 0
    inactive : Literal[0, 1], optional
        Return inactive brand metrics only if set to `1`, by default 0
    public : Literal[0, 1], optional
        Return active brand metrics only if set to `1`, by default 0
    private : Literal[0, 1], optional
        Return inactive brand metrics only if set to `1`, by default 0
    groups : int or list[int], optional
        Brand metrics group ID or list of brand metrics group IDs, by default None
    filters : BrandMetricsFilters or dict of filters, optional
        BrandMetricsFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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
        DataFrame with `brand-metrics` endpoint results.
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.brand_metrics(
            name,
            metric_id,
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
async def brand_metric_groups(
    token: str,
    name: Optional[str] = None,
    group_id: Optional[int] = None,
    active: Literal[0, 1] = 0,
    inactive: Literal[0, 1] = 0,
    *,
    filters: OptionalFiltersOrMapping[_filters.BrandMetricGroupsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brand-metric-groups` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search brand metric groups by name, by default None
    group_id : int, optional
        Fount brand metric group ID, by default None

        If a metric group ID is provided, only that metric group will be returned
    active : Literal[0, 1], optional
        Return active brand metric groups only if set to `1`, by default 0
    inactive : Literal[0, 1], optional
        Return inactive brand metric groups only if set to `1`, by default 0
    filters : BrandMetricGroupsFilters or dict of filters, optional
        BrandMetricGroupsFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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
        DataFrame with `brand-metric-groups` endpoint results.
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.brand_metric_groups(
            name,
            group_id,
            active,
            inactive,
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
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brands` endpoint

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
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
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.brands(
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
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brandscape-data` endpoint.

    This endpoint requires at least one of the following combinations of parameters:

    - Study + Audience + Brand + Category
    - Country + Year + Audience
    - Brand + Audience + Country + Year

    You should read these from left to right. A combination of "Study + Audience"
    worksjust as well as "Study + Audience + Brand".
    However, "Category + Audience" will not.

    If you use Country or Year filters, you must use both filters together.

    An audience filter is also highly recommended, as otherwise the API will return
    data for all audiences (there are more than 100 standard audiences).

    The `Audiences` class is provided to make it easier to filter audiences.

    Note that this endpoint has a default set of `include` resources:
    - `brand`
    - `study`
    - `category`

    Any additional valid includes will be added to the default set.

    If any of the default includes are used in `include`, then only that resource
    will be retrieved. This is to allow requesting individual includes if they are
    part of the default.

    To suppress default includes, set `include` to `"no_default"`.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
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
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.brandscape_data(
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
async def categories(
    token: str,
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    sector: OptionalListOr[int] = None,
    *,
    filters: OptionalFiltersOrMapping[_filters.CategoriesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `categories` endpoint.

    Note that this endpoint has a default set of `include` resources:
    - `sector`

    To suppress default includes, set `include` to `"no_default"`.

    Parameters
    ----------
    name : str, optional
        Search categories by name, by default None
    category_id : int, optional
        Fount category ID, by default None

        If an category ID is provided, only that category will be returned
    sector : int or list[int], optional
        Filter categories by sector ID, by default 0
    filters : CategoriesFilters or dict of filters, optional
        CategoriesFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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
        DataFrame with `categories` endpoint results.
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.categories(
            name,
            category_id,
            sector,
            filters=filters,
            fields=fields,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def collections(
    token: str,
    name: Optional[str] = None,
    collection_id: Optional[int] = None,
    public: Literal[0, 1] = 0,
    shared_with_me: Literal[0, 1] = 0,
    mine: Literal[0, 1] = 0,
    *,
    filters: OptionalFiltersOrMapping[_filters.CollectionsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `collections` endpoint.

    Parameters
    ----------
    name : str, optional
        Search collections by name, by default None
    collection_id : int, optional
        Fount collection ID, by default None

        If a collection ID is provided, only that collection will be returned
    public : Literal[0, 1], optional
        Return public collections only if set to `1`, by default 0
    shared_with_me : Literal[0, 1], optional
        Only return collections that have been shared with the user, by default 0
    mine : Literal[0, 1], optional
        Only return collections created by the user, by default 0
    filters : CollectionsFilters or dict of filters, optional
        CollectionsFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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
        DataFrame with `collections` endpoint results.
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.collections(
            name,
            collection_id,
            public,
            shared_with_me,
            mine,
            filters=filters,
            fields=fields,
            include=include,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def sectors(
    token: str,
    name: Optional[str] = None,
    sector_id: Optional[int] = None,
    in_most_influential: Literal[0, 1] = 0,
    not_in_most_influential: Literal[0, 1] = 0,
    *,
    filters: OptionalFiltersOrMapping[_filters.SectorsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `sectors` endpoint.

    Parameters
    ----------
    name : str, optional
        Search categories by name, by default None
    sector_id : int, optional
        Fount sectors ID, by default None

        If a sector ID is provided, only that sector will be returned
    in_most_influential : Literal[0, 1], optional
        Sectors that are part of the Most Influential lists, by default 0
    not_in_most_influential : Literal[0, 1], optional
        Sectors that are not part of the Most Influential lists, by default 0
    filters : SectorsFilters or dict of filters, optional
        SectorsFilters object or dictionary of filter parameters, by default None
    fields : str or list[str], optional
        Fields to retrieve in API response, by default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, by default None
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, by default False
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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
        DataFrame with `sectors` endpoint results.
    """

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.sectors(
            name,
            sector_id,
            in_most_influential,
            not_in_most_influential,
            filters=filters,
            fields=fields,
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
    timeout: float = 30.0,
    verbose: bool = True,
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `studies` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
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
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, by default True
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

    async with Client(token, timeout=timeout, verbose=verbose) as client:
        return await client.studies(
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
