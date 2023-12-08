# pylint: disable=missing-function-docstring, missing-module-docstring

from typing import Optional

import pytest

from bavapi import filters
from bavapi.query import Query


def test_with_page():
    assert Query(filters={"audience": 1}).with_page(2, 25) == Query(
        page=2, per_page=25, filters={"audience": 1}
    )


def test_paginated():
    paginated = tuple(Query(filters={"audience": 1}).paginated(10, 100))

    assert len(paginated) == 10
    assert [p.page for p in paginated] == list(range(1, 11))


def test_to_params_no_filters_no_fields():
    assert Query(id=1).to_params("test") == {}


@pytest.mark.parametrize(
    "query",
    (
        Query(id=1, filters={"name": 1}, fields="metric"),
        Query(
            id=1,
            filters=filters.FountFilters(**{"name": 1}),  # type: ignore[arg-type]
            fields="metric",
        ),
    ),
)
def test_to_params(query: Query):
    assert query.to_params("test") == {
        "filter[name]": 1,
        "fields[test]": "metric",
    }


def test_to_params_dict_filters():
    query = Query(id=1, filters={"name": 1})
    query.filters = {"name": 1}

    assert query.to_params("test") == {"filter[name]": 1}


@pytest.mark.parametrize(
    "kwargs",
    (
        {"page": 2},
        {"max_pages": 1},
    ),
)
def test_is_single_page(kwargs: dict):
    query = Query(**kwargs)
    assert query.is_single_page()


@pytest.mark.parametrize(
    "kwargs",
    (
        {},
        {"per_page": 10, "max_pages": 10},
        {"page": 2, "per_page": 10, "max_pages": 10},
    ),
)
def test_is_not_single_page(kwargs: dict):
    query = Query(**kwargs)
    assert not query.is_single_page()


@pytest.mark.parametrize(("query_param"), (Query(), None))
def test_ensure_always_returns(query_param: Optional[Query]):
    query = Query.ensure(query_param)
    assert isinstance(query, Query)


def test_ensure_addl_params():
    query = Query.ensure(per_page=100, include=["a", "b"])
    assert query.per_page == 100
    assert query.include == ["a", "b"]


def test_ensure_query_over_addl():
    query = Query.ensure(Query(metric_keys=["a", "b"]), metric_keys=[])
    assert query.metric_keys == ["a", "b"]


def test_ensure_filters_same_type():
    query = Query.ensure(Query(filters=filters.FountFilters()))
    assert isinstance(query.filters, filters.FountFilters)
