# Categories

!!! abstract "New in `v0.10`"

The `categories` endpoint has full support, including query validation.

| Endpoint       | Function                        | `Client` method                                 | Filters class                                    |
| -------------- | ------------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| `"categories"` | [`categories`][sync.categories] | [`Client.categories`][client.Client.categories] | [`CategoriesFilters`][filters.CategoriesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`categories`](https://developer.wppbav.com/docs/2.x/core-resources/categories) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.categories("TOKEN", name="Soap")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.categories(name="Soap")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `name`, `sectors`
- Keyword filters: `category_id`

For other filters, passing a `CategoriesFilters` instance to the `filters` parameter is required.

## Default includes

In order to provide critical information about the data retrieved from `categories`, and to move its structure in line with data downloads from the Fount or BAV's Cultural Rank Tool (CRT), some `include` values are requested by default: `sector`.

```py
# All default (sector) includes will be requested
bavapi.categories("TOKEN", name="All Adults")
```

To suppress default includes, set `include` to `"no_default"`.
