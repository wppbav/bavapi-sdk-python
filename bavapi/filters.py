"""
Filter objects for WPPBAV Fount API queries based on `pydantic`.

All endpoint filters are subclasses of `FountFilters`.

You can use any endpoint filter class with `raw_query` functions and methods,
but you must use endpoint-specific filters for each endpoint function or method.

Examples
--------

Use `BrandsFilters` with the `brands` endpoint:

>>> import bavapi
>>> bavapi.brands("TOKEN", filters=bavapi.filters.BrandsFilters(name="Facebook"))

`FountFilters` is compatible with all endpoints (including `raw_query`):

>>> bavapi.brands("TOKEN", filters=bavapi.filters.FountFilters(name="Facebook"))

Using the wrong filter can lead to unexpected results:
>>> bavapi.brands("TOKEN", filters=bavapi.filters.CategoriesFilters(country_codes="UK"))

The above example may work, but it is highly discouraged.
"""

# pylint: disable=no-name-in-module, too-few-public-methods

from typing import Dict, Literal, Optional, Type, TypeVar, Union

from pydantic import BaseModel, field_validator, model_validator

from bavapi.parsing.params import parse_date
from bavapi.typing import (
    DTValues,
    InputParamsMapping,
    InputSequenceOrValues,
    OptionalListOr,
)

__all__ = (
    "FountFilters",
    "AudiencesFilters",
    "BrandsFilters",
    "BrandMetricsFilters",
    "BrandMetricGroupsFilters",
    "BrandscapeFilters",
    "CategoriesFilters",
    "CollectionsFilters",
    "SectorsFilters",
    "StudiesFilters",
)

F = TypeVar("F", bound="FountFilters")

FiltersOrMapping = Union[F, InputParamsMapping]


class FountFilters(BaseModel):
    """Base class for Fount API Filters.

    Can be used with `raw_query` endpoints.

    Attributes
    ----------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    **kwargs : str, int or float, or list of str, int or floats, optional
        Any additional filters to apply to the request, including for columns within
        the response data.
    """

    # Allow arbitrary filters for compatibility with raw_query
    model_config = {"extra": "allow"}

    updated_since: DTValues = None

    @field_validator("updated_since", mode="before")
    @classmethod
    def _parse_date(cls, value: DTValues) -> Optional[str]:
        if value is None:
            return value
        return parse_date(value)

    @classmethod
    def ensure(
        cls: Type[F],
        filters: Optional[FiltersOrMapping["FountFilters"]],
        **addl_filters: InputSequenceOrValues,
    ) -> Optional[F]:
        """Ensure `FountFilters` class from dictionary or other `FountFilters` class.

        Defaults to values passed to `filters` when any additional filters overlap.

        Parameters
        ----------
        filters : FountFilters or dict of filter values, optional
            Dictionary of filters or `FountFilters` class.
        **addl_filters : SequenceOrValues, optional
            Additional filters to add to the new `FountFilters` instance.

        Returns
        -------
        FountFilters, optional
            `FountFilters` class or `None` if `filters` is `None`
            and no additional filters are passed.
        """
        new_filters: Dict[str, InputSequenceOrValues] = {
            k: v for k, v in addl_filters.items() if v
        }

        if filters is None:
            if not new_filters:
                return None
            return cls(**new_filters)  # type: ignore[arg-type]

        if isinstance(filters, FountFilters):
            if not new_filters:
                return cls(**filters.model_dump(exclude_defaults=True))
            new_filters.update(filters.model_dump(exclude_defaults=True))
        else:
            new_filters.update(filters)

        return cls(**new_filters)  # type: ignore[arg-type]


class AudiencesFilters(FountFilters):
    """Filters for the `brands` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/audiences>
    for more info.

    Attributes
    ----------
    active : Literal[0, 1], optional
        Return active audiences only if set to `1`, default 0
    inactive : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, default 0
    public : Literal[0, 1], optional
        Return active audiences only if set to `1`, default 0
    private : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, default 0
    groups : int or list[int], optional
        Audience group ID or list of audience group IDs, default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    active: Literal[0, 1] = 0
    inactive: Literal[0, 1] = 0
    public: Literal[0, 1] = 0
    private: Literal[0, 1] = 0
    groups: OptionalListOr[int] = None


class BrandsFilters(FountFilters):
    """Filters for the `brands` endpoint.

    Filters other than `country_codes` and `year_numbers` filter by
    the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/brands>
    for more info.

    Attributes
    ----------
    country_codes : str or list[str], optional
        Two-letter ISO-3166 country code or list of country codes, default None
    year_numbers : int or list[int], optional
        Study years in numerical format (not IDs), default None
    categories : int or list[int], optional
        Fount category ID or list of category IDs, default None
    countries : int or list[int], optional
        Fount country ID or list of country IDs, default None
    regions : int or list[int], optional
        Fount region ID or list of region IDs, default None
    sectors : int or list[int], optional
        Fount sector ID or list of sector IDs, default None
    studies : int or list[int], optional
        Fount study ID or list of study IDs, default None
    years : int or list[int], optional
        Fount year ID or list of year IDs, default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    country_codes: OptionalListOr[str] = None
    year_numbers: OptionalListOr[int] = None
    categories: OptionalListOr[int] = None
    countries: OptionalListOr[int] = None
    regions: OptionalListOr[int] = None
    sectors: OptionalListOr[int] = None
    studies: OptionalListOr[int] = None
    years: OptionalListOr[int] = None


class BrandMetricsFilters(FountFilters):
    """Filters for the `brand-metrics` endpoint.

    `groups` filters by the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/brand-metrics>
    for more info.

    Attributes
    ----------
    active : Literal[0, 1], optional
        Return active brand metrics when set to `1`, default 0
    inactive : Literal[0, 1], optional
        Return inactive brand metrics when set to `1`, default 0
    public : Literal[0, 1], optional
        Return public brand metrics when set to `1`, default 0
    private : Literal[0, 1], optional
        Return private brand metrics when set to `1`, default 0
    groups : int or list[int], optional
        Fount brand metric group ID or list of group IDs, default None
    current : Literal[0, 1], optional
        Return current brand metrics when set to `1`, default 0
    legacy : Literal[0, 1], optional
        Return legacy brand metrics when set to `1`, default 0
    core : Literal[0, 1], optional
        Return core brand metrics when set to `1`, default 0
    custom : Literal[0, 1], optional
        Return custom brand metrics when set to `1`, default 0

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    active: Literal[0, 1] = 0
    inactive: Literal[0, 1] = 0
    public: Literal[0, 1] = 0
    private: Literal[0, 1] = 0
    groups: OptionalListOr[int] = None
    current: Literal[0, 1] = 0
    legacy: Literal[0, 1] = 0
    core: Literal[0, 1] = 0
    custom: Literal[0, 1] = 0


class BrandMetricGroupsFilters(FountFilters):
    """Filters for the `brand-metric-groups` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/brand-metric-groups>
    for more info.

    Attributes
    ----------
    active : Literal[0, 1], optional
        Return active brand metrics when set to `1`, default 0
    inactive : Literal[0, 1], optional
        Return inactive brand metrics when set to `1`, default 0
    """

    active: Literal[0, 1] = 0
    inactive: Literal[0, 1] = 0


class BrandscapeFilters(FountFilters):
    """Filters for the `studies` endpoint.

    `audiences`, `countries`, `studies`, `years`, `brands` and `categories` filter by
    the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/brandscape-data>
    for more info.

    The `brandscape-data` endpoint requires the use of, at minimum, these filters:

    - Study + Audience + Brand + Category
    - Country + Year + Audience
    - Brand + Audience + Country + Year

    You should read these from left to right. A combination of "Study + Audience"
    worksjust as well as "Study + Audience + Brand".
    However, "Category + Audience" will not.

    An audience filter is also highly recommended, as otherwise the API will return
    data for all audiences (there are more than 30 standard audiences).

    The `Audiences` class is provided to make it easier to filter audiences.

    Attributes
    ----------
    country_code : str or list[str], optional
        Two-letter ISO-3166 country code or list of country codes, default None
    year_number : int or list[int], optional
        Study years in numerical format (not IDs), default None
    audiences : int or list[int], optional
        Fount ID of the desired audience, default None

        The `Audiences` class can help with using audience IDs.
    brand_name : str, optional
        Perform a search on the brand name, default None
    brands : int or list[int], optional
        Fount brand ID or list of brand IDs, default None
    categories : int or list[int], optional
        Fount category ID or list of category IDs, default None
    countries : int or list[int], optional
        Fount country ID or list of country IDs, default None

        The `Countries` class can help with using country IDs.
    studies : int or list[int], optional
        Fount study ID or list of study IDs, default None
    years : int or list[int], optional
        Fount year ID or list of year IDs, default None


    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    country_code: OptionalListOr[str] = None
    year_number: OptionalListOr[int] = None
    audiences: OptionalListOr[int] = None
    brand_name: Optional[str] = None
    studies: OptionalListOr[int] = None
    countries: OptionalListOr[int] = None
    years: OptionalListOr[int] = None
    brands: OptionalListOr[int] = None
    categories: OptionalListOr[int] = None

    @model_validator(mode="before")
    @classmethod
    def _check_params(cls, values: Dict[str, object]) -> Dict[str, object]:
        using_country_year = bool(
            set(values).intersection(
                ("country_code", "countries", "year_number", "years")
            )
        )

        if not (
            "brands" in values
            or "brand_name" in values
            or "studies" in values
            or using_country_year
        ):
            raise ValueError(
                "You need to apply either the `brands`, or `studies`, or `brand_name` "
                "filters, or the `country_code`/`countries` "
                "and `year_number`/`years` filters together."
            )

        if using_country_year:
            if not (
                ("country_code" in values or "countries" in values)
                and ("year_number" in values or "years" in values)
            ):
                raise ValueError(
                    "`country_code`/`countries` and `year_number`/`years` "
                    "filters must be used together."
                )

        return values


class CategoriesFilters(FountFilters):
    """Filters for the `categories` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/categories>
    for more info.

    Attributes
    ----------
    sector : int or list[int], optional
        Fount sector ID or list of sector IDs, default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    sector: OptionalListOr[int] = None


class CollectionsFilters(FountFilters):
    """Filters for the `collections` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/collections>
    for more info.

    Attributes
    ----------
    public : Literal[0, 1], optional
        Return public collections only, default 0
    shared_with_me : Literal[0, 1], optional
        Only return collections that have been shared with the user, default 0
    mine : Literal[0, 1], optional
        Only return collections created by the user, default 0

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    public: Literal[0, 1] = 0
    shared_with_me: Literal[0, 1] = 0
    mine: Literal[0, 1] = 0


class SectorsFilters(FountFilters):
    """Filters for the `sectors` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/sectors>
    for more info.

    Attributes
    ----------
    in_most_influential : Literal[0, 1], optional
        Sectors that are part of the Most Influential lists, default 0
    not_in_most_influential : Literal[0, 1], optional
        Sectors that are not part of the Most Influential lists, default 0

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    in_most_influential: Literal[0, 1] = 0
    not_in_most_influential: Literal[0, 1] = 0


class StudiesFilters(FountFilters):
    """Filters for the `studies` endpoint.

    `years`, `countries` and `regions` filter by the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/studies>
    for more info.

    Attributes
    ----------
    country_codes : str or list[str], optional
        Two-letter ISO-3166 country code or list of country codes, default None
    year_numbers : int or list[int], optional
        Study years in numerical format (not IDs), default None
    full_year : Literal[0, 1], optional
        Return full year studies when set to `1` (excludes US quarterly), default 0
    released : Literal[0, 1], optional
        Return released studies when set to `1`, default 0
    unreleased : Literal[0, 1], optional
        Return unreleased studies when set to `1`, default 0
    open_survey : Literal[0, 1], optional
        Return studies with open brand requests when set to `1`, default 0
    active : Literal[0, 1], optional
        Return active audiences when set to `1`, default 0
    inactive : Literal[0, 1], optional
        Return inactive audiences when set to `1`, default 0
    bav_study : Literal[0, 1], optional
        Return full BAV studies when set to `1`, default 0
    data_updated_since : DTValues, optional
        Return studies updated since datetime value, default None
    countries : int or list[int], optional
        Fount country ID or list of country IDs, default None
    regions : int or list[int], optional
        Fount region ID or list of region IDs, default None
    years : int or list[int], optional
        Fount year ID or list of year IDs, default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, default None
    """

    country_codes: OptionalListOr[str] = None
    year_numbers: OptionalListOr[int] = None
    full_year: Literal[0, 1] = 0
    released: Literal[0, 1] = 0
    unreleased: Literal[0, 1] = 0
    open_survey: Literal[0, 1] = 0
    active: Literal[0, 1] = 0
    inactive: Literal[0, 1] = 0
    bav_study: Literal[0, 1] = 0
    data_updated_since: DTValues = None
    years: OptionalListOr[int] = None
    countries: OptionalListOr[int] = None
    regions: OptionalListOr[int] = None

    @field_validator("data_updated_since", mode="before")
    @classmethod
    def _parse_date(cls, value: DTValues) -> Optional[str]:
        if value is None:
            return value
        return parse_date(value)
