# Studies

The `studies` endpoint has full support, including query validation.

| Endpoint    | Function                  | `Client` method                           | Filters class                              |
| ----------- | ------------------------- | ----------------------------------------- | ------------------------------------------ |
| `"studies"` | [`studies`][sync.studies] | [`Client.studies`][client.Client.studies] | [`StudiesFilters`][filters.StudiesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`studies`](https://developer.wppbav.com/docs/2.x/core-resources/studies) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.studies("TOKEN", country_codes="US")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.studies(country_codes="US")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `country_codes`, `year_numbers`, `full_year`, `released`, `bav_study`
- Keyword filters: `study_id`

For other filters, passing a `StudiesFilters` instance to the `filters` parameter is required.
