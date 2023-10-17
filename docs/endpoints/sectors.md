# Sectors

!!! abstract "New in `v0.10`"

The `sectors` endpoint has full support, including query validation.

| Endpoint    | Function                  | `Client` method                           | Filters class                              |
| ----------- | ------------------------- | ----------------------------------------- | ------------------------------------------ |
| `"sectors"` | [`sectors`][sync.sectors] | [`Client.sectors`][client.Client.sectors] | [`SectorsFilters`][filters.SectorsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`sectors`](https://developer.wppbav.com/docs/2.x/core-resources/sectors) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.sectors("TOKEN", name="Distribution")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.sectors(name="Distribution")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- `name`
- `sector_id`
- `in_most_influential`
- `not_in_most_influential`

For other filters, passing a `SectorsFilters` instance to the `filters` parameter is required.
