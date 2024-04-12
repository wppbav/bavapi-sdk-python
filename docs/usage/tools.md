# `bavapi` Tools/TurboPitch

!!! abstract "New in `v1.1`"

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/tools)"

The `tools` namespace in `bavapi` and the API enables access to ready-made analyses and frameworks to gain direct insights from BAV data.

Every tool operates by requesting the analysis to be performed on specific brands, categories, markets or audiences, specified by their ID in the Fount.

Because the breadth of filters and parameters is much simpler than the query API endpoints, `pydantic` models are not needed to make requests. Function parameters are still type validated thanks to the [pydantic.validate_call][pydantic.validate_call_decorator.validate_call] decorator.

## Using `bavapi.tools`

The `tools` interface must be used through the `async` interface provided by the [`ToolsClient`][tools.ToolsClient] class:

```py
from bavapi.tools import ToolsClient

async with ToolsClient("TOKEN") as client:  # (1)
    result = await client.brand_worth_map(brands=1, studies=1)
```

1. :lock: Replace `"TOKEN"` with your own API key

You can also manually close the connection instead of using an `async with` block:

```py
from bavapi.tools import ToolsClient

client = ToolsClient("TOKEN")
try:
    result = await client.brand_worth_map(brands=1, studies=1)
finally:
    await client.aclose()  # (1)
```

1. :recycle: Close the connection with the API server

You will need to instantiate a new `ToolsClient` object once you use it inside the `async with` block or call `aclose`.

!!! warning "Different return types by endpoint"
    Each tool will return results with different signatures. Some will return simply `pandas.DataFrame` instances, and others will return a tuple of additional metadata as a JSON dictionary and parsed data as a `pandas.DataFrame`. Please refer to the [documentation][tools.ToolsClient] for specific information on each endpoint method.

    ```py
    await ToolsClient("TOKEN").brand_worth_map(...)  # returns (JSONDict, pd.DataFrame)

    await ToolsClient("TOKEN").brand_personality_match(...)  # returns pd.DataFrame
    ```

## Client settings

Unlike the query API endpoints, these tools do not return paginated results, so many of the parameters to control pagination behavior in the query endpoints are not used. You can still specify the following when initializing `ToolsClient`:

- `auth_token`
- `base_url`
- `user_agent`
- `headers`: if used, don't pass `auth_token` and `user_agent`
- `client`: if used, don't pass `auth_token`, `headers` and `user_agent`
- `retries`

Please refer to the [basic usage](basic.md) section for more information on how to use these configuration parameters.