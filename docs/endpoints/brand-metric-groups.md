# Brand Metric Groups

!!! abstract "New in `v0.10`"

The `brand-metric-groups` endpoint has full support, including query validation.

| Endpoint          | Function                              | `Client` method                                       | Filters class                                        |
| ----------------- | ------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| `"brand-metric-groups"` | [`brand_metric_groups`][sync.brand_metric_groups] | [`Client.brand_metric_groups`][client.Client.brand_metric_groups] | [`BrandMetricsFilters`][filters.BrandMetricsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`brand-metric-groups`](https://developer.wppbav.com/docs/2.x/core-resources/brand-metric-groups) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.brand_metric_groups("TOKEN", name="Pillars")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.brand_metric_groups(name="Pillars")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `name`, `active`
- Keyword filters: `group_id`

For other filters, passing a `BrandMetricGroupsFilters` instance to the `filters` parameter is required.
