# Audiences

The `audiences` endpoint has full support, including query validation.

| Endpoint      | Function                      | `Client` method                               | Filters class                                  |
| ------------- | ----------------------------- | --------------------------------------------- | ---------------------------------------------- |
| `"audiences"` | [`audiences`][sync.audiences] | [`Client.audiences`][client.Client.audiences] | [`AudiencesFilters`][filters.AudiencesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`audiences`](https://developer.wppbav.com/docs/2.x/core-resources/audiences) endpoint.

## Usage

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.audiences(name="All Adults")
    ```

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.audiences("TOKEN", name="All Adults")
    ```
