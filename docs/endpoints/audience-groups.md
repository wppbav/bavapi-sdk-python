# Audience Groups

The `audience-groups` endpoint has full support, including query validation.

| Endpoint            | Function                                  | `Client` method                                           | Filters class                                            |
| ------------------- | ----------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| `"audience-groups"` | [`audience_groups`][sync.audience_groups] | [`Client.audience_groups`][client.Client.audience_groups] | [`AudienceGroupsFilters`][filters.AudienceGroupsFilters] |

For more information on available filters and functionality, see the Fount documentation for the [`audience-groups`](https://developer.wppbav.com/docs/2.x/core-resources/audience-groups) endpoint.

## Usage

=== "Sync"

    ```py title="Using top-level functions"
    import bavapi

    result = bavapi.audience_groups("TOKEN", name="All")
    ```

=== "Async"

    ```py title="Using Client asynchronously"
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.audience_groups(name="All")
    ```

## Available filters in function calls

These filters are available directly within the function/method:

- Positional filters: `name`
- Keyword filters: `audience_group_id`

For other filters, passing an `AudienceGroupsFilters` instance to the `filters` parameter is required.
