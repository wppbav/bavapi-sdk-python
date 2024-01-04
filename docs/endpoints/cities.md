# Cities

!!! abstract "New in `v1.0`"

The `cities` endpoint has full support, including query validation.

| Endpoint   | Function                | `Client` method                         | Filters class                            |
| ---------- | ----------------------- | --------------------------------------- | ---------------------------------------- |
| `"cities"` | [`cities`][sync.cities] | [`Client.cities`][client.Client.cities] | [`CitiesFilters`][filters.CitiesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`cities`](https://developer.wppbav.com/docs/2.x/core-resources/cities) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.cities("TOKEN", name="London")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.cities(name="London")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `capitals`, `countries`, `in_best_countries`
- Keyword filters: `city_id`

For other filters, passing a `CitiesFilters` instance to the `filters` parameter is required.
