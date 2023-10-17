# Basic usage

Once you have installed `bavapi` and acquired a token from the Fount, you can start using `bavapi` directly in Python or in a Jupyter Notebook.

```py
import bavapi
```

## Using bavapi

!!! info "SSL Issues"
    It's possible that you get `SSL: CERTIFICATE_VERIFY_FAILED` errors when performing requests with `bavapi`. At the moment, it is not clear to what might be the source of the issue; as it only happens sometimes, and the error doesn't appear to happen with other tested URLs.

    Usually, making the request again solves the issue, but you might have to do so a couple of times if the issue persists.

    :bulb: If you have any thoughts on how to solve this, please open an [issue](https://github.com/wppbav/bavapi-sdk-python/issues/) on GitHub.

You can query the available [endpoints](../endpoints/index.md) with their corresponding methods:

```py
swatch = bavapi.brands("TOKEN", name="Swatch")  # (1)
```

1. :lock: Replace `TOKEN` with your [API key](../getting-started/authentication.md)

These endpoints methods will return a pandas DataFrame containing the data retrieved for your query:

|     | id     | name   | ... |
| --: | :----- | :----- | :-- |
|   0 | 2342   | Swatch | ... |
|   1 | 127896 | Swatch | ... |
| ... | ...    | ...    | ... |

You can make requests to other [endpoints](../endpoints/index.md) in the same way:

```py
uk_studies = bavapi.studies("TOKEN", country_code="GB")

uk22 = bavapi.brandscape_data("TOKEN", year_numbers=2022, country_code="GB", audiences=1)

all_adults = bavapi.audiences("TOKEN", name="All Adults")
```

!!! question "Want to use other endpoints?"
    The BAV API is very extensive, so not all endpoints are fully implemented yet.

    See the [Other endpoints](advanced.md#other-endpoints) section in Advanced Usage.

## Filtering responses

In order to validate the request parameters before sending a bad request, `bavapi` will automatically check that the parameters from your query and filters are of the type expected by the Fount API. If any parameter doesn't conform to the API requirements, `bavapi` will raise a `ValidationError`.

!!! info "What it's doing"
    `bavapi` performs an initial request to make sure the query parameters are valid, and to retrieve information about the number of pages it will need to fetch.

    If the initial request fails, `bavapi` will not perform more requests.

    Similarly, if the initial request returns the entirety of the query (e.g., there are only 10 results and `per_page` is above 10, which it is by default), no further requests will be performed, and instead the data from the initial response will be returned.

Each endpoint has a filter class associated with it, as each endpoint has its own filter requirements:

| Endpoint                | Filters class                                                  |
| ----------------------- | -------------------------------------------------------------- |
| `"audiences"`           | [`AudiencesFilters`][filters.AudiencesFilters]                 |
| `"brand-metric-groups"` | [`BrandMetricGroupsFilters`][filters.BrandMetricGroupsFilters] |
| `"brand-metrics"`       | [`BrandMetricsFilters`][filters.BrandMetricsFilters]           |
| `"brands"`              | [`BrandsFilters`][filters.BrandsFilters]                       |
| `"brandscape-data"`     | [`BrandscapeFilters`][filters.BrandscapeFilters]               |
| `"categories"`          | [`CategoriesFilters`][filters.CategoriesFilters]               |
| `"collections"`         | [`CollectionsFilters`][filters.CollectionsFilters]             |
| `"sectors"`             | [`SectorsFilters`][filters.SectorsFilters]                     |
| `"studies"`             | [`StudiesFilters`][filters.StudiesFilters]                     |

!!! warning
    Using a filters class not meant for a specific endpoint will raise a `ValueError`.

    However, using a dictionary instead (as seen in the instructions below) won't raise errors if the dictionary doesn't match the expected filter types. Use the dictionary method with caution.

These classes are available in the `bavapi.filters` module.

Some of the more common filters for each endpoint have been added directly to the `bavapi` functions. More info in the [endpoints](../endpoints/index.md) section.

!!! example
    `bavapi.brands` has parameters such as `name`, `country_codes`, `year_numbers`, `brand_id` or `studies`, which you can use directly from the function without creating a filters instance.

However, less commonly used filters, as well as [value filters](#value-filters) must be specified by using the `filters` parameters in each function.

Filters can be specified using a Python dictionary (if you know the name of the filters you need), or directly creating a Filters instance:

=== "Filters instances (recommended)"

    ```py
    result = bavapi.brands(
        filters=BrandsFilters(name="Swatch", country_codes=["US", "UK"])
    )
    ```

=== "Dictionary"

    ```py
    result = bavapi.brands(
        filters={"name":"Swatch", "country_codes":["US", "UK"]}
    )
    ```

!!! warning
    If both regular function parameters and filters are specified, the values in the filters parameter will take precedence for the actual request:

    ```py
    result = bavapi.brands(name="Swatch", filters={"name": "Facebook"})
    ```

    The request will use `name="Facebook"`, because values specified in the `filters` parameter take precedence.

### Value filters

"Value" filters refer to filtering on the values of the data returned by the endpoint, as opposed to filtering via query parameters specified in the Fount API [documentation](https://developer.wppbav.com/docs/2.x/customizing/fields). For example, filtering by category name or by sector in the `brandscape-data` endpoint.

These value filters **must** be specified in the `filters` parameter. If they are added to the function call as regular keyword arguments, a `ValidationError` will be raised.

```py
bavapi.brands(name="Swatch", filters={"sector_name": "Watches"})  # ok

bavapi.brands(name="Swatch", sector_name="Watches")  # raises ValidationError
```

When using additional value filters, which might not be available in the arguments to the function call, it is recommended to use the `filters` parameter instead of mixing function parameters and Filters parameters:

```py
bavapi.brands(filters=BrandsFilters(name="Swatch", sector_name="Watches"))
```

## Using *Reference* classes

`bavapi` provides reference classes to make API queries easier to construct.

These reference classes must be generated on your machine after installation. Please follow the instructions in the [Installing Reference Classes](../getting-started/reference-classes.md) section.

The following reference classes are available as of `v0.10`:

- `Audiences`: Audience IDs for all available Fount audiences.
- `Countries`: Country IDs for all available Fount countries.

They make it easier to use these filters, which require Fount IDs to work:

```py
uk22 = bavapi.brandscape_data(
    "TOKEN",
    countries=Countries.UNITED_KINGDOM,
    audiences=Audiences.ALL_ADULTS,
)
```

## Timeout

!!! abstract "New in `v0.8`"

By default, API requests will timeout after 30 seconds in order to avoid hangups.

This may happen more commonly when performing requests with more than 50-100 pages. If you get a `TimeoutError`, you can change this parameter to allow for longer timeouts.

It is possible to set the time before timeout when performing requests with `bavapi`:

=== "Sync"

    ```py
    bavapi.brands(TOKEN, "Facebook", timeout=60)
    ```

=== "Async"

    ```py
    async with bavapi.Client(TOKEN, timeout=60) as bav:
        await bav.brands("Facebook")
    ```

## Suppressing progress bars

!!! abstract "New in `v0.9`"

`bavapi` displays progress bars to show download progress. Each tick in the progress bar refers to individual pages being downloaded.

It's possible to supress progress bar outputs via the `verbose` parameter in function calls and `Client` init methods:

=== Sync (Won't show progress bar)
    ```py
    bavapi.brands(TOKEN, "Facebook", verbose=False)
    ```

=== Async (Won't show progress bar)
    ```py
    async with bavapi.Client(TOKEN, verbose=False) as bav:
        bav.brands("Facebook")
    ```

## Other query parameters

### Fields

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/customizing/fields)"

It is possible to specify which fields a response should contain. If so, the API will **only** return those fields.

```py
result = bavapi.brands(name="Swatch", fields=["id", "name"])
result.columns  # will only have ["id", "name"] as columns
```

### Sorting

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/customizing/filters#sorting-results)"

It is possible to sort the data by a column from the response.

```py
# sorted by name
result = bavapi.brands(name="Swatch", sort="name")

# descending sorted by name (note the '-')
result = bavapi.brands(name="Swatch", sort="-name")
```

Responses are sorted by item id, in ascending order, by default.

### Related data (includes)

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/customizing/includes)"

Aside from the data directly available for each of the resources in the Fount, these resources can also be connected across endpoints.

!!! example
    From the `brands` endpoint, you can request info about a brand's `company`, `sector` or `studies`, among others.

Each endpoint supports different `includes` fields. Please read the Fount API [documentation](https://developer.wppbav.com/docs/2.x/intro) for more info on the specific set of includes supported by each endpoint.

```py
# will include info about the brand's company
result = bavapi.brands(name="Swatch", includes="company")
```

!!! note "Default `includes`"
    The `brandscape_data` function includes `study`, `brand`, `category` and `audience` by default, to align functionality with other sources of data like the Fount website and the Cultural Rank Tool.

### Pagination

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/pagination)"

All requests to the Fount are "paginated", meaning that one must request and receive from the server one page at a time. `bavapi` then combines all responses into one data table.

While the default value for `bavapi` is 100, it is possible to set a custom number of `per_page` elements for each request:

```py
# will send requests for the specified number of elements.
result = bavapi.brands(name="Swatch", per_page=1000)
```

!!! info
    The maximum number of elements per page allowed by the Fount API is `1000`.

You can also set a custom number of `max_pages` for the request, or directly specify the `page` parameter to get a single page of results.

### Metric keys

`metric_keys` is a special filter to specify the data *columns* that the response should contain.

The API response will include all score types for that metric.

!!! note
    Currently, only the `brandscape-data` endpoint supports the use of metric keys. All other endpoints will ignore this parameter.

    More info in the [`brandscape-data`](../endpoints/brandscape-data.md#metric-keys) endpoint section.

## Formatting output

It is possible that some of the data retrieved from the Fount includes multiple items.

!!! example
    For example, requesting the `studies` include in `bavapi.brands` will return a column containing lists of dictionaries with study info for all studies that a brand appears in.

    |     |    id | name     | studies                             |
    | --: | ----: | :------- | :---------------------------------- |
    |   0 | 24353 | Facebook | [{'id': 254, 'name': 'Argentin...}] |
    | ... |   ... | ...      | ...                                 |

`bavapi` has a `stack_data` parameter in its functions and methods that will take those lists of dictionaries and recursively generate a new entry (row) in the resulting DataFrame for each element in the list.

```py
bavapi.brands("Facebook", include="studies", stack_data=True)
```

|     |    id | name     | studies_id | studies_name            | ... |
| --: | ----: | :------- | ---------: | :---------------------- | --- |
|   0 | 24353 | Facebook |        254 | Argentina - Adults 2011 | ... |
|   1 | 24353 | Facebook |        787 | Argentina - Adults 2012 | ... |
| ... |   ... | ...      |        ... | ...                     | ... |

## Datetime in Fount responses

Parsing of datetime values in Fount responses is not currently supported, though it is a planned feature.

For now, parse datetime values manually using `pandas` instead.

!!! tip
    The functions shown in the "Basic usage" section are meant for easy use in Jupyter notebooks, experimentation, one-off scripts, etc.

    For more advanced uses and significant performance benefits, see [Advanced Usage](advanced.md) next.
