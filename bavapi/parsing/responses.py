"""Functions for parsing Fount API responses"""

from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    TypeVar,
    Union,
    cast,
)

import pandas as pd

T = TypeVar("T")


def flatten_mapping(
    mapping: Mapping[str, Union[T, Mapping[str, T]]],
    parent: str = "",
    sep: str = "_",
    prefix: str = "",
) -> Dict[str, T]:
    """Recursively flattens all nested dictionaries into top level key-value pairs.

    Include prefixes or suffixes if nested keys clash with top-level keys.

    Parameters
    ----------
    mapping : dict[str, Any] or mapping
        Dictionary with potential nested dictionaries
    parent : str
        Parent key for generating children keys, by default ""
    sep : str
        Separator to use between keys and parent keys, by default ""
    prefix: str
        Prefix for nested keys that clash with keys in the top-level mapping, by default ""

        An empty prefix will ignore key conflicts.

    Returns
    -------
    dict[str, Any]
        Flattened dictionary.
    """
    new: Dict[str, T] = {}

    for key, value in mapping.items():
        if parent:
            key = f"{parent}{sep}{key}"

        if isinstance(value, Mapping):
            if prefix and any(
                k.startswith(key)
                for k, v in mapping.items()
                if not isinstance(v, Mapping)
            ):
                key = f"{prefix}{sep}{key}"

            new = {**new, **flatten_mapping(value, key, sep, prefix)}
        else:
            new[key] = value

    return new


def flatten(
    mapping: Mapping[str, Union[T, Mapping[str, T]]],
    parent: str = "",
    sep: str = "_",
    prefix: str = "",
    expand: bool = False,
) -> Iterator[Dict[str, T]]:
    """Recursively flatten all nested mappings and lists in the given mapping.

    Returns an iterator because it expands any nested lists into new dictionaries,
    then yields each repeated dictionary with its corresponding value from the list.

    This is equivalent to a `JOIN` operation in a relational database, where lists
    represent multiple entries on the right table of the `JOIN`.

    Note: If many nested lists are present, this function will generate as many entries
    as the PRODUCT of the nested lists. If the mapping has one nested list with 5
    elements, and another nested list with 5 elements,
    the function will yield 25 (5x5) dictionaries in total.

    Parameters
    ----------
    mapping : dict[str, Any] or mapping
        Dictionary with potential nested dictionaries and lists of dictionaries
    parent : str
        Parent key for generating children keys, by default ""
    sep : str
        Separator to use between keys and parent keys, by default ""
    prefix: str
        Prefix for keys that clash with keys in the top-level mapping, by default ""

        An empty prefix will ignore key conflicts.
    expand : bool, optional
        Whether to expand nested lists into new dictionaries, by default False

    Yields
    ------
    Iterator[dict[str, Any]]
        Yield flattened dictionaries.

        If expand is True and any nested lists are present, yield each resulting
        flattened dictionary.
    """
    new: Dict[str, T] = flatten_mapping(mapping, parent, sep, prefix)
    expand_keys: List[str] = (
        [k for k, v in new.items() if isinstance(v, list)] if expand else []
    )

    if not expand_keys:
        yield new
    else:
        for key in expand_keys:
            values = cast(List[Mapping[str, T]], new[key])
            print(key)
            for val in values:
                for i in flatten(val, key, sep, prefix, expand):
                    yield {**{k: v for k, v in new.items() if k != key}, **i}


def parse_response(
    page: Iterable[Mapping[str, object]],
    prefix: str = "",
    index: Optional[str] = None,
    expand: bool = False,
) -> pd.DataFrame:
    """Parse Fount API JSON into a pandas DataFrame.

    Parameters
    ----------
    page : iterable of dicts with keys of type str
        Page from API response.
    prefix : str, optional
        Prefix to prepend to columns with clashing names, by default `""`
    index : str, optional
        Column name to use as index, by default None.
    expand : bool, optional
        Whether to expand lists of dictionaries into new entries (rows)
        in the resulting DataFrame, by default False.

    Returns
    -------
    pd.DataFrame
        DataFrame of the response data.
    """
    return (
        pd.DataFrame.from_records(
            (i for item in page for i in flatten(item, prefix=prefix, expand=expand)),
            index=index,
        )
        .dropna(axis=1, how="all")
        .transform(pd.to_numeric, errors="ignore")
    )