# Regions

!!! abstract "New in `v1.0`"

The `regions` endpoint has full support, including query validation.

| Endpoint    | Function                  | `Client` method                           | Filters class                              |
| ----------- | ------------------------- | ----------------------------------------- | ------------------------------------------ |
| `"regions"` | [`regions`][sync.regions] | [`Client.regions`][client.Client.regions] | [`RegionsFilters`][filters.RegionsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`regions`](https://developer.wppbav.com/docs/2.x/core-resources/regions) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.regions("TOKEN", name="Europe")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.regions(name="Europe")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: None
- Keyword filters: `region_id`

For other filters, passing a `RegionsFilters` instance to the `filters` parameter is required.
