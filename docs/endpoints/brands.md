# Brands

The `brands` endpoint has full support, including query validation.

| Endpoint   | Function                | `Client` method                         | Filters class                            |
| ---------- | ----------------------- | --------------------------------------- | ---------------------------------------- |
| `"brands"` | [`brands`][sync.brands] | [`Client.brands`][client.Client.brands] | [`BrandsFilters`][filters.BrandsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`brands`](https://developer.wppbav.com/docs/2.x/core-resources/brands) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.brands("TOKEN", name="Facebook")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.brands(name="Facebook")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `name`, `country_codes`, `year_numbers`
- Keyword filters: `brand_id`, `studies`

For other filters, passing a `BrandsFilters` instance to the `filters` parameter is required.
