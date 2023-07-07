# Brandscape Data

The `brandscape-data` endpoint has full support, including query validation.

This is the main entry point to WPPBAV's extensive brand data catalog.

| Endpoint            | Function                                  | `Client` method                                           | Filters class                                    |
| ------------------- | ----------------------------------------- | --------------------------------------------------------- | ------------------------------------------------ |
| `"brandscape-data"` | [`brandscape_data`][sync.brandscape_data] | [`Client.brandscape_data`][client.Client.brandscape_data] | [`BrandscapeFilters`][filters.BrandscapeFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`brandscape-data`](https://developer.wppbav.com/docs/2.x/core-resources/brandscape-data) endpoint.

## Usage

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.brandscape_data(name="Facebook")
    ```

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.brandscape_data("TOKEN", name="Facebook")
    ```

!!! warning
    `brandscape-data` has filters which have a slightly **different** name than for other endpoints:

    - `year_number` instead of `year_numbers`.
    - `country_code` instead of `country_codes`.

    This is to maintain parity with the way the API is structured. Using the wrong spelling of these parameters will likely result in an error.

## Required filters

`brandscape-data` can retrieve brand datasets from an arbitrary combination of studies, audiences and years, so it is possible that the request becomes too large for the server to deliver effectively for all users.

Thus, the `brandscape-data` endpoint has been restricted to require at least one of these specific set of filters:

- `studies`
- `brand_name`/`brands`
- `year_number`/`years` and `brands`/`brand_name`
- `country_code`/`countries` and `brands`/`brand_name`
- `year_number`/`years` and `country_code`/`countries`

If a query does not have any of these combinations of filters, it will raise a `ValidationError`:

```py
bavapi.brandscape_data("TOKEN")  # Error, no filters specified

bavapi.brandscape_data("TOKEN", year_number=2022) # Error, not enough filters

bavapi.brandscape_data("TOKEN", brand_name="Facebook") # OK

bavapi.brandscape_data("TOKEN", country_code="UK", brands=123)  # OK
```

## Default includes

In order to provide critical information about the data retrieved from `brandscape-data`, and to move its structure in line with data downloads from the Fount or BAV's Cultural Rank Tool (CRT), some `include` values are requested by default: `study`, `brand`, `category` and `audience`.

If you add any of these values in the `include` field by themselves, the default won't be used, and `bavapi` will make a request with the specified `include` instead.

If, on the other hand, you request an `include` that is *not* part of the default values, `bavapi` will append that new value to the default `include` values.

```py
# All default includes will be requested
bavapi.brandscape_data("TOKEN", brand_name="Facebook")

# Only the "brand" include will be requested
bavapi.brandscape_data("TOKEN", brand_name="Facebook", include="brand")

# The "company" include will be appended to the default "include" values
bavapi.brandscape_data("TOKEN", brand_name="Facebook", include="company")

```

## Clashing column names

Some includes can have clashing column names with the original data. This happens, for example, with the `"brand"` include, which when expanded will have column names such as `"brand_name"`, which is already present in the `brandscape-data` table.

To circumvent this issue, the response parsing function will append the `"global_"` prefix to includes with potentially clashing names.

As a result, you will see a set of columns, extracted from the `"brand"` include, which will have a `"global_"` prefix in their names.

!!! warning
    This may change in future versions of `bavapi` as the parsing logic is upgraded.

## Metric keys

`brandscape-data` provides a special filter to specify the data *columns* that the response should contain: `metric_keys`.

You can specify the metrics that your response should contain, and the API will include all score types for that metric.

!!! example
    Setting `metric_keys` to `["differentiation", "relevance"]` will instruct the request to only return the following columns:

    - `differentiation_c`
    - `differentiation_rank`
    - `relevance_c`
    - `relevance_rank`
    - Brand information such as `id`, `brand_name`, and `category_name`
    - Any additional columns from the `include` parameter
