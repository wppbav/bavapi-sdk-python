"""Functions to parse parameter values."""

import datetime as dt
from typing import Dict, Mapping, Sequence, TypeVar, Union, cast

from bavapi.typing import BaseMutableParamsMapping, BaseMutableParamsMappingValues

T = TypeVar("T")


def parse_date(value: Union[str, dt.datetime, dt.date]) -> str:
    """Parse date string or datetime value into a date string.

    Parameters
    ----------
    value : str, dt.datetime, dt.date
        Input to parse into a date string.

    Returns
    -------
    str
        The parsed date as a string.
    """
    fmt_out = "%Y-%m-%d %H:%M:%S"
    if isinstance(value, dt.datetime):
        return value.strftime(fmt_out)
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.datetime.min.time()).strftime(fmt_out)
    try:
        return dt.datetime.strptime(value, fmt_out).strftime(fmt_out)
    except ValueError:
        return dt.datetime.fromisoformat(value).strftime(fmt_out)


def to_fount_params(data: Mapping[str, T], param: str) -> Dict[str, T]:
    """Constructs dictionary keys for special Fount API formatting.

    The resulting dictionary keys will be formatted to include `param` as the
    main parameter name:

    >>> to_fount_params({"a":1}, "test")
    {"test[a]":1}

    Parameters
    ----------
    data : dict[str, Any]
        Dictionary to format.
    param : str
        Parameter name.

    Returns
    -------
    dict[str, Any]
        Fount API parameter dictionary.
    """
    return {f"{param}[{k}]": v for k, v in data.items()}


def list_to_str(mapping: BaseMutableParamsMapping) -> BaseMutableParamsMappingValues:
    """Convert any lists in a dictionary to a string with comma-separated elements.

    Parameters
    ----------
    mapping : ParamsMapping
        Dictionary with lists

    Returns
    -------
    ParamsMappingValues
        Dictionary without strings
    """
    for key, value in mapping.items():
        if not isinstance(value, str) and isinstance(value, Sequence):
            mapping[key] = ",".join(str(i) for i in value)

    return cast(BaseMutableParamsMappingValues, mapping)
