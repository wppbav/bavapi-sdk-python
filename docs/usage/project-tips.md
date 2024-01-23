# Tips for using `bavapi` in your projects

## Retry failed requests

!!! tip "New default behavior"
    `bavapi` automatically retries failed requests starting from `v0.13`. The number of retry attempts can be controlled by the `retries` parameter in top-level functions and the `Client` interface. [More info](advanced.md#control-bavapi-behavior).

    If you are using an older version of `bavapi`, this tip should still apply.

You can use the [`retry`](https://github.com/invl/retry) package to automatically retry requests upon failure.

Here's an example snippet:

```py
from retry.api import retry_call
import ssl
import bavapi

retry_call(bavapi.brands, ("TOKEN", "Facebook"), exceptions=ssl.SSLError, tries=3)
```

This will attempt to make the request 3 times upon failure. If none of the tries succeeds, it will raise the exception resulting from the last retry.

## Batch requests

!!! tip "New default behavior"
    `bavapi` automatically batches requests starting from `v0.13`. Number of requests per batch and number of worker coroutines can be controlled by the `batch_size` and `n_workers` parameters in top-level functions and the `Client` interface. [More info](advanced.md#control-bavapi-behavior).

    If you are using an older version of `bavapi`, or you want to work around API rate limits, this tip should still apply.

!!! abstract "New in `v0.12`"

Thanks to the new pagination logic, it is now possible to batch large requests to manage rate limits using `page`, `per_page` and `max_pages`.

```py
import time
from typing import Sequence

import pandas as pd
import bavapi

def make_batched_brand_request(
    query: bavapi.Query,
    batch_size: int,
    per_page: int = 100,
    wait: int = 60,  # BAV API rate limit duration
) -> pd.DataFrame:
    n_items = per_page
    page = query.page or 1
    max_pages = query.max_pages 
    results: list[pd.DataFrame] = []

    def collected_all(results: Sequence[pd.DataFrame]) -> bool:
        return max_pages and len(results) * batch_size >= max_pages

    # Loop if max_pages hasn't been reached OR n_items (per page) still equals per_page
    while not collected_all(results) or n_items == per_page:
        try:
            res = bavapi.brands(query=query.with_page(page, per_page, batch_size))
        except DataNotFoundError:
            break  # If no more data found, in case last page has the same items as per_page
        results.append(res)
        page += batch_size
        n_items = res["id"].nunique()  # Supports `stack_data` functionality
        time.sleep(wait)  # Wait for the rate limit to reset

    return pd.concat(results)  # return all results as one DataFrame
```

With this function you can run:

```py
# Will perform batches of requests for 100 pages and wait 60 seconds
# between batches until all the data is acquired
>>> make_batched_brand_request(query=bavapi.Query(), batch_size=100)
```

## Save & load filters and queries

One beneficial side-effect of using `bavapi` is the ability to save specific queries or filters in order to be able to reproduce them later on.

Imagine that you need to share with your team a query that someone else will need to run.

You could share the data if you save the file and then share with them, but another option which might work better if you have to manage multiple audiences/data files is to save the `bavapi` queries and load them for later use.

The recommended (simplest) way to achieve this would be to save the query in a JSON file.

```py
to_save = bavapi.filters.BrandsFilters(name="Facebook", country_code="GB")

with open("my_filters.json", "w", encoding="utf-8") as file:
    file.write(to_save.model_dump_json())
```

The code above will save your filters as a JSON file:

```json title="my_filters.json"
{
    "updated_since": null,
    "country_codes": "GB",
    "year_numbers": null,
    "categories": null,
    "countries": null,
    "regions": null,
    "sectors": null,
    "studies": null,
    "years": null,
    "name": "Facebook"
}
```

You can then load the file into a `bavapi.filters.BrandsFilters` (or any `FountFilters`) object like so:

```py
import json

with open("my_filters.json", "r", encoding="utf-8") as file:
    loaded = bavapi.filters.BrandsFilters(**json.load(file))
```

This should restore all filter values, so you can use it again with other requests:

```py
>>> loaded
BrandsFilters(name="Facebook", country_code="GB", ...)
```

This also works for `Query` objects:

```py
to_save = bavapi.Query(...)

with open("my_query.json", "w", encoding="utf-8") as file:
    file.write(to_save.model_dump_json(), file)

# Saved to `my_query.json`

with open("my_query.json", "r", encoding="utf-8") as file:
    loaded = bavapi.Query(**json.load(file))
```

When saving and re-loading `Query` objects, its filters will be loaded as the base `FountFilters` class. Everything should work normally, but **filter values won't be validated**.

For that reason, it is recommended *NOT* to create the filters and query in JSON directly, but to create the query in Python and then dump to JSON, so the values get validated before saving the query to a JSON file.

!!! abstract "New in `v0.11`"

You can save and load Query objects to be used with any endpoint function or method.

```py
# continuing from code above...
bavapi.brands("TOKEN", query=loaded) # (1)
```

1. Will use the query parameters loaded from the `my_query.json` file.

Note that only parameters specified in the `Query` object will be used.

## Using `bavapi` to develop real-time applications

`bavapi` provides asynchronous functionality for embedding `bavapi` into applications.

Please see the [Advanced Usage](advanced.md) section for more information.
