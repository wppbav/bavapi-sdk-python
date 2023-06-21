"""Common parameter types"""

import datetime
from typing import Mapping, MutableMapping, Optional, Sequence, TypeVar, Union

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

ListOrValues = Union[T, list[T]]

ParamsDict = dict[str, T]

BaseListOrValues = ListOrValues[BaseValues]
InputListOrValues = Union[BaseListOrValues, DTValues]

BaseParamsDict = ParamsDict[BaseListOrValues]
BaseParamsDictValues = ParamsDict[BaseValues]

InputParamsDict = ParamsDict[InputListOrValues]

# USER-FACING

OptionalSequenceOr = Optional[Union[T, Sequence[T]]]
OptionalListOr = Optional[Union[T, list[T]]]

JSONDict = dict[str, ListOrValues[Union[BaseValues, "JSONDict"]]]
JSONData = Union[JSONDict, list[JSONDict]]

FlatJSONDict = dict[str, BaseSequenceOrValues]
FlatJSONDictValues = dict[str, BaseValues]
