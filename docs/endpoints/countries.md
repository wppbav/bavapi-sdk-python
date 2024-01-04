# Countries

!!! abstract "New in `v1.0`"

The `countries` endpoint has full support, including query validation.

| Endpoint      | Function                      | `Client` method                               | Filters class                                  |
| ------------- | ----------------------------- | --------------------------------------------- | ---------------------------------------------- |
| `"countries"` | [`countries`][sync.countries] | [`Client.countries`][client.Client.countries] | [`CountriesFilters`][filters.CountriesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`countries`](https://developer.wppbav.com/docs/2.x/core-resources/countries) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.countries("TOKEN", name="Mexico")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.countries(name="Mexico")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `active`, `regions`, `with_studies`
- Keyword filters: `country_id`, `with_recent_studies`

For other filters, passing a `CountriesFilters` instance to the `filters` parameter is required.
