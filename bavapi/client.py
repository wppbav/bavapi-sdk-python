"""
Asynchronous BAV API client interface.

Similar to `requests.Session` or `httpx.AsyncClient` (uses the latter as dependency).

Examples
--------

Create a client instance and make a request to the `brands` endpoint.

>>> async with bavapi.Client("TOKEN") as bav:
...     result = await bav.brands("Facebook")

A more complex query:

>>> from bavapi_refs import Audiences
>>> async with bavapi.Client("TOKEN") as bav:
...     bss = await bav.brandscape_data(
...         country_code="UK",
...         year_number=2022,
...         audiences=Audiences.ALL_ADULTS,
...     )

Multiple queries will share the client connection for better performance:

>>> async with bavapi.Client("TOKEN") as bav:
...     result1 = await bav.brands("Facebook")
...     result2 = await bav.brands("Instagram")

Use `Client.raw_query` (with `bavapi.Query`) for endpoints that aren't fully supported:

>>> query = bavapi.Query(filters=bavapi.filters.FountFilters(name="Meta"))
>>> async with bavapi.Client("TOKEN") as bav:
...     result = await bav.raw_query("companies", query=query)
"""

# pylint: disable=too-many-arguments, too-many-lines

from typing import (
    TYPE_CHECKING,
    Final,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from bavapi import filters as _filters
from bavapi.http import HTTPClient
from bavapi.parsing.responses import parse_response
from bavapi.query import Query
from bavapi.typing import CommonQueryParams, JSONDict, OptionalListOr, Unpack

if TYPE_CHECKING:
    from types import TracebackType

    from pandas import DataFrame

__all__ = ("Client",)

BASE_URL: Final[str] = "https://fount.wppbav.com/api/v2/"
USER_AGENT: Final[str] = "BAVAPI SDK Python"

BRANDSCAPE_DEFAULTS: Final[List[str]] = ["study", "brand", "category", "audience"]
CATEGORIES_DEFAULTS: Final[List[str]] = ["sector"]

F = TypeVar("F", bound=_filters.FountFilters)

OptionalFiltersOrMapping = Optional[_filters.FiltersOrMapping[F]]


class Client:
    """Asynchronous API to interact with the WPPBAV Fount API.

    This class uses `asyncio` to perform asynchronous requests to the Fount API.

    Asynchronous requests allow you to make multiple requests at the same time,
    extremely helpful for working with a paginated API like the Fount. (returns
    data in multiple pages or requests instead of one single download)

    To use the Client class, you will need to precede calls with `await`:

    ```py
    bav = Client("TOKEN")  # creating client instance does not use `await`
    data = await bav.brands("Swatch")  # must use `await`
    ```

    For more information, see the `asyncio` documentation for Python.

    Either `auth_token` or `client` are required to instantiate a Client.

    Parameters
    ----------
    auth_token : str, optional
        WPPBAV Fount API authorization token, default `''`
    per_page : int, optional
        Default number of entries per page, default 100
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verify : bool or str, optional
        Verify SSL credentials, default True

        Also accepts a path string to an SSL certificate file.
    user_agent : str, optional
        The name of the User-Agent to send to the Fount API, default `''`.

        If no user_agent is set, `bavapi` will use `"BAVAPI SDK Python"` by default.
    client : HTTPClient, optional
        Authenticated async client from `bavapi.http`, default None

        If `client` is passed, all other parameters will be ignored.
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

    Raises
    ------
    ValueError
        If neither `auth_token` nor `client` are provided

    Examples
    --------
    Use `async with` to get data and close the connection.

    This way you get the benefits from `httpx` speed improvements
    and closes the connection when exiting the async with block.

    >>> async with Client("TOKEN") as bav:
    ...     data = await bav.brands("Swatch")

    When not using `async with`, close the connection manually by awaiting `aclose`.

    >>> bav = Client("TOKEN")
    >>> data = await bav.brands("Swatch")
    >>> await bav.aclose()

    If you want to perform multiple endpoint requests with the same `Client`, it is
    recommended to use `verbose=False` to avoid jumping progress bars.

    >>> async with Client("TOKEN", verbose=False) as bav:
    ...     resp1 = await bav.brands("Facebook")
    ...     resp2 = await bav.brands("Microsoft")
    """

    @overload
    def __init__(self, auth_token: str) -> None:
        ...

    @overload
    def __init__(
        self,
        auth_token: str,
        per_page: int = 100,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        user_agent: str = "",
        *,
        verbose: bool = True,
        batch_size: int = 10,
        n_workers: int = 2,
        retries: int = 3,
        on_errors: Literal["warn", "raise"] = "warn",
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        client: HTTPClient = ...,
        verbose: bool = True,
        batch_size: int = 10,
        n_workers: int = 2,
        retries: int = 3,
        on_errors: Literal["warn", "raise"] = "warn",
    ) -> None:
        ...

    def __init__(
        self,
        auth_token: str = "",
        per_page: int = 100,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        user_agent: str = "",
        *,
        client: Optional[HTTPClient] = None,
        verbose: bool = True,
        batch_size: int = 10,
        n_workers: int = 2,
        retries: int = 3,
        on_errors: Literal["warn", "raise"] = "warn",
    ) -> None:
        if client is not None:
            self._client = client
        else:
            if not auth_token:
                raise ValueError("You must provide `auth_token` or `client`.")
            self._client = HTTPClient(
                base_url=BASE_URL,
                per_page=per_page,
                timeout=timeout,
                verify=verify,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Accept": "application/json",
                    "User-Agent": user_agent or USER_AGENT,
                },
                verbose=verbose,
                batch_size=batch_size,
                n_workers=n_workers,
                retries=retries,
                on_errors=on_errors,
            )

    @property
    def per_page(self) -> int:
        """Default number of items to retrieve per page."""
        return self._client.per_page

    @per_page.setter
    def per_page(self, value: int) -> None:
        self._client.per_page = value

    @property
    def verbose(self) -> bool:
        """Show progress bar when making requests."""
        return self._client.verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._client.verbose = value

    @property
    def batch_size(self) -> int:
        """Size of batches to make requests with."""
        return self._client.batch_size

    @batch_size.setter
    def batch_size(self, value: int) -> None:
        self._client.batch_size = value

    @property
    def n_workers(self) -> int:
        """Number of workers to make requests."""
        return self._client.n_workers

    @n_workers.setter
    def n_workers(self, value: int) -> None:
        self._client.n_workers = value

    @property
    def retries(self) -> int:
        """Number of times to retry a request."""
        return self._client.retries

    @retries.setter
    def retries(self, value: int) -> None:
        self._client.retries = value

    @property
    def on_errors(self) -> Literal["warn", "raise"]:
        """Number of times to retry a request."""
        return self._client.on_errors

    @on_errors.setter
    def on_errors(self, value: Literal["warn", "raise"]) -> None:
        self._client.on_errors = value

    async def __aenter__(self) -> "Client":
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: "Optional[TracebackType]" = None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)

    async def aclose(self) -> None:
        """Close existing HTTP connections."""
        return await self._client.aclose()

    async def raw_query(self, endpoint: str, query: Query[F]) -> List[JSONDict]:
        """Perform a raw GET query to the WPPBAV Fount API, returning
        the response JSON data instead of a `pandas` DataFrame.

        Parameters
        ----------
        endpoint : str
            Endpoint name
        query : Query
            bavapi.Query object with query parameters.

        Returns
        -------
        list[dict[str, Any]]
            List of JSON response data
        """
        return list(await self._client.query(endpoint, query))

    async def audiences(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `audiences` endpoint.

        Parameters
        ----------
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
            DataFrame with `brands` endpoint results.
        """
        filters = _filters.AudiencesFilters.ensure(
            filters,
            name=name,
            active=active,
            public=public,
            private=private,
            groups=groups,
        )

        query = Query.ensure(
            query,
            id=audience_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("audiences", query)

        return parse_response(items, expand=stack_data)

    async def brand_metrics(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `brand-metrics` endpoint.

        Parameters
        ----------
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
            Brand metrics group ID or list of Brand metrics group IDs, default None
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
        filters = _filters.BrandMetricsFilters.ensure(
            filters,
            name=name,
            active=active,
            public=public,
            private=private,
            groups=groups,
        )

        query = Query.ensure(
            query,
            id=metric_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("brand-metrics", query)

        return parse_response(items, expand=stack_data)

    async def brand_metric_groups(
        self,
        name: Optional[str] = None,
        active: Literal[0, 1] = 0,
        *,
        group_id: Optional[int] = None,
        filters: OptionalFiltersOrMapping[_filters.BrandMetricGroupsFilters] = None,
        fields: OptionalListOr[str] = None,
        include: OptionalListOr[str] = None,
        query: Optional[Query[_filters.BrandMetricGroupsFilters]] = None,
        stack_data: bool = False,
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `brand-metric-groups` endpoint.

        Parameters
        ----------
        name : str, optional
            Search brand metric groups by name, default None
        active : Literal[0, 1], optional
            Return active brand metric groups only if set to `1`, default 0
        group_id : int, optional
            Fount metric group ID, default None

            If an metric group ID is provided, only that metric group will be returned
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
        filters = _filters.BrandMetricGroupsFilters.ensure(
            filters,
            name=name,
            active=active,
        )

        query = Query.ensure(
            query,
            id=group_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("brand-metric-groups", query)

        return parse_response(items, expand=stack_data)

    async def brands(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `brands` endpoint.

        Parameters
        ----------
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
            DataFrame with `brands` endpoint results.
        """
        filters = _filters.BrandsFilters.ensure(
            filters,
            name=name,
            country_codes=country_codes,
            year_numbers=year_numbers,
            studies=studies,
        )

        query = Query.ensure(
            query,
            id=brand_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("brands", query)

        return parse_response(items, expand=stack_data)

    async def brandscape_data(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `brandscape-data` endpoint.

        This endpoint requires at least one of the following combinations of filters:

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
        - `audience`

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
            DataFrame with `brandscape-data` endpoint results.

        Raises
        ------
        ValidationError
            If used with an invalid combination of parameters (see above)
        """
        filters = _filters.BrandscapeFilters.ensure(
            filters,
            country_code=country_code,
            year_number=year_number,
            audiences=audiences,
            brand_name=brand_name,
            studies=studies,
        )

        query = Query.ensure(
            query,
            filters=filters,
            fields=fields,
            include=_default_include(include, BRANDSCAPE_DEFAULTS),
            metric_keys=metric_keys,
            metric_group_keys=metric_group_keys,
            **kwargs,
        )

        items = await self._client.query("brandscape-data", query)

        # Prefix 'global' to avoid clashing with 'brand_name' on 'brand' includes
        return parse_response(items, "global", expand=stack_data)

    async def categories(
        self,
        name: Optional[str] = None,
        sector: OptionalListOr[int] = None,
        *,
        category_id: Optional[int] = None,
        filters: OptionalFiltersOrMapping[_filters.CategoriesFilters] = None,
        fields: OptionalListOr[str] = None,
        include: OptionalListOr[str] = None,
        query: Optional[Query[_filters.CategoriesFilters]] = None,
        stack_data: bool = False,
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `categories` endpoint.

        Note that this endpoint has a default set of `include` resources:
        - `sector`

        Any additional valid includes will be added to the default set.

        If any of the default includes are used in `include`, then only that resource
        will be retrieved. This is to allow requesting individual includes if they are
        part of the default.

        Parameters
        ----------
        name : str, optional
            Search categories by name, default None
        sector : int or list[int], optional
            Filter categories by sector ID, default None
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
        filters = _filters.CategoriesFilters.ensure(
            filters,
            name=name,
            sector=sector,
        )

        query = Query.ensure(
            query,
            id=category_id,
            filters=filters,
            fields=fields,
            include=_default_include(include, CATEGORIES_DEFAULTS),
            **kwargs,
        )

        items = await self._client.query("categories", query)

        return parse_response(items, expand=stack_data)

    async def collections(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `collections` endpoint.

        Parameters
        ----------
        name : str, optional
            Search collections by name, default None
        public : Literal[0, 1], optional
            Return public collections only, default 0
        collection_id : int, optional
            Fount collection ID, default None

            If an collection ID is provided, only that collection will be returned
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
        filters = _filters.CollectionsFilters.ensure(
            filters,
            name=name,
            public=public,
            shared_with_me=shared_with_me,
            mine=mine,
        )

        query = Query.ensure(
            query,
            id=collection_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("collections", query)

        return parse_response(items, expand=stack_data)

    async def sectors(
        self,
        name: Optional[str] = None,
        in_most_influential: Literal[0, 1] = 0,
        *,
        sector_id: Optional[int] = None,
        filters: OptionalFiltersOrMapping[_filters.SectorsFilters] = None,
        fields: OptionalListOr[str] = None,
        include: OptionalListOr[str] = None,
        query: Optional[Query[_filters.SectorsFilters]] = None,
        stack_data: bool = False,
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `sectors` endpoint.

        Parameters
        ----------
        name : str, optional
            Search sectors by name, default None
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
        filters = _filters.SectorsFilters.ensure(
            filters,
            name=name,
            in_most_influential=in_most_influential,
        )

        query = Query.ensure(
            query,
            id=sector_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("sectors", query)

        return parse_response(items, expand=stack_data)

    async def studies(
        self,
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
        **kwargs: Unpack[CommonQueryParams],
    ) -> "DataFrame":
        """Query the Fount `studies` endpoint.

        Parameters
        ----------
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
            DataFrame with `studies` endpoint results.
        """
        filters = _filters.StudiesFilters.ensure(
            filters,
            country_codes=country_codes,
            year_numbers=year_numbers,
            full_year=full_year,
            released=released,
            bav_study=bav_study,
        )

        query = Query.ensure(
            query,
            id=study_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,
        )

        items = await self._client.query("studies", query)

        return parse_response(items, expand=stack_data)


def _default_include(
    value: OptionalListOr[str], default: List[str]
) -> OptionalListOr[str]:
    """Appends default includes to the passed value

    Parameters
    ----------
    value : OptionalListOr[str]
        value to add defaults to
    default : List[str]
        Default values to add to `value`

    Returns
    -------
    OptionalListOr[str]
        None if value is `"no_default"`, else returns defaults
        and any includes in `value`
    """
    if value is None:
        return default
    if isinstance(value, list):
        return list(set(default).union(value))
    if value == "no_default":
        return None
    if value in default:
        return value
    return list(set(default).union((value,)))
