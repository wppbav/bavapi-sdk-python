# Brand Metrics

!!! abstract "New in `v0.10`"

The `brand-metrics` endpoint has full support, including query validation.

| Endpoint          | Function                              | `Client` method                                       | Filters class                                        |
| ----------------- | ------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| `"brand-metrics"` | [`brand_metrics`][sync.brand_metrics] | [`Client.brand_metrics`][client.Client.brand_metrics] | [`BrandMetricsFilters`][filters.BrandMetricsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`brand-metrics`](https://developer.wppbav.com/docs/2.x/core-resources/brand-metrics) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.brand_metrics("TOKEN", name="Differentiation")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.brand_metrics(name="Differentiation")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- `name`
- `metric_id`
- `active`
- `inactive`
- `public`
- `private`
- `groups`

For other filters, passing a `BrandMetricsFilters` instance to the `filters` parameter is required.
