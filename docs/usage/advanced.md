---
sidebar_label: Advanced
---

# Advanced Usage

This section is intended for developers who are interested in embedding `bavapi` functionality into their APIs and applications.

!!! note "Async support"
    `bavapi` natively supports asynchronous execution, so it is ready to work with popular `async` libraries such as [`fastapi`](https://fastapi.tiangolo.com/).

## The `Client` interface

The [`Client`][client.Client] class is the backbone of `bavapi`, and it is the recommended way to interact with the Fount for more advanced users.

!!! tip
    If you're familiar with the `requests` or `httpx` python packages, this is similar to using `requests.Session()` or `httpx.Client()`.

Using the `Client` class instead of the top-level endpoint functions (`bavapi.brands`, for example), can bring significant performance improvements, especially when performing multiple requests at the same time.

The `Client` interface is based on `httpx.Client`, so it benefits from all the performance features from `httpx`:

!!! quote "Quote from the `httpx` [docs](https://www.python-httpx.org/advanced/)"
    - Reduced latency across requests (no handshaking).
    - Reduced CPU usage and round-trips.
    - Reduced network congestion.

By using `Client`, you will also get all these benefits, including in Jupyter Notebooks.

## Using the `Client` interface

It is recommended to use `Client` in an `async with` block:

```py
async with bavapi.Client("TOKEN") as bav:
    result = await bav.brands("Swatch")
```

Otherwise, it is possible to use `Client` methods outside of an `async with` block, but it might be slightly less performant.

```py
bav = bavapi.Client("TOKEN")
result = await bav.brands("Swatch")
await bav.aclose()  # (1)
```

1. :recycle: Close the connection by awaiting `aclose` after you're done with your requests.

## Other endpoints

Because of the large number of available endpoints in the Fount and the highly customizable queries, some endpoints won't have extended support from the start.

!!! tip "Open for feedback"
    If you would like to see new endpoints with full type annotation support, please open an [issue](https://github.com/wppbav/bavapi-sdk-python/issues) on GitHub with the Feature Request template.

`bavapi` provides `raw_query` functions/methods to access all the available endpoints without existing endpoint functions/methods:

- [`bavapi.raw_query`][sync.raw_query] for synchronous requests.
- [`bavapi.Client.raw_query`][client.Client.raw_query] for asynchronous requests.

These `raw_query` methods require the use of [`bavapi.Query`][query.Query] instances to make the request:

```py
import bavapi
from bavapi import Query
from bavapi.filters import FountFilters

async with bavapi.Client("TOKEN") as bav:
    res = await bav.raw_query("companies", Query(filters=FountFilters(name="Apple")))
```

These functions will return a list of JSON dictionaries, one for each entry retrieved from the Fount:

```json
[
    {"name": "Apple", "id": 1},
    {"name": "Applebee's", "id": 2},
    // ...
]
```

!!! tip
    These methods are meant to be used for custom processing of data (not resulting in a `pandas` DataFrame), but it is also possible to use some of the parsing functions available in [bavapi.parsing.responses][parsing.responses].

## The `Query` class

[`bavapi.Query`][query.Query] is a `pydantic`-powered class that holds and validates all the common (aside from endpoint-specific filters) query parameters to pass to the Fount API.

The default values for the class are the same as the default values in the Fount API itself, so an empty `Query` object can be used to get all entries for a specific endpoint:

```py
query = bavapi.Query()

async with bavapi.Client("TOKEN") as bav:
    res = await bav.raw_query("brand-metrics", query) # (1)
```

1. :material-expand-all: Returns all entries for `brand-metrics`. Similar to making a `GET` request with no parameters.

`Query` can be used to set limits on the number of pages retrieved, or to request a specific page from a query:

```py
bavapi.Query(
    per_page = 200,
    max_pages = 50,
    ...  # Other params
)
```

### `Query` parameters

All Fount queries performed with [`bavapi.Query`][query.Query] support the following parameters:

- `id`: Return only results for a specific id.
- `page`: The page number of results to return.
- `per_page`: The number of results to return per page. Default is 25 and maximum is 100.
- `max_pages`: The maximum number of pages to request. Defaults to requesting all pages in a query.
- `fields`: The keys for the fields to include in the response. Usually they are the field name in lower case.
- `sort`: The key(s) for the field(s) to order the response results by.
- `include`: Additional linked resources to include in the response.
- `updated_since`: Only return items that have been updated since this timestamp.

For more information on the behavior of each of these parameters, see the [Fount API docs](https://developer.wppbav.com/docs/2.x/customizing/fields).

### Raw parameter dictionary

The `to_params` method can be used to parse the parameters into a dictionary of what will be sent to the Fount API:

```py
>>> bavapi.Query(
...     filters=BrandscapeFilters(
...         brand_name="Facebook",
...         year_numbers=[2012, 2013, 2014, 2015]
...     ),
...     include=["company"]
... ).to_params(endpoint="brandscape-data")  # (1)
{
    "include[brandscape-data]": "company",  # (2)
    "filter[brand_name]": "Facebook",
    "year_numbers": "2012,2013,2014,2015",
}
```

1. Needs the endpoint name to format parameters correctly.
2. :bulb: Parses `filters` and `include` into the correct format for the Fount API, and parses all elements in lists of parameters to their string representation.

## Control `bavapi` batching behavior

!!! abstract "New in `v0.13`"

`bavapi` will automatically batch paginated requests to the API to improve latency and throughput. Default values are set to maintain around twenty concurrent requests at a time.

In addition, `bavapi` will also automatically retry failed requests a number of times (default `2`), which can be defined by the user.

Both top-level functions and the `Client` class have the following parameters to control the behavior of the requests:

- `batch_size`: Number of pages to include in each batch of requests, default `10`.
- `n_workers`: Number of worker coroutines that will make batched requests at once, default `2`.
- `retries`: Number of times to retry a page request before raising an exception, default `3`.
- `on_errors`: Whether to `"warn"` about failed requests at the end of the query, or `"raise"` immediately upon failure (after retries), default `"warn"`.

These parameters can be set in both top-level functions and the async `Client` class:

=== "Sync"

    ```py
    bavapi.brands(
        TOKEN,
        batch_size=5,  # number of requests per batch
        n_workers=5,  # number of concurrent workers
        retries=2,  # number of retry attempts
        on_errors="raise",  # raise on failure after retries
    )
    ```

=== "Async"

    ```py
    async with bavapi.Client(
        TOKEN,
        batch_size=5,  # number of requests per batch
        n_workers=5,  # number of concurrent workers
        retries=2,  # number of retry attempts
        on_errors="raise",  # raise on failure after retries
    ) as client:
        await client.brands()
    ```

The query from the examples above will result in *25* concurrent API requests (5 `batch_size` * 5 `n_workers`), and `bavapi` will retry each failed request *twice* (after the initial request). `on_errors="raise"` will ensure that an exception is raised if all retries for any page result in exceptions.

!!! warning
    In order to avoid SSL and timeout issues, it is recommended to set `batch_size` and `n_workers` so `bavapi` will perform at most 20-30 concurrent requests. The default is 20 concurrent requests (10 `batch_size` * 2 `n_workers`).

## User Agent

!!! abstract "New in `v0.8.0`"

It is possible to set the `User Agent` parameter for HTTP requests.

The default user agent is `"BAVAPI SDK Python"`.

If you want to change the user agent for your application, you can set it when instantiating a `Client`:

```py
bav = bavapi.Client(user_agent="Your User Agent")
```
