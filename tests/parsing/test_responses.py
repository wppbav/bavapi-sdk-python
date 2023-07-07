# pylint: disable=missing-function-docstring, missing-module-docstring

from typing import Any, Dict, List
from unittest import mock

import pandas as pd
import pytest

from bavapi.parsing import responses


def test_flatten_mapping():
    assert responses.flatten_mapping(
        {
            "other_a": None,
            "test": {"1": 1, "2": 2, "nested": {"a": 3}},  # type: ignore
            "flat": 4,
            "other": {"a": 5},
        },
        prefix="pre",
    ) == {
        "other_a": None,
        "test_1": 1,
        "test_2": 2,
        "test_nested_a": 3,
        "flat": 4,
        "pre_other_a": 5,
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (
            {
                "other_a": None,
                "test": {"1": 1, "2": 2, "nested": {"a": 3}},
                "flat": 4,
                "other": {"a": 5},
            },
            [
                {
                    "other_a": None,
                    "test_1": 1,
                    "test_2": 2,
                    "test_nested_a": 3,
                    "flat": 4,
                    "pre_other_a": 5,
                }
            ],
        ),
        (
            {
                "a": 1,
                "b": [
                    {"c": 1, "d": [{"e": 1}, {"e": 2}]},
                    {"c": 2, "d": [{"e": 1}, {"e": 2}]},
                ],
            },
            [
                {"a": 1, "b_c": 1, "b_d_e": 1},
                {"a": 1, "b_c": 1, "b_d_e": 2},
                {"a": 1, "b_c": 2, "b_d_e": 1},
                {"a": 1, "b_c": 2, "b_d_e": 2},
            ],
        ),
    ),
)
def test_flatten(value: Dict[str, Any], expected: List[Dict[str, Any]]):
    assert list(responses.flatten(value, prefix="pre", expand=True)) == expected


def test_flatten_no_expand():
    value = {
        "a": 1,
        "b": [
            {"c": 1, "d": [{"e": 1}, {"e": 2}]},
            {"c": 2, "d": [{"e": 1}, {"e": 2}]},
        ],
    }

    assert list(responses.flatten(value, expand=False)) == [value]


@mock.patch(
    "bavapi.parsing.responses.pd.DataFrame.transform",
    return_value=pd.DataFrame({"a": [1, 2]}),
)
@mock.patch(
    "bavapi.parsing.responses.pd.DataFrame.dropna",
    return_value=pd.DataFrame({"a": [1, 2]}),
)
def test_parse_response(mock_dropna: mock.Mock, mock_transform: mock.Mock):
    res = responses.parse_response([{"a": 1, "b": None}, {"a": 2, "b": None}])

    assert res.shape == (2, 1)
    mock_dropna.assert_called_once_with(axis=1, how="all")
    mock_transform.assert_called_once_with(pd.to_numeric, errors="ignore")
