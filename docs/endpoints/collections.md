# Collections

!!! abstract "New in `v0.10`"

The `collections` endpoint has full support, including query validation.

| Endpoint        | Function                          | `Client` method                                   | Filters class                                      |
| --------------- | --------------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| `"collections"` | [`collections`][sync.collections] | [`Client.collections`][client.Client.collections] | [`CollectionsFilters`][filters.CollectionsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`collections`](https://developer.wppbav.com/docs/2.x/core-resources/collections) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.collections("TOKEN", name="Unilever")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.collections(name="Unilever")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- `name`
- `public`
- `shared_with_me`
- `mine`

For other filters, passing a `CollectionsFilters` instance to the `filters` parameter is required.
