"""Module for interacting with the BAV API's `tools`.

Read more at <https://developer.wppbav.com/docs/2.x/tools>.

Each tool will return very different results, depending on each of their requirements.
Check the return types of each function and method.

Examples
--------

>>> from bavapi.tools import ToolsClient
>>> async with ToolsClient("TOKEN") as client:
>>>     result = await client.commitment_funnel(brands=1, studies=1)
"""

import contextlib
from json import JSONDecodeError
from types import TracebackType
from typing import (
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import httpx
import pandas as pd
from pydantic import validate_call

from bavapi.client import BASE_URL, USER_AGENT
from bavapi.exceptions import APIError
from bavapi._fetcher import aretry
from bavapi.parsing.params import list_to_str
from bavapi.parsing.responses import flatten_mapping, parse_response
from bavapi.typing import (
    AsyncClientType,
    JSONDict,
    ListOrValues,
    MutableParamsMapping,
    OptionalListOr,
    OptionalSequenceOr,
)

__all__ = ("ToolsClient",)

T = TypeVar("T")
Params = MutableParamsMapping[T]


class ToolsClient:
    """Asynchronous API to interact with the WPPBAV Fount API tools.

    Read more at <https://developer.wppbav.com/docs/2.x/tools>.

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
    timeout : float, optional
        Maximum timeout for requests in seconds, default 30.0
    verify : bool or str, optional
        Verify SSL credentials, default True

        Also accepts a path string to an SSL certificate file.
    headers : dict[str, str], optional
        Collection of headers to send with each request, default None
    user_agent : str, optional
        The name of the User-Agent to send to the Fount API, default `''`.

        If no user_agent is set, `bavapi` will use `"BAVAPI SDK Python"` by default.
    client : httpx.AsyncClient, optional
        Authenticated async client, default None

        If `client` is passed, all other parameters will be ignored.
    retries : int, optional
        Number of times to retry a request, default 3

    Raises
    ------
    ValueError
        If neither `auth_token` nor `client` are provided

    Examples
    --------
    Use `async with` to get data and close the connection.

    This way you get the benefits from `httpx` speed improvements
    and closes the connection when exiting the async with block.

    >>> async with ToolsClient("TOKEN") as bav:
    ...     data = await bav.commitment_funnel(brands=1, studies=1)

    When not using `async with`, close the connection manually by awaiting `aclose`.

    >>> bav = ToolsClient("TOKEN")
    >>> data = await bav.commitment_funnel(brands=1, studies=1)
    >>> await bav.aclose()

    If you want to perform multiple endpoint requests with the same `Client`, it is
    recommended to use `verbose=False` to avoid jumping progress bars.

    >>> async with ToolsClient("TOKEN", verbose=False) as bav:
    ...     resp1 = await bav.commitment_funnel(brands=1, studies=1)
    ...     resp2 = await bav.brand_worth_map(brands=1, studies=1)
    """

    C = TypeVar("C", bound="ToolsClient")

    @overload
    def __init__(
        self,
        auth_token: str,
        *,
        base_url: str = ...,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        user_agent: str = "",
        retries: int = 3,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        base_url: str = ...,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        headers: Optional[Dict[str, str]] = ...,
        retries: int = 3,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        client: AsyncClientType = ...,
        retries: int = 3,
    ) -> None: ...

    def __init__(
        self,
        auth_token: str = "",
        *,
        base_url: str = "",
        timeout: float = 30.0,
        verify: Union[bool, str] = True,
        headers: Optional[Dict[str, str]] = None,
        user_agent: str = "",
        client: Optional[AsyncClientType] = None,
        retries: int = 3,
    ) -> None:
        self.retries = retries

        self.client = client or httpx.AsyncClient(
            headers=headers
            or {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json",
                "User-Agent": user_agent or USER_AGENT,
            },
            timeout=timeout,
            verify=verify,
            base_url=base_url or BASE_URL + "tools",
        )

    async def __aenter__(self: C) -> C:
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def aclose(self) -> None:
        """Asynchronously close all client connections."""
        return await self.client.aclose()

    async def _get(
        self,
        endpoint: str,
        params: Params[Union[str, int]],
    ) -> Dict[str, JSONDict]:
        get_func = aretry(self.client.get, self.retries, delay=0.25)  # type: ignore
        resp = await get_func(endpoint, params=params)

        if resp.status_code != 200:
            try:
                message = resp.json()["message"]
            except (KeyError, JSONDecodeError):
                message = "An error occurred with the Fount."

            raise APIError(f"Error {resp.status_code}:\n{message}\nurl={resp.url}")

        return resp.json()

    @overload
    async def archetypes(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        categories: ListOrValues[int] = ...,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @overload
    async def archetypes(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        collections: ListOrValues[int] = ...,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @validate_call
    async def archetypes(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        categories: OptionalListOr[int] = None,
        collections: OptionalListOr[int] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `archetypes` endpoint

        [NOT IMPLEMENTED]
        
        See <https://developer.wppbav.com/docs/2.x/tools/archetypes> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None
        categories : OptionalListOr[int], optional
            Category ID or list of category IDs for the target category, default None
        collections : OptionalListOr[int], optional
            Collection ID or list of collections for the target collection, default None

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        ValueError
            If category or collection are not specified, or if they are both specified
        APIError
            If an error occurs with the query
        """
        if not bool(categories) ^ bool(collections):
            raise ValueError("Either categories OR collections must be specified.")

        raise NotImplementedError

    @validate_call
    async def brand_personality_match(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
    ) -> pd.DataFrame:
        """Retrieve results from the `brand-personality-match` endpoint

        See <https://developer.wppbav.com/docs/2.x/tools/brand-personality-match> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        params = {
            "brands": brands,
            "studies": studies,
            "audiences": audiences,
        }

        resp = await self._get("brand-personality-match", params=_to_url_params(params))

        with raise_if_fails():
            payload = cast(List[JSONDict], resp["data"])
            return parse_response(payload)

    @validate_call
    async def brand_vulnerability_map(
        self,
        brand: int,
    ) -> pd.DataFrame:
        """Retrieve results from the `brand-vulnerability-map` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/brand-vulnerability-map> for more info.

        Parameters
        ----------
        brand : int
            Brand ID

        Returns
        -------
        pd.DataFrame
            Dataframe containing the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        params: Params[Union[str, int]] = {"brand": brand}

        resp = await self._get("brand-vulnerability-map", params=params)

        with raise_if_fails():
            payload = cast(List[JSONDict], resp["data"])
            return parse_response(payload)

    @validate_call
    async def brand_worth_map(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `brand-worth-map` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/brand-worth-map> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        params = {
            "brands": brands,
            "studies": studies,
            "audiences": audiences,
        }

        resp = await self._get("brand-worth-map", params=_to_url_params(params))

        with raise_if_fails():
            payload = cast(JSONDict, resp["data"])
            data = cast(List[JSONDict], payload.pop("data"))
            return payload, parse_response(data)

    @validate_call
    async def category_worth_map(
        self,
        categories: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `category-worth-map` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/category-worth-map> for more info.

        Parameters
        ----------
        categories : ListOrValues[int]
            Category ID or list of category IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        params = {
            "categories": categories,
            "studies": studies,
            "audiences": audiences,
        }

        resp = await self._get("category-worth-map", params=_to_url_params(params))

        with raise_if_fails():
            payload = cast(JSONDict, resp["data"])
            data = cast(List[JSONDict], payload.pop("data"))
            return payload, parse_response(data)

    @validate_call
    async def commitment_funnel(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
    ) -> pd.DataFrame:
        """Retrieve results from the `commitment-funnel` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/commitment-funnel> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        params: dict[str, OptionalSequenceOr[Union[str, int]]] = {
            "brands": brands,
            "studies": studies,
            "audiences": audiences,
        }

        resp = await self._get("commitment-funnel", params=_to_url_params(params))

        def parse_entry(entry: JSONDict) -> MutableParamsMapping[Union[str, float]]:
            metrics = entry.pop("metrics")
            parsed = cast(Dict[str, Union[str, float]], flatten_mapping(entry))
            parsed.update(
                {metric["key"]: metric["value"] for metric in metrics}  # type: ignore[arg-type]
            )
            return parsed

        with raise_if_fails():
            payload = cast(List[JSONDict], resp["data"])
            return pd.DataFrame([parse_entry(entry) for entry in payload])

    @overload
    async def cost_of_entry(
        self,
        brand: int,
        study: int,
        audience: Optional[int] = None,
        *,
        categories: ListOrValues[int] = ...,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @overload
    async def cost_of_entry(
        self,
        brand: int,
        study: int,
        audience: Optional[int] = None,
        *,
        collections: ListOrValues[int] = ...,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @validate_call
    async def cost_of_entry(
        self,
        brand: int,
        study: int,
        audience: Optional[int] = None,
        *,
        categories: OptionalListOr[int] = None,
        collections: OptionalListOr[int] = None,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `cost-of-entry` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/cost-of-entry> for more info.

        Parameters
        ----------
        brand : int
            Brand ID
        study : int
            Study ID
        audience : int, optional
            Audience ID, default None
        categories : OptionalListOr[int], optional
            Category ID or list of category IDs for the target category, default None
        collections : OptionalListOr[int], optional
            Collection ID or list of collections for the target collection, default None
        comparison_name : str, optional
            Custom name to give the comparison, default None

            Default behavior is to use the category or collection name.

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        ValueError
            If category or collection are not specified, or if they are both specified
        APIError
            If an error occurs with the query
        """
        if not bool(categories) ^ bool(collections):
            raise ValueError("Either categories OR collections must be specified.")

        params = {
            "brand": brand,
            "study": study,
            "audience": audience,
            "categories": categories,
            "collections": collections,
            "comparisonName": comparison_name,
        }

        resp = await self._get("cost-of-entry", params=_to_url_params(params))

        with raise_if_fails():
            payload = cast(JSONDict, resp["data"])
            data = cast(List[JSONDict], payload.pop("data"))
            return payload, parse_response(data)

    @validate_call
    async def love_plus(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
    ) -> pd.DataFrame:
        """Retrieve results from the `love-plus` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/love-plus> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """

        params: dict[str, OptionalSequenceOr[Union[str, int]]] = {
            "brands": brands,
            "studies": studies,
            "audiences": audiences,
        }

        resp = await self._get("love-plus", params=_to_url_params(params))

        def parse_entry(
            entry: JSONDict,
        ) -> MutableParamsMapping[Union[int, str, float]]:
            data = cast(Dict[str, JSONDict], entry.pop("data"))
            parsed = cast(Dict[str, Union[str, float]], flatten_mapping(entry))
            parsed.update(
                {metric: val["value"] for metric, val in data.items()}  # type: ignore[arg-type]
            )
            return parsed

        with raise_if_fails():
            payload = cast(List[JSONDict], resp["data"])
            return pd.DataFrame([parse_entry(entry) for entry in payload])

    @validate_call
    async def partnership_exchange_map(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        comparison_brands: ListOrValues[int],
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `partnership-exchange-map` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/partnership-exchange-map> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        comparison_brands : ListOrValues[int]
            Brand ID for comparison with the brand specified in `brands

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """

        params: Params[OptionalSequenceOr[Union[int, str]]] = {
            "brands": brands,
            "studies": studies,
            "comparison_brands": comparison_brands,
        }

        resp = await self._get(
            "partnership-exchange-map", params=_to_url_params(params)
        )

        with raise_if_fails():
            payload = cast(JSONDict, resp["data"])
            data = cast(List[JSONDict], payload.pop("data"))
            return payload, parse_response(data)

    @overload
    async def swot(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        categories: ListOrValues[int] = ...,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @overload
    async def swot(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        collections: ListOrValues[int] = ...,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]: ...

    @validate_call
    async def swot(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        categories: OptionalListOr[int] = None,
        collections: OptionalListOr[int] = None,
        comparison_name: Optional[str] = None,
    ) -> Tuple[JSONDict, pd.DataFrame]:
        """Retrieve results from the `swot` endpoint
        
        See <https://developer.wppbav.com/docs/2.x/tools/swot> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None
        categories : OptionalListOr[int], optional
            Category ID or list of category IDs for the target category, default None
        collections : OptionalListOr[int], optional
            Collection ID or list of collections for the target collection, default None
        comparison_name : str, optional
            Custom name to give the comparison, default None

            Default behavior is to use the category or collection name.

        Returns
        -------
        Tuple[JSONDict, pd.DataFrame]
            A tuple containing a JSON dictionary of metadata and a Dataframe with the results

        Raises
        ------
        ValueError
            If category or collection are not specified, or if they are both specified
        APIError
            If an error occurs with the query
        """
        if not bool(categories) ^ bool(collections):
            raise ValueError("Either categories OR collections must be specified.")

        params = {
            "brands": brands,
            "studies": studies,
            "audiences": audiences,
            "categories": categories,
            "collections": collections,
            "comparisonName": comparison_name,
        }

        resp = await self._get("swot", params=_to_url_params(params))

        with raise_if_fails():
            payload = cast(JSONDict, resp["data"])
            data = cast(List[JSONDict], payload.pop("data"))
            return payload, parse_response(data)

    @validate_call
    async def toplist_market(
        self,
        brands: ListOrValues[int],
        studies: ListOrValues[int],
        audiences: OptionalListOr[int] = None,
        *,
        metrics: OptionalListOr[int] = None,
        metric_keys: OptionalListOr[str] = None,
    ) -> pd.DataFrame:
        """Retrieve results from the `toplist-market` endpoint

        [NOT IMPLEMENTED]
        
        See <https://developer.wppbav.com/docs/2.x/tools/toplist-market> for more info.

        Parameters
        ----------
        brands : ListOrValues[int]
            Brand ID or list of brand IDs
        studies : ListOrValues[int]
            Study ID or list of study IDs
        audiences : OptionalListOr[int], optional
            Audience ID or list of audience IDs, default None
        metrics : OptionalListOr[int], optional
            Metric ID or list of metric IDs, default None
        metric_keys : OptionalListOr[str], optional
            Metric key or list of metric keys, default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing the results

        Raises
        ------
        APIError
            If an error occurs with the query
        """
        raise NotImplementedError


@contextlib.contextmanager
def raise_if_fails() -> Generator[None, None, None]:
    try:
        yield
    except (ValueError, TypeError, KeyError) as exc:
        raise APIError("Could not parse response") from exc


def _to_url_params(
    params: MutableParamsMapping[OptionalSequenceOr[Union[str, int]]]
) -> MutableParamsMapping[Union[str, int]]:
    return list_to_str({k: v for k, v in params.items() if v})
