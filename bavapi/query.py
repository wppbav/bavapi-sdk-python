"""Query objects for Fount API queries based on `pydantic`."""

# pylint: disable=no-name-in-module, too-few-public-methods

from typing import Final, Generic, Iterator, Optional, Set, TypeVar, cast

from pydantic import BaseModel, Field

from bavapi import filters as _filters
from bavapi.parsing.params import list_to_str, to_fount_params
from bavapi.typing import (
    BaseMutableParamsMapping,
    BaseParamsDict,
    BaseParamsDictValues,
    BaseParamsMapping,
    OptionalListOr,
)

__all__ = ("Query",)

F = TypeVar("F", bound=_filters.FountFilters)


class Query(BaseModel, Generic[F]):
    """Base WPPBAV Fount query.

    Attributes
    ----------
    id: int, optional
        Get specific resource by ID, by default None
    filters : FountFilters instance or dict of filter values, optional
        Filters to apply to the query, by default None
    fields: str or list[str], optional
        Specific fields to retrieve from the query, by default None
    include: str or list[str], optional
        Additional resources to retrieve from the query, by default None
    metric_keys: str or list[str], optional
        Key or list of keys for the metrics included in the response, by default None

        Currently, this parameter is only available for the `brandscape-data` endpoint.
    sort: str, optional
        Sort response by field, by default None

        To sort in descending (highest first) order, use a `-` before the field name:
        `sort="-differentiation_rank"`

        Sorts by item ID by default.
    page: int, optional
        Get specific page from paginated response, by default None

        When None, the default value in the Fount is 1
    per_page: int, optional
        Number of items per page, by default None

        When None, the default value in the Fount is 25

        When performing paged queries, Client uses 100 as the default `per_page`.
    max_pages: int, optional
        Maximum number of pages to retrieve, by default None

        When None, all pages will be retrieved with a `per_page` value of 100 by default.
    """

    item_id: Optional[int] = Field(default=None, alias="id")
    filters: Optional[_filters.FiltersOrMapping[F]] = None
    fields: OptionalListOr[str] = None
    include: OptionalListOr[str] = None
    metric_keys: OptionalListOr[str] = None
    sort: Optional[str] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    max_pages: Optional[int] = None

    def to_params(self, endpoint: str) -> BaseParamsDictValues:
        """Return Fount-compatible dictionary of the query.

        Parameters
        ----------
        endpoint : str
            The endpoint for which to format the query

        Returns
        -------
        dict[str, Any]
            Fount-compatible dictionary of the query.
        """
        exclude: Final[Set[str]] = {"filters", "fields", "max_pages"}

        filters: BaseParamsMapping = {}
        fields: BaseMutableParamsMapping = {}

        if isinstance(self.filters, _filters.FountFilters):
            filters = self.filters.model_dump(by_alias=True, exclude_defaults=True)
        elif self.filters is not None:
            filters = cast(BaseParamsDict, self.filters)
        filters = to_fount_params(filters, "filter")
        fields = to_fount_params(
            {endpoint.replace("-", "_"): self.fields} if self.fields else fields,
            "fields",
        )

        params = {
            **self.model_dump(exclude=exclude, by_alias=True, exclude_defaults=True),
            **filters,
            **fields,
        }

        return cast(BaseParamsDictValues, list_to_str(params))

    def with_page(self, page: int, per_page: int) -> "Query[F]":
        """Create new instance of `Query` with page parameters if either is set to default.

        Returns new instance of Query.

        Parameters
        ----------
        page : int
            Current page number
        per_page : int
            Number of results per page

        Returns
        -------
        Query
            New `Query` instance with page parameters.
        """
        if self.page and self.per_page:
            return self

        return self.__class__.model_construct(
            self.model_fields_set.union(  # pylint: disable=no-member
                {"page", "per_page"}
            ),
            page=self.page or page,
            per_page=self.per_page or per_page,
            filters=self.filters,  # avoid turning filters into dictionary
            **self.model_dump(
                by_alias=True,
                exclude={"page", "per_page", "filters"},
                exclude_defaults=True,
            ),
        )

    def paginated(self, per_page: int, n_pages: int) -> Iterator["Query[F]"]:
        """Yield `Query` instances with page parameters for each page in `n_pages`.

        For performing multiple paginated requests.

        Parameters
        ----------
        per_page : int
            Number of results per page
        n_pages : int
            Number of pages for which to generate paginated `Query` instances

        Yields
        ------
        Query
            Query instances with page parameters set.
        """
        yield from (self.with_page(p, per_page) for p in range(1, n_pages + 1))
