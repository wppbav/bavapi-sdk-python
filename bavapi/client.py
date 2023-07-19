"""Fount API interface."""

# pylint: disable=too-many-arguments

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
from bavapi.typing import BaseListOrValues, JSONDict, OptionalListOr

if TYPE_CHECKING:
    from types import TracebackType

    from pandas import DataFrame

__all__ = ("Client",)

BASE_URL: Final[str] = "https://fount.wppbav.com/api/v2/"

F = TypeVar("F", bound=_filters.FountFilters)

OptionalFiltersOrMapping = Optional[_filters.FiltersOrMapping[F]]


class Client:
    """Asynchronous API to interact with the WPPBAV Fount.

    This class uses `asyncio` to perform asynchronous requests to the Fount API.

    Asynchronous requests allow you to make multiple requests at the same time,
    extremely helpful for working with a paginated API like the Fount. (returns
    data in multiple pages or requests instead of one single download)

    To use the Client class, you will need to precede calls with `await`:

    ```python
    fount = Client("TOKEN")  # creating instance does not use `await`
    data = await fount.brands("Swatch")  # must use `await`
    ```

    For more information, see the `asyncio` documentation for Python.

    Either `auth_token` or `client` are required to instantiate a Client.

    Parameters
    ----------
    auth_token : str, optional
        Fount API authorization token, by default `''`
    per_page : int, optional
        Default number of entries per page, by default 100
    timeout : float, optional
        Maximum timeout for requests in seconds, by default 30.0
    verify : bool or str, optional
        Verify SSL credentials, by default True

        Also accepts a path string to an SSL certificate file.
    client : HTTPClient, optional
        Authenticated async client from `bavapi.http`, by default None

    Raises
    ------
    ValueError
        If neither `auth_token` nor `client` are provided

    Examples
    --------
    Use `async with` to get data and close the connection.

    This way you get the benefits from `httpx` speed improvements
    and closes the connection when exiting the async with block.

    >>> async with Client("TOKEN") as fount:
    ...     data = await fount.brands("Swatch")

    When not using `async with`, close the connection manually by awaiting `aclose`.

    >>> client = Client("TOKEN")
    >>> data = await fount.brands("Swatch")
    >>> await client.aclose()
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
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        client: HTTPClient = ...,
        per_page: int = 100,
    ) -> None:
        ...

    def __init__(
        self,
        auth_token: str = "",
        per_page: int = 100,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        *,
        client: Optional[HTTPClient] = None,
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
                },
            )

    @property
    def per_page(self) -> int:
        """Default number of items to retrieve per page."""
        return self._client.per_page

    @per_page.setter
    def per_page(self, value: int) -> None:
        self._client.per_page = value

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

    async def raw_query(self, endpoint: str, params: Query[F]) -> List[JSONDict]:
        """Perform a raw GET query to the Fount API, returning the response JSON data
        instead of a `pandas` DataFrame.

        Parameters
        ----------
        endpoint : str
            Endpoint name
        params : Query
            Query `pydantic` model with query parameters.

        Returns
        -------
        list[dict[str, Any]]
            List of JSON response data
        """
        return list(await self._client.query(endpoint, params))

    async def audiences(
        self,
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
            DataFrame with `brands` endpoint results.
        """

        filters = _filters.AudiencesFilters.ensure(
            filters,
            name=name,
            active=active,
            inactive=inactive,
            public=public,
            private=private,
            groups=groups,
        )

        query: Query[_filters.AudiencesFilters] = Query(
            id=audience_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,  # type: ignore[arg-type]
        )

        items = await self._client.query("audiences", query)

        return parse_response(items, expand=stack_data)

    async def brands(
        self,
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
        """Query the Fount `brands` endpoint.

        Parameters
        ----------
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
            DataFrame with `brands` endpoint results.
        """

        filters = _filters.BrandsFilters.ensure(
            filters,
            name=name,
            country_codes=country_codes,
            year_numbers=year_numbers,
            studies=studies,
        )

        query: Query[_filters.BrandsFilters] = Query(
            id=brand_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,  # type: ignore[arg-type]
        )

        items = await self._client.query("brands", query)

        return parse_response(items, expand=stack_data)

    async def brandscape_data(
        self,
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

        This endpoint requires at least one of the following combinations of filters:

        - `studies`
        - `brand_name`
        - `brands`
        - `year_number`/`years` and `brands`/`brand_name`
        - `country_code`/`countries` and `brands`/`brand_name`
        - `year_number`/`years` and `country_code`/`countries`

        An audience filter is also highly recommended, as otherwise the API will return
        data for all audiences (there are more than 30 standard audiences).

        The `Audiences` class is provided to make it easier to filter audiences.

        Note that this endpoint has a default set of `include` resources:
        - `brand`
        - `study`
        - `category`
        - `audience`

        Any additional valid includes will be added to the default set.

        If any of the default includes are used in `include`, then only that resource
        will be retrieved. This is to allow requesting individual includes if they are
        part of the default.

        Parameters
        ----------
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

        query: Query[_filters.BrandscapeFilters] = Query(
            filters=filters,
            fields=fields,
            include=_default_brandscape_include(include),
            metric_keys=metric_keys,
            **kwargs,  # type: ignore[arg-type]
        )

        items = await self._client.query("brandscape-data", query)

        # Prefix 'global' to avoid clashing with 'brand_name' on 'brand' includes
        return parse_response(items, "global", expand=stack_data)

    async def studies(
        self,
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
            DataFrame with `studies` endpoint results.
        """
        filters = _filters.StudiesFilters.ensure(
            filters,
            country_codes=country_codes,
            year_numbers=year_numbers,
            full_year=full_year,
        )

        query: Query[_filters.StudiesFilters] = Query(
            id=study_id,
            filters=filters,
            fields=fields,
            include=include,
            **kwargs,  # type: ignore[arg-type]
        )

        items = await self._client.query("studies", query)

        return parse_response(items, expand=stack_data)


def _default_brandscape_include(value: OptionalListOr[str]) -> OptionalListOr[str]:
    default: Final[List[str]] = ["study", "brand", "category", "audience"]

    if value is None:
        return default
    if isinstance(value, list):
        return list(set(default).union(value))
    if value == "no_default":
        return None
    if value in default:
        return value
    return list(set(default).union((value,)))
