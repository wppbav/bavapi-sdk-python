---
sidebar_label: Overview
---

# Endpoints

As of `v1.0`, these are the endpoints that have been fully implemented in `bavapi`:

- [`audiences`](audiences.md)
- [`audience-groups`](audience-groups.md)
- [`brand-metrics`](brand-metrics.md)
- [`brand-metric-groups`](brand-metric-groups.md)
- [`brands`](brands.md)
- [`brandscape-data`](brandscape-data.md)
- [`categories`](categories.md)
- [`cities`](cities.md)
- [`collections`](collections.md)
- [`companies`](companies.md)
- [`countries`](countries.md)
- [`sectors`](sectors.md)
- [`studies`](studies.md)
- [`years`](years.md)

"Implemented" in this case means that the endpoint has a corresponding function, `Client` method, and filters class associated with them. More info in each endpoint's respective section linked above.

If an existing endpoint does not appear in the list above, you can still perform queries to it using the `raw_query` function/method (see [below](#other-endpoints)), but `bavapi` won't validate filter parameters.

Examples for each endpoint are available in each of their individual sections, both for the top-level, synchronous functions, and the asynchronous methods in `bavapi.Client`.

For a summary of all existing Fount endpoints, as well as their parameters and supported filters, please see the [Resources](https://developer.wppbav.com/docs/2.x/intro) section of the Fount API documentation.

## Other endpoints

While there are some commonly used endpoints with more extensive validation support, there are a *lot* of additional endpoints available for querying.

With the `raw_query` functions and methods, you can perform requests to any endpoint in the Fount, even if it's not supported with dedicated code.

| Endpoint | Function                      | `Client` method                               | Filters class                          |
| -------- | ----------------------------- | --------------------------------------------- | -------------------------------------- |
| `{any}`  | [`raw_query`][sync.raw_query] | [`Client.raw_query`][client.Client.raw_query] | [`FountFilters`][filters.FountFilters] |

Queries from `raw_query` functions and methods return a list of JSON dictionaries, instead of a `pandas` DataFrame.

!!! note
    You need to use a [`Query`][query.Query] instance to perform queries with `raw_query` methods. [More info](../usage/advanced.md#other-endpoints)

### Usage

=== "Async"

    ```py
    import bavapi

    async with bavapi.Client("TOKEN") as bav:
        result = await bav.raw_query("companies", bavapi.Query())
    ```

=== "Sync"

    ```py
    import bavapi

    result = bavapi.raw_query("TOKEN", "companies", bavapi.Query())
    ```

Since the result of these queries will be a list of JSON dictionaries, you can use the `parse_response` function in the `bavapi.parsing.responses` module to parse the JSON response into a DataFrame:

```py
import bavapi
from bavapi.parsing.responses import parse_response

result = bavapi.raw_query("companies", bavapi.Query())

parsed = parse_response(result)  # will return a DataFrame
```
