# Basic usage

Once you have installed `bavapi` and acquired a token from the Fount, you can start using `bavapi` directly in Python or in a Jupyter Notebook.

```py
import bavapi
```

## Using bavapi

!!! info "SSL Issues"
    It's possible that you get `SSL: CERTIFICATE_VERIFY_FAILED` errors when performing requests with `bavapi`. At the moment, it is not clear to what might be the source of the issue; as it only happens sometimes, and the error doesn't appear to happen with other tested URLs.

    Usually, making the request again solves the issue, but you might have to do so a couple of times if the issue persists. Here's a temporary [solution](project-tips.md#retry-failed-requests) for the issue.

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

uk22 = bavapi.brandscape_data("TOKEN", year_number=2022, country_code="GB", audiences=12)

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

Each endpoint function has a filter class associated with it, as each endpoint has its own filter requirements:

| Endpoint Function                                 | Filters class                                                  |
| ------------------------------------------------- | -------------------------------------------------------------- |
| [`audiences`][sync.audiences]                     | [`AudiencesFilters`][filters.AudiencesFilters]                 |
| [`brand_metric_groups`][sync.brand_metric_groups] | [`BrandMetricGroupsFilters`][filters.BrandMetricGroupsFilters] |
| [`brand_metrics`][sync.brand_metrics]             | [`BrandMetricsFilters`][filters.BrandMetricsFilters]           |
| [`brands`][sync.brands]                           | [`BrandsFilters`][filters.BrandsFilters]                       |
| [`brandscape_data`][sync.brandscape_data]         | [`BrandscapeFilters`][filters.BrandscapeFilters]               |
| [`categories`][sync.categories]                   | [`CategoriesFilters`][filters.CategoriesFilters]               |
| [`collections`][sync.collections]                 | [`CollectionsFilters`][filters.CollectionsFilters]             |
| [`sectors`][sync.sectors]                         | [`SectorsFilters`][filters.SectorsFilters]                     |
| [`studies`][sync.studies]                         | [`StudiesFilters`][filters.StudiesFilters]                     |

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
    If both regular function parameters and `filters` are specified, the values in the `filters` parameter will take precedence for the actual request:

    ```py
    result = bavapi.brands(name="Swatch", filters={"name": "Facebook"})
    ```

    The request will use `name="Facebook"`, because values specified in the `filters` parameter take precedence.

### Value filters

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/customizing/filters)"

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

They make it easier to use their respective filters, which require Fount IDs to work, rather than remembering each respective ID:

```py
from bavapi_refs import Audiences, Countries

uk22 = bavapi.brandscape_data(
    "TOKEN",
    year_number=2021,
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

=== "Sync (Won't show progress bar)"

    ```py
    bavapi.brands(TOKEN, "Facebook", verbose=False)
    ```

=== "Async (Won't show progress bar)"

    ```py
    async with bavapi.Client(TOKEN, verbose=False) as bav:
        bav.brands("Facebook")
    ```

## Other query parameters

The following query parameters are available for all endpoints (unless stated otherwise).

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
    The `brandscape_data` function includes `study`, `brand`, `category` and `audience` by default, to align functionality with other sources of data like the Fount website and the Cultural Rank Tool. More [info](../endpoints/brandscape-data.md#default-includes). The `categories` function also has [default includes](../endpoints/categories.md#default-includes).

### Pagination

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/pagination)"

All requests to the Fount are "paginated", meaning that one must request and receive from the server one page at a time. `bavapi` then combines all responses into one data table.

!!! abstract "New in `v0.12.0`"

Pagination is controlled by three parameters:

- `page`
- `per_page`
- `max_pages`

If only `page` is set to an integer greater than `0`, that single page will be requested.

```py
bavapi.studies(page=1)  # Will request a single page of data
```

If either `per_page` or `max_pages` are set, `bavapi` will request the appropriate pages from the Fount API. The default `per_page` set by `bavapi` is `100`.

!!! info
    The maximum number of elements per page allowed by the Fount API is `1000`.

`bavapi` will calculate the number of pages from the total items reported by the Fount.

It is also possible to set the number of `max_pages`, which will limit the number of pages requested regardless of the reported total.

```py
# Request pages with 50 items per page
# up to pages calculated from total reported
bavapi.studies(per_page=50)

# Request pages with 100 items (default) per page up to 10
# or pages calculated from total reported, whichever is smaller
bavapi.studies(max_pages=10)

# Request pages with 10 items per page up to 100
# or pages calculated from total reported, whichever is smaller
bavapi.studies(per_page=10, max_pages=100)
```

### Metric and metric group keys

!!! abstract "New in `v0.12.0`"

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/core-resources/brandscape-data#additional-column-customizations)"

`metric_keys` and `metric_group_keys` are special filters to specify the data *columns* that the response should contain.

The API response will include all score types for that metric or metric group.

!!! note
    Currently, only the `brandscape-data` endpoint supports the use of metric and metric group keys. All other endpoints will ignore this parameter. More info in the [`brandscape-data`](../endpoints/brandscape-data.md#metric-and-metric-group-keys) endpoint section.

## Using `Query` objects

!!! abstract "New in `v0.11.0`"

While the available parameters in endpoint functions and methods are provided for convenience, it is possible to use [`bavapi.Query`][query.Query] objects directly inside function calls.

This can be combined with the techniques covered in the [saving query objects](project-tips.md#save--load-filters-and-queries) section of the documentation for powerful reproducibility.

When using `Query` in one of the endpoint methods, only the parameter values specified in the `Query` object will be used.

```py
# will use `name="Facebook"` because `query` values take precedence.
bavapi.brands(name="Swatch", query=bavapi.Query(filters={"name":"Facebook"}))
```

!!! info
    Read more about `Query` in the [Advanced usage](advanced.md#the-query-class) section.

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

!!! tip
    The functions shown in the "Basic usage" section are meant for easy use in Jupyter notebooks, experimentation, one-off scripts, etc.

    For more advanced uses and significant performance benefits, see [Advanced Usage](advanced.md) next.
