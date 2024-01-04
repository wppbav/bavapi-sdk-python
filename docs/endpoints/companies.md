# Companies

!!! abstract "New in `v1.0`"

The `companies` endpoint has full support, including query validation.

| Endpoint      | Function                      | `Client` method                               | Filters class                                  |
| ------------- | ----------------------------- | --------------------------------------------- | ---------------------------------------------- |
| `"companies"` | [`companies`][sync.companies] | [`Client.companies`][client.Client.companies] | [`CompaniesFilters`][filters.CompaniesFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`companies`](https://developer.wppbav.com/docs/2.x/core-resources/companies) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.companies("TOKEN", name="Alphabet")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.companies(name="Alphabet")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `public`, `private`, `brands`
- Keyword filters: `company_id`

For other filters, passing a `CompaniesFilters` instance to the `filters` parameter is required.
