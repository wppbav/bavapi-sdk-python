"""Common parameter types"""

# pylint: disable=missing-class-docstring, useless-import-alias, unused-import

import datetime
import sys
from typing import (
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
)

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
