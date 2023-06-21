# pylint: disable=missing-function-docstring, missing-module-docstring

import datetime

import pytest

from bavapi.parsing import params


def test_to_fount_params():
    assert params.to_fount_params({"test": 1}, "param") == {"param[test]": 1}


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("2020-07-01 12:00:00", "2020-07-01 12:00:00"),
        (datetime.datetime(2020, 7, 1, 12, 0, 0), "2020-07-01 12:00:00"),
        (datetime.date(2020, 7, 1), "2020-07-01 00:00:00"),
        ("2020-07-01", "2020-07-01 00:00:00"),
    ),
)
def test_parse_date(value, expected):
    assert params.parse_date(value) == expected


@pytest.mark.parametrize(
    "value",
    ("bad_string", "2022-012-02 00:00:00"),
)
def test_parse_date_fails(value):
    with pytest.raises(ValueError):
        params.parse_date(value)


def test_list_to_str():
    parsed = params.list_to_str({"a": [1, 2], "b": 4})

    assert parsed == {"a": "1,2", "b": 4}
