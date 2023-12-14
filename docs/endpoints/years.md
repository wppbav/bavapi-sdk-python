# Years

!!! abstract "New in `v1.0.0`"

The `years` endpoint has full support, including query validation.

| Endpoint  | Function              | `Client` method                       | Filters class                          |
| --------- | --------------------- | ------------------------------------- | -------------------------------------- |
| `"years"` | [`years`][sync.years] | [`Client.years`][client.Client.years] | [`YearsFilters`][filters.YearsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`years`](https://developer.wppbav.com/docs/2.x/core-resources/years) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.years("TOKEN", year=2023)
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.years(year=2023)
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `year`
- Keyword filters: `year_id`

For other filters, passing a `YearsFilters` instance to the `filters` parameter is required.
