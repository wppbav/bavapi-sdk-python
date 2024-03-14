"""Common parameter types"""

# pylint: disable=missing-class-docstring, useless-import-alias, unused-import

import datetime
import sys
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    import httpx

if sys.version_info < (3, 12):
    from typing_extensions import Unpack as Unpack
else:
    from typing import Unpack as Unpack

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec as ParamSpec
else:
    from typing import ParamSpec as ParamSpec

T = TypeVar("T")

# VALUE PRIMITIVES

BaseValues = Optional[Union[str, int, float]]
DTValues = Optional[Union[str, datetime.datetime, datetime.date]]

# MUTABLE ABSTRACT COLLECTIONS

SequenceOrValues = Union[T, Sequence[T]]

ParamsMapping = Mapping[str, T]
MutableParamsMapping = MutableMapping[str, T]

BaseSequenceOrValues = SequenceOrValues[BaseValues]
InputSequenceOrValues = Union[BaseSequenceOrValues, DTValues]

BaseParamsMapping = ParamsMapping[BaseSequenceOrValues]
BaseParamsMappingValues = ParamsMapping[BaseValues]
BaseMutableParamsMapping = MutableParamsMapping[BaseSequenceOrValues]
BaseMutableParamsMappingValues = MutableParamsMapping[BaseValues]

InputParamsMapping = ParamsMapping[InputSequenceOrValues]
InputMutableParamsMapping = MutableParamsMapping[InputSequenceOrValues]

# MUTABLE CONCRETE COLLECTIONS

ListOrValues = Union[T, List[T]]

ParamsDict = Dict[str, T]

BaseListOrValues = ListOrValues[BaseValues]
InputListOrValues = Union[BaseListOrValues, DTValues]

BaseParamsDict = ParamsDict[BaseListOrValues]
BaseParamsDictValues = ParamsDict[BaseValues]

InputParamsDict = ParamsDict[InputListOrValues]

# USER-FACING

OptionalSequenceOr = Optional[Union[T, Sequence[T]]]
OptionalListOr = Optional[Union[T, List[T]]]

JSONDict = Dict[str, ListOrValues[Union[BaseValues, "JSONDict"]]]
JSONData = Union[JSONDict, List[JSONDict]]

FlatJSONDict = Dict[str, BaseSequenceOrValues]
FlatJSONDictValues = Dict[str, BaseValues]


class CommonQueryParams(TypedDict, total=False):
    page: Optional[int]
    per_page: Optional[int]
    max_pages: Optional[int]
    sort: Optional[str]


H = TypeVar("H", bound="_HTTP")


class _HTTP(Protocol):
    is_closed: bool

    async def __aenter__(self: H) -> H: ...

    async def __aexit__(self, *_, **__) -> None: ...

    async def aclose(self) -> None: ...

    async def get(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, BaseSequenceOrValues]] = None,
        **kwargs,
    ) -> "httpx.Response": ...


AsyncClientType = Union["httpx.AsyncClient", _HTTP]


class _Query(Protocol):
    """Protocol for Query objects with pagination support"""

    item_id: Optional[int]
    max_pages: Optional[int]
    per_page: Optional[int]
    page: Optional[int]

    def to_params(self, endpoint: str) -> BaseParamsMapping:
        """HTTP-compatible params dictionary"""
        raise NotImplementedError

    def paginated(
        self, n_pages: int, per_page: Optional[int] = None
    ) -> Iterator["_Query"]:
        """Yields Query objects with page parameters for paginated queries"""
        raise NotImplementedError

    def is_single_page(self) -> bool:
        """True if query is for a single page, False for multiple"""
        raise NotImplementedError

    def with_page(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> "_Query":
        """Returns Query with new pagination parameters"""
        raise NotImplementedError


C = TypeVar("C", bound="_HTTPClient")


class _HTTPClient(Protocol):
    per_page: int
    verbose: bool
    batch_size: int
    n_workers: int
    retries: int
    on_errors: Literal["warn", "raise"]
    client: AsyncClientType

    async def __aenter__(self: C) -> C: ...

    async def __aexit__(self, *_, **__) -> None: ...

    async def aclose(self) -> None:
        """Close the connection"""
        raise NotImplementedError

    async def query(
        self,
        endpoint: str,
        query: _Query,
    ) -> Iterator[JSONDict]:
        """Perform a query on the given endpoint"""
        raise NotImplementedError
