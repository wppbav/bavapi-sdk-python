"""
Top level functions to perform queries to the Fount.

You will need your BAV API token to use these functions.

Examples
--------

Use top level functions for one-off downloads:

>>> import bavapi
>>> result = bavapi.brands("TOKEN", "Facebook")  # Replace TOKEN with your API key

A more complex query:

>>> from bavapi_refs import Audiences
>>> bss = bavapi.brandscape_data(
...     "TOKEN",  # Replace TOKEN with your API key
...     country_code="UK",
...     year_number=2022,
...     audiences=Audiences.ALL_ADULTS,
... )

Use `bavapi.raw_query` (with `bavapi.Query`) for endpoints that aren't fully supported:

>>> query = bavapi.Query(filters=bavapi.filters.FountFilters(name="Meta"))
>>> result = bavapi.raw_query("companies", query=query)

If you want to make multiple requests or embed `bavapi` into applications,
consider using the `bavapi.Client` interface.
"""

# pylint: disable=redefined-outer-name, too-many-arguments
# pylint: disable=too-many-locals, too-many-lines

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
    "audiences",
    "brand_metrics",
    "brand_metric_groups",
    "brands",
    "brandscape_data",
    "categories",
    "collections",
    "raw_query",
    "sectors",
    "studies",
)

P = ParamSpec("P")
R = TypeVar("R")
F = TypeVar("F", bound=_filters.FountFilters)


def _coro(func: Callable[P, Awaitable[R]]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
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
    query: Query[F],
    *,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
) -> List[JSONDict]:
    """Perform a raw GET query to the Fount API, returning the response JSON data
    instead of a `pandas` DataFrame.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    endpoint : str
        Endpoint name
    query : Query
        bavapi.Query object with query parameters.
    timeout : float
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`

    Returns
    -------
    list[dict[str, Any]]
        List of JSON response data
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.raw_query(endpoint, query)


@_coro
async def audiences(
    token: str,
    name: Optional[str] = None,
    active: Literal[0, 1] = 0,
    public: Literal[0, 1] = 0,
    *,
    audience_id: Optional[int] = None,
    private: Literal[0, 1] = 0,
    groups: OptionalListOr[int] = None,
    filters: OptionalFiltersOrMapping[_filters.AudiencesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.AudiencesFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `audiences` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search audiences by name, default None
    active : Literal[0, 1], optional
        Return active audiences only if set to `1`, default 0
    public : Literal[0, 1], optional
        Return active audiences only if set to `1`, default 0
    audience_id : int, optional
        Fount audience ID, default None

        If an audience ID is provided, only that audience will be returned
    private : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, default 0
    groups : int or list[int], optional
        Audience group ID or list of audience group IDs, default None
    filters : AudiencesFilters or dict of filters, optional
        AudiencesFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[AudiencesFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brands` endpoint results
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.audiences(
            name,
            active,
            public,
            audience_id=audience_id,
            private=private,
            groups=groups,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def brand_metrics(
    token: str,
    name: Optional[str] = None,
    active: Literal[0, 1] = 0,
    public: Literal[0, 1] = 0,
    *,
    metric_id: Optional[int] = None,
    private: Literal[0, 1] = 0,
    groups: OptionalListOr[int] = None,
    filters: OptionalFiltersOrMapping[_filters.BrandMetricsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.BrandMetricsFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brand-metrics` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search brand metrics by name, default None
    active : Literal[0, 1], optional
        Return active brand metrics only if set to `1`, default 0
    public : Literal[0, 1], optional
        Return active brand metrics only if set to `1`, default 0
    metric_id : int, optional
        Fount metric ID, default None

        If an metric ID is provided, only that metric will be returned
    private : Literal[0, 1], optional
        Return inactive brand metrics only if set to `1`, default 0
    groups : int or list[int], optional
        Brand metrics group ID or list of brand metrics group IDs, default None
    filters : BrandMetricsFilters or dict of filters, optional
        BrandMetricsFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[BrandMetricsFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brand-metrics` endpoint results.
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.brand_metrics(
            name,
            active,
            public,
            metric_id=metric_id,
            private=private,
            groups=groups,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def brand_metric_groups(
    token: str,
    name: Optional[str] = None,
    active: Literal[0, 1] = 0,
    *,
    group_id: Optional[int] = None,
    filters: OptionalFiltersOrMapping[_filters.BrandMetricGroupsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.BrandMetricGroupsFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brand-metric-groups` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search brand metric groups by name, default None
    active : Literal[0, 1], optional
        Return active brand metric groups only if set to `1`, default 0
    group_id : int, optional
        Fount brand metric group ID, default None

        If a metric group ID is provided, only that metric group will be returned
    filters : BrandMetricGroupsFilters or dict of filters, optional
        BrandMetricGroupsFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[BrandMetricGroupsFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brand-metric-groups` endpoint results.
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.brand_metric_groups(
            name,
            active,
            group_id=group_id,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def brands(
    token: str,
    name: Optional[str] = None,
    country_codes: OptionalListOr[str] = None,
    year_numbers: OptionalListOr[int] = None,
    *,
    brand_id: Optional[int] = None,
    studies: OptionalListOr[int] = None,
    filters: OptionalFiltersOrMapping[_filters.BrandsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.BrandsFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `brands` endpoint

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    name : str, optional
        Search brands by name, default None
    country_codes: str or list[str], optional
        ISO-3166-1 alpha-2 country codes, default None
    year_numbers : int or list[int], optional
        Study years, default None
    brand_id : int, optional
        Fount brand ID, default None

        If a brand ID is provided, only that brand will be returned
    studies : int or list[int], optional
        Fount study IDs, default None
    filters : BrandsFilters or dict of filters, optional
        BrandsFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[BrandsFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `brands` endpoint results
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.brands(
            name,
            country_codes,
            year_numbers,
            brand_id=brand_id,
            studies=studies,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
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
    *,
    studies: OptionalListOr[int] = None,
    filters: OptionalFiltersOrMapping[_filters.BrandscapeFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    metric_keys: OptionalListOr[str] = None,
    metric_group_keys: OptionalListOr[str] = None,
    query: Optional[Query[_filters.BrandscapeFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
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

    Also note that due to a name clash in the "brand" `include`, brand columns
    will be prefixed with `"global_"`. Thus, these columns will refer to the global
    brand, while the `brand_name` column will refer to the local brand/spelling.

    If any of the default includes are used in `include`, then only that resource
    will be retrieved. This is to allow requesting individual includes if they are
    part of the default.

    To suppress default includes, set `include` to `"no_default"`.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    country_code : str or list[str], optional
        ISO-3166-1 alpha-2 country codes, default None
    year_number : int or list[int], optional
        Study years, default None
    audiences : int or list[int], optional
        Audiences to retrieve by audience ID, default None

        The `Audiences` class can help with this filter.
    brand_name : str, optional
        Search by brand name, default None
    studies : int or list[int], optional
        Fount studies IDs, default None
    filters : BrandscapeFilters or dict of filters, optional
        BrandscapeFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    metric_keys: str or list[str], optional
        Key or list of keys for the metrics included in the response, default None
    metric_group_keys: str or list[str], optional
        Key or list of keys for the metric groups included in the response, default None

        Currently, this parameter is only available for the `brandscape-data` endpoint.
    query : Query[BrandscapeFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

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

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.brandscape_data(
            country_code,
            year_number,
            audiences,
            brand_name,
            studies=studies,
            filters=filters,
            fields=fields,
            metric_keys=metric_keys,
            metric_group_keys=metric_group_keys,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def categories(
    token: str,
    name: Optional[str] = None,
    sector: OptionalListOr[int] = None,
    *,
    category_id: Optional[int] = None,
    filters: OptionalFiltersOrMapping[_filters.CategoriesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.CategoriesFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `categories` endpoint.

    Note that this endpoint has a default set of `include` resources:
    - `sector`

    To suppress default includes, set `include` to `"no_default"`.

    Parameters
    ----------
    name : str, optional
        Search categories by name, default None
    sector : int or list[int], optional
        Filter categories by sector ID, default 0
    category_id : int, optional
        Fount category ID, default None

        If an category ID is provided, only that category will be returned
    filters : CategoriesFilters or dict of filters, optional
        CategoriesFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[CategoriesFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `categories` endpoint results.
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.categories(
            name,
            sector,
            category_id=category_id,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def collections(
    token: str,
    name: Optional[str] = None,
    public: Literal[0, 1] = 0,
    *,
    collection_id: Optional[int] = None,
    shared_with_me: Literal[0, 1] = 0,
    mine: Literal[0, 1] = 0,
    filters: OptionalFiltersOrMapping[_filters.CollectionsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.CollectionsFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `collections` endpoint.

    Parameters
    ----------
    name : str, optional
        Search collections by name, default None
    public : Literal[0, 1], optional
        Return public collections only if set to `1`, default 0
    collection_id : int, optional
        Fount collection ID, default None

        If a collection ID is provided, only that collection will be returned
    shared_with_me : Literal[0, 1], optional
        Only return collections that have been shared with the user, default 0
    mine : Literal[0, 1], optional
        Only return collections created by the user, default 0
    filters : CollectionsFilters or dict of filters, optional
        CollectionsFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[CollectionsFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `collections` endpoint results.
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.collections(
            name,
            public,
            collection_id=collection_id,
            shared_with_me=shared_with_me,
            mine=mine,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def sectors(
    token: str,
    name: Optional[str] = None,
    in_most_influential: Literal[0, 1] = 0,
    *,
    sector_id: Optional[int] = None,
    filters: OptionalFiltersOrMapping[_filters.SectorsFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.SectorsFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `sectors` endpoint.

    Parameters
    ----------
    name : str, optional
        Search categories by name, default None
    in_most_influential : Literal[0, 1], optional
        Sectors that are part of the Most Influential lists, default 0
    sector_id : int, optional
        Fount sectors ID, default None

        If a sector ID is provided, only that sector will be returned
    filters : SectorsFilters or dict of filters, optional
        SectorsFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[SectorsFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `sectors` endpoint results.
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.sectors(
            name,
            in_most_influential,
            sector_id=sector_id,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )


@_coro
async def studies(
    token: str,
    country_codes: OptionalListOr[str] = None,
    year_numbers: OptionalListOr[int] = None,
    full_year: Literal[0, 1] = 0,
    released: Literal[0, 1] = 0,
    bav_study: Literal[0, 1] = 0,
    *,
    study_id: Optional[int] = None,
    filters: OptionalFiltersOrMapping[_filters.StudiesFilters] = None,
    fields: OptionalListOr[str] = None,
    include: OptionalListOr[str] = None,
    query: Optional[Query[_filters.StudiesFilters]] = None,
    stack_data: bool = False,
    timeout: float = 30.0,
    verbose: bool = True,
    batch_size: int = 10,
    n_workers: int = 2,
    retries: int = 3,
    on_errors: Literal["warn", "raise"] = "warn",
    **kwargs: Unpack[CommonQueryParams],
) -> "DataFrame":
    """Query the Fount `studies` endpoint.

    Parameters
    ----------
    token : str
        WPPBAV Fount API token
    country_codes: str or list[str], optional
        ISO-3166-1 alpha-2 country codes, default None
    year_numbers : int or list[int], optional
        Study years, default None
    full_year : Literal[0, 1], optional
        Include or exclude studies which are not "full year" studies,
        such as US quarterly studies or special studies, default 0

        A value of 1 will filter non-full-year studies.
    released : Literal[0, 1], optional
        Return released studies when set to `1`, default 0
    bav_study : Literal[0, 1], optional
        Return full BAV studies when set to `1`, default 0
    study_id : int, optional
        Fount study ID, default None
        If a study ID is provided, only that study will be returned
    filters : StudiesFilters or dict of filters, optional
        StudiesFilters object or dictionary of filter parameters, default None
    fields : str or list[str], optional
        Fields to retrieve in API response, default None

        Only specified fields are returned.
        If `fields` is None, all fields are returned.
    include : str or list[str], optional
        Additional resources to include in API response, default None
    query : Query[StudiesFilters], optional
        Query object to perform request with, default None

        If query is used, all parameters listed before `query` will be ignored.
    stack_data : bool, optional
        Whether to expand nested lists into new dictionaries, default False
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verbose : bool, optional
        Set to False to disable progress bar, default True
    batch_size : int, optional
        Size of batches to make requests with, default 10
    n_workers : int, optional
        Number of workers to make requests, default 2
    retries : int, optional
        Number of times to retry a request, default 3
    on_errors : Literal["warn", "raise"], optional
        Warn about failed requests or raise immediately on failure, default `"warn"`
    **kwargs
        Additional parameters to pass to the Query. See `Other Parameters`.
        For any filters, use the `filters` parameter.

    Other Parameters
    ----------------
    page : int, optional
        Page number to fetch, default None
    per_page : int, optional
        Number of results per page, default None
    max_pages : int, optional
        Max number of results to return, default None
    sort : str, optional
        Sort response by field, default None

        To sort in descending (highest first) order, use a `-` before the field name:

        `sort="-differentiation_rank"`

        Sorts by item ID by default.

    Returns
    -------
    pandas.DataFrame
        DataFrame with `studies` endpoint results
    """

    async with Client(
        token,
        timeout=timeout,
        verbose=verbose,
        batch_size=batch_size,
        n_workers=n_workers,
        retries=retries,
        on_errors=on_errors,
    ) as client:
        return await client.studies(
            country_codes,
            year_numbers,
            full_year,
            released,
            bav_study,
            study_id=study_id,
            filters=filters,
            fields=fields,
            include=include,
            query=query,
            stack_data=stack_data,
            **kwargs,
        )
