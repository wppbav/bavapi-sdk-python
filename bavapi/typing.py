"""Common parameter types"""

import datetime
from typing import (
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

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
