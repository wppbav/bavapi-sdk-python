# pylint: disable=missing-function-docstring, missing-module-docstring

from unittest import mock

import pytest

from bavapi import filters
from bavapi.query import Query


def test_with_page():
    assert Query(filters={"audience": 1}).with_page(2, 25) == Query(
        page=2, per_page=25, filters={"audience": 1}
    )


def test_with_page_no_construction():
    query = Query(page=2, per_page=25)
    assert query.with_page(1, 10) is query


def test_paginated():
    paginated = tuple(Query(filters={"audience": 1}).paginated(100, 10))

    assert len(paginated) == 10
    assert [p.page for p in paginated] == list(range(1, 11))


@pytest.mark.parametrize(
    "query",
    (
        Query(filters={"name": 1}),
        Query(filters=filters.FountFilters(**{"name": 1})),  # type: ignore[arg-type]
    ),
)
def test_to_params_filters(query: Query):
    with mock.patch(
        "bavapi.query.to_fount_params", return_value={}
    ) as mock_to_fount_params:
        query.to_params("test")

    assert mock_to_fount_params.call_args_list == [
        mock.call({"name": 1}, "filter"),
        mock.call({}, "fields"),
    ]


def test_to_params_fields():
    with mock.patch(
        "bavapi.query.to_fount_params", return_value={}
    ) as mock_to_fount_params:
        Query(fields=["name"]).to_params("test")

    assert mock_to_fount_params.call_args_list == [
        mock.call({}, "filter"),
        mock.call({"test": ["name"]}, "fields"),
    ]
