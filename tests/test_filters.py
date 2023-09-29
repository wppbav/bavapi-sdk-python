# pylint: disable=missing-function-docstring, missing-module-docstring, protected-access

from unittest import mock

import pytest
from pydantic import ValidationError

from bavapi import filters


def test_filters_any_extra_params():
    filters_ = filters.FountFilters(**{"test_param": 1})  # type: ignore[arg-type]

    assert getattr(filters_, "test_param") == 1


def test_filters_parse_date():
    with mock.patch("bavapi.filters.parse_date", return_value=None) as mock_parse:
        filters.FountFilters(updated_since="2022-01-01")

    mock_parse.assert_called_once_with("2022-01-01")


def test_filters_skip_parse_date():
    with mock.patch("bavapi.filters.parse_date") as mock_parse:
        filters.FountFilters(updated_since=None)

    mock_parse.assert_not_called()


def test_studies_parse_date():
    with mock.patch("bavapi.filters.parse_date", return_value=None) as mock_parse:
        filters.StudiesFilters(data_updated_since="2022-01-01")

    mock_parse.assert_called_once_with("2022-01-01")


def test_studies_skip_parse_date():
    with mock.patch("bavapi.filters.parse_date") as mock_parse:
        filters.StudiesFilters(data_updated_since=None)

    mock_parse.assert_not_called()


@pytest.mark.parametrize(
    "values",
    (
        {"brands": [0]},
        {"studies": [0]},
        {"country_code": "", "year_number": 0},
        {"brand_name": ""},
    ),
)
def test_brandscape_query_validator(values):
    filters.BrandscapeFilters(**values)


@pytest.mark.parametrize("values", ({"country_code": ""}, {"year_number": 0}, {}))
def test_brandscape_query_validator_fails(values):
    with pytest.raises(ValidationError):
        filters.BrandscapeFilters(**values)


@pytest.mark.parametrize(
    ("filters_", "expected"),
    (
        (filters.FountFilters(), filters.FountFilters()),
        (
            {"updated_since": "2022-01-01"},
            filters.FountFilters(updated_since="2022-01-01"),
        ),
    ),
)
def test_filters_ensure(filters_, expected):
    assert filters.FountFilters.ensure(filters_) == expected


def test_filters_ensure_no_addl():
    assert filters.FountFilters.ensure(None) is None


@pytest.mark.parametrize(
    ("filters_", "addl_filters"),
    (
        (filters.FountFilters(), {"addl_name": "test"}),
        ({}, {"addl_name": "test"}),
        (None, {"addl_name": "test"}),
    ),
)
def test_ensure_filters_class_w_addl(filters_, addl_filters):
    res = filters.FountFilters.ensure(filters_, **addl_filters)

    assert getattr(res, "addl_name") == "test"
    assert isinstance(res, filters.FountFilters)
