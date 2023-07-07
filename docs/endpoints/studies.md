# Studies

The `studies` endpoint has full support, including query validation.

| Endpoint    | Function                  | `Client` method                           | Filters class                              |
| ----------- | ------------------------- | ----------------------------------------- | ------------------------------------------ |
| `"studies"` | [`studies`][sync.studies] | [`Client.studies`][client.Client.studies] | [`StudiesFilters`][filters.StudiesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`studies`](https://developer.wppbav.com/docs/2.x/core-resources/studies) endpoint.

## Usage

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.studies(country_codes="US")
    ```

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.studies("TOKEN", country_codes="US")
    ```
