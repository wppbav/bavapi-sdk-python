"""Filter objects for Fount API queries based on `pydantic`."""

# pylint: disable=no-name-in-module, too-few-public-methods

from typing import Dict, Literal, Mapping, Optional, Type, TypeVar, Union

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
    "BrandscapeFilters",
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
        Request items that have been updated since the specified date, by default None
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
        """Ensure FountFilters class from dictionary or other FountFilters class.

        Parameters
        ----------
        filters : FountFilters or dict of filter values, optional
            Dictionary of filters or FountFilters class.
        **addl_filters : SequenceOrValues, optional
            Additional filters to add to the new FountFilters instance.

        Returns
        -------
        FountFilters, optional
            FountFilters class or None if `filters` is None and no additional filters are passed.

        Notes
        -----
        Defaults to values passed to `filters` when any additional filters overlap.
        """
        addl_filters = {k: v for k, v in addl_filters.items() if v}

        if filters is None:
            if not addl_filters:
                return None
            return cls(**addl_filters)  # type: ignore[arg-type]

        new_filters = addl_filters.copy()

        if isinstance(filters, Mapping):
            new_filters.update(filters)
        else:
            new_filters.update(filters.model_dump(exclude_defaults=True))

        return cls(**new_filters)  # type: ignore[arg-type]


class AudiencesFilters(FountFilters):
    """Filters for the `brands` endpoint.

    See <https://developer.wppbav.com/docs/2.x/core-resources/audiences>
    for more info.

    Attributes
    ----------
    active : Literal[0, 1], optional
        Return active audiences only if set to `1`, by default 0
    inactive : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, by default 0
    public : Literal[0, 1], optional
        Return active audiences only if set to `1`, by default 0
    private : Literal[0, 1], optional
        Return inactive audiences only if set to `1`, by default 0
    groups : int or list[int], optional
        Audience group ID or list of audience group IDs, by default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, by default None
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
        Two-letter ISO-3166 country code or list of country codes, by default None
    year_numbers : int or list[int], optional
        Study years in numerical format (not IDs), by default None
    categories : int or list[int], optional
        Fount category ID or list of category IDs, by default None
    countries : int or list[int], optional
        Fount country ID or list of country IDs, by default None
    regions : int or list[int], optional
        Fount region ID or list of region IDs, by default None
    sectors : int or list[int], optional
        Fount sector ID or list of sector IDs, by default None
    studies : int or list[int], optional
        Fount study ID or list of study IDs, by default None
    years : int or list[int], optional
        Fount year ID or list of year IDs, by default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, by default None
    """

    country_codes: OptionalListOr[str] = None
    year_numbers: OptionalListOr[int] = None
    categories: OptionalListOr[int] = None
    countries: OptionalListOr[int] = None
    regions: OptionalListOr[int] = None
    sectors: OptionalListOr[int] = None
    studies: OptionalListOr[int] = None
    years: OptionalListOr[int] = None


class BrandscapeFilters(FountFilters):
    """Filters for the `studies` endpoint.

    `audiences`, `countries`, `studies`, `years`, `brands` and `categories` filter by
    the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/brandscape-data>
    for more info.

    The `brandscape-data` endpoint requires the use of, at minimum, these filters:

    - `studies`
    - `brand_name` or `brands`
    - `country_code` or `countries` and `brands` or `brand_name`
    - `year_number` or `years` and `country_code` or `countries`

    An audience filter is also highly recommended, as otherwise the API will return
    data for all audiences (there are more than 30 standard audiences).

    The `Audiences` class is provided to make it easier to filter audiences.

    Attributes
    ----------
    country_code : str or list[str], optional
        Two-letter ISO-3166 country code or list of country codes, by default None
    year_number : int or list[int], optional
        Study years in numerical format (not IDs), by default None
    audiences : int or list[int], optional
        Fount ID of the desired audience, by default None

        The `Audiences` class can help with using audience IDs.
    brand_name : str, optional
        Perform a search on the brand name, by default None
    brands : int or list[int], optional
        Fount brand ID or list of brand IDs, by default None
    categories : int or list[int], optional
        Fount category ID or list of category IDs, by default None
    countries : int or list[int], optional
        Fount country ID or list of country IDs, by default None

        The `Countries` class can help with using country IDs.
    studies : int or list[int], optional
        Fount study ID or list of study IDs, by default None
    years : int or list[int], optional
        Fount year ID or list of year IDs, by default None


    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, by default None
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
        if not (
            "brands" in values
            or "brand_name" in values
            or "studies" in values
            or (
                ("country_code" in values or "countries" in values)
                and ("year_number" in values or "years" in values)
            )
        ):
            raise ValueError(
                "You need to apply either the `brands`, or `studies`, or `brand_name` "
                "filters, or the `country_code`/`countries` "
                "and `year_number`/`years` filters together."
            )

        return values


class StudiesFilters(FountFilters):
    """Filters for the `studies` endpoint.

    `years`, `countries` and `regions` filter by the Fount IDs of the specific resources.

    See <https://developer.wppbav.com/docs/2.x/core-resources/studies>
    for more info.

    Attributes
    ----------
    country_codes: str or list[str], optional
        Two-letter ISO-3166 country code or list of country codes, by default None
    year_numbers: int or list[int], optional
        Study years in numerical format (not IDs), by default None
    full_year: Literal[0, 1], optional
        Return full year studies when set to `1` (excludes US quarterly), by default 0
    released: Literal[0, 1], optional
        Return released studies when set to `1`, by default 0
    unreleased: Literal[0, 1], optional
        Return unreleased studies when set to `1`, by default 0
    open_survey: Literal[0, 1], optional
        Return studies with open brand requests when set to `1`, by default 0
    active: Literal[0, 1], optional
        Return active audiences when set to `1`, by default 0
    inactive: Literal[0, 1], optional
        Return inactive audiences when set to `1`, by default 0
    bav_study: Literal[0, 1], optional
        Return full BAV studies when set to `1`, by default 0
    data_updated_since: DTValues, optional
        Return studies updated since datetime value, by default None
    countries: int or list[int], optional
        Fount country ID or list of country IDs, by default None
    regions: int or list[int], optional
        Fount region ID or list of region IDs, by default None
    years: int or list[int], optional
        Fount year ID or list of year IDs, by default None

    Other Parameters
    ----------------
    updated_since : str, date or datetime, optional
        Request items that have been updated since the specified date, by default None
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
