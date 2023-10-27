# Tips for using `bavapi` in your projects

## Retry failed requests

There's a sporadic issue where some requests may raise an `SSL: CERTIFICATE_VERIFY_FAILED` error.

While we will continue investigating solutions to the issue, you can use the [`retry`](https://github.com/invl/retry) package to automatically retry requests upon failure.

Here's an example snippet:

```py
from retry.api import retry_call
import ssl
import bavapi

retry_call(bavapi.brands, ("TOKEN", "Facebook"), exceptions=ssl.SSLError, tries=3)
```

This will attempt to make the request 3 times upon failure. If none of the tries succeeds, it will raise an exception.

## Save & load filters and queries

One beneficial side-effect of using `bavapi` is the ability to save specific queries or filters in order to be able to reproduce them later on.

Imagine that you need to share with your team a query that someone else will need to run.

You could share the data if you save the file and then share with them, but another option which might work better if you have to manage multiple audiences/data files is to save the `bavapi` queries and load them for later use.

The recommended (simplest) way to achieve this would be to save the query in a JSON file.

```py
import json

to_save = bavapi.filters.BrandsFilters(name="Facebook", country_code="GB")

with open("my_filters.json", "w", encoding="utf-8") as file:
    json.dump(to_save.model_dump(), file)
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

You can then load the file into a `bavapi.filters` object like so:

```py
with open("my_filters.json", "r", encoding="utf-8") as file:
    loaded = bavapi.filters.BrandsFilters(**json.load(file))
```

This should restore all filter values, so you can use it again with other requests:

```py
>>> loaded
BrandsFilters(name="Facebook", country_code="GB", ...)
```

!!! tip
    This also works for `Query` objects:

    ```py
    to_save = bavapi.Query(...)

    with open("my_query.json", "w", encoding="utf-8") as file:
        json.dump(to_save.model_dump(), file)
    
    # Saved to `my_query.json`

    with open("my_query.json", "r", encoding="utf-8") as file:
        loaded = bavapi.Query(**json.load(file))
    ```

    When saving and re-loading `Query` objects, its filters will be loaded as the base `FountFilters` class. Everything should work normally, but filter values won't be validated.

    For that reason, it is recommended *NOT* to create the filters and query in JSON directly, but to create the query in Python and then dump to JSON, so the values get validated before saving the query to a JSON file.

    !!! abstract "New in `v0.11.0`"

    You can save and load Query objects to be used with any endpoint function or method.

    ```py
    # continuing from code above...
    bavapi.brands(TOKEN, query=loaded) # (1)
    ```

    1. Will use the query parameters loaded form the `my_query.json` file.

    Note that only parameters specified in the `Query` object will be used.

## Using `bavapi` to develop real-time applications

`bavapi` provides asynchronous functionality for embedding `bavapi` into applications.

Please see the [Advanced Usage](advanced.md) section for more information.
