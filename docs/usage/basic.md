# Basic usage

Once you have installed `bavapi` and acquired a token from the Fount, you can start using `bavapi` directly in Python or in a Jupyter Notebook.

```py
import bavapi
```

## Using bavapi

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

!!! tip
    You can also use `bavapi` Reference classes to define more readable filters. See more in [Reference classes](../getting-started/reference-classes.md).

```py
uk_studies = bavapi.studies("TOKEN", country_code="GB")

uk22 = bavapi.brandscape_data("TOKEN", year_number=2022, country_code="GB", audiences=12)

all_adults = bavapi.audiences("TOKEN", name="All Adults")
```

!!! question "Want to use other endpoints?"
    The BAV API is very extensive, so not all endpoints are fully implemented yet.

    To query unsupported endpoints see the [Other endpoints](advanced.md#other-endpoints) section in Advanced Usage.

## `bavapi` query parameters

In order to validate the request parameters before sending a bad request, `bavapi` will automatically check that the parameters from your query and filters are of the type expected by the Fount API. If any parameter doesn't conform to the API requirements, `bavapi` will raise a `ValidationError`.

!!! info "What it's doing"
    `bavapi` performs an initial request to make sure the query parameters are valid, and to retrieve information about the number of pages it will need to fetch.

    If the initial request fails, `bavapi` will not perform more requests.

    Similarly, if the initial request returns the entirety of the query (e.g., there are only 10 results and `per_page` is above 10, which it is by default), no further requests will be performed, and instead the data from the initial response will be returned.

### Filters

Each endpoint function has a filter class associated with it, as each endpoint has its own filter requirements:

| Endpoint Function                                 | Filters class                                                  |
| ------------------------------------------------- | -------------------------------------------------------------- |
| [`audiences`][sync.audiences]                     | [`AudiencesFilters`][filters.AudiencesFilters]                 |
| [`audience_groups`][sync.audience_groups]                     | [`AudienceGroupsFilters`][filters.AudienceGroupsFilters]                 |
| [`brand_metric_groups`][sync.brand_metric_groups] | [`BrandMetricGroupsFilters`][filters.BrandMetricGroupsFilters] |
| [`brand_metrics`][sync.brand_metrics]             | [`BrandMetricsFilters`][filters.BrandMetricsFilters]           |
| [`brands`][sync.brands]                           | [`BrandsFilters`][filters.BrandsFilters]                       |
| [`brandscape_data`][sync.brandscape_data]         | [`BrandscapeFilters`][filters.BrandscapeFilters]               |
| [`categories`][sync.categories]                   | [`CategoriesFilters`][filters.CategoriesFilters]               |
| [`cities`][sync.cities]                           | [`CitiesFilters`][filters.CitiesFilters]                       |
| [`collections`][sync.collections]                 | [`CollectionsFilters`][filters.CollectionsFilters]             |
| [`companies`][sync.companies]                     | [`CompaniesFilters`][filters.CompaniesFilters]                 |
| [`countries`][sync.countries]                     | [`CountriesFilters`][filters.CountriesFilters]                 |
| [`sectors`][sync.sectors]                         | [`SectorsFilters`][filters.SectorsFilters]                     |
| [`studies`][sync.studies]                         | [`StudiesFilters`][filters.StudiesFilters]                     |
| [`years`][sync.years]                             | [`YearsFilters`][filters.YearsFilters]                         |

!!! warning
    Using a filters class not meant for a specific endpoint won't raise any errors from the outset, but it also won't provide IDE type support or type validation to the parameters that are associated with each endpoint.

    Similarly, using a dictionary (as seen in the example below) won't provide validation or type hints. Use the dictionary method with caution.

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

#### Value filters

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

### Includes (related data)

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

!!! abstract "New in `v0.12`"

Pagination is controlled by three parameters:

- `page`
- `per_page`
- `max_pages`

If only `page` is set to an integer greater than `0`, that single page will be requested.

```py
bavapi.studies(page=1)  # Will request a single page of data
```

If either `per_page` or `max_pages` are set, `bavapi` will request the appropriate pages from the Fount API.

While the Fount API default is `25`, the default `per_page` set by `bavapi` is `100`.

!!! info
    The maximum number of elements per page allowed by the Fount API is `1000`.

`bavapi` will calculate the number of pages from the total items reported by the Fount.

It is also possible to set the number of `max_pages`, which will limit the number of pages requested regardless of the reported total.

The `page` value will be used as the starting page for the request. Therefore, if `page=10` and, for example, `max_pages=30`, `bavapi` will request pages `10` to `40`.

```py
# Request pages with 50 items per page
# up to pages calculated from total reported
bavapi.studies("TOKEN", per_page=50)

# Request pages with 100 items (default) per page up to 10 pages
# or pages calculated from total reported, whichever is smaller
bavapi.studies("TOKEN", max_pages=10)

# Request pages with 10 items per page up to 100 pages
# or pages calculated from total reported, whichever is smaller
bavapi.studies("TOKEN", per_page=10, max_pages=100)

# Request pages with 100 items (default) per page from page 3 to 33
# or pages calculated from total reported, whichever is smaller
bavapi.studies("TOKEN", page=3, max_pages=30)
```

### Metric and metric group keys

!!! abstract "New in `v0.12`"

!!! info "Read more in the [API documentation](https://developer.wppbav.com/docs/2.x/core-resources/brandscape-data#additional-column-customizations)"

`metric_keys` and `metric_group_keys` are special filters to specify the data *columns* that the response should contain.

The API response will include all score types for that metric or metric group.

!!! note
    Currently, only the `brandscape-data` endpoint supports the use of metric and metric group keys. All other endpoints will ignore this parameter. More info in the [`brandscape-data`](../endpoints/brandscape-data.md#metric-and-metric-group-keys) endpoint section.

## Using `Query` objects

!!! abstract "New in `v0.11`"

While the available parameters in endpoint functions and methods are provided for convenience, it is possible to use [`bavapi.Query`][query.Query] objects directly inside function calls.

This can be combined with the techniques covered in the [saving query objects](project-tips.md#save--load-filters-and-queries) section of the documentation for powerful reproducibility.

Similarly to filters objects, when using `Query` in one of the endpoint methods, the parameter values specified in the `Query` object will take precedence over parameters specified at the function level.

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

## Suppressing progress bars

!!! abstract "New in `v0.9`"

`bavapi` displays progress bars to show download progress. Each tick in the progress bar refers to individual pages being downloaded.

It's possible to supress progress bar outputs via the `verbose` parameter in function calls and `Client` init methods:

=== "Sync (Won't show progress bar)"

    ```py
    bavapi.brands("TOKEN", "Facebook", verbose=False)
    ```

=== "Async (Won't show progress bar)"

    ```py
    async with bavapi.Client("TOKEN", verbose=False) as bav:
        bav.brands("Facebook")
    ```

## Timeout

!!! abstract "New in `v0.8`"

By default, API requests will timeout after 30 seconds in order to avoid hangups.

It is possible to set the time before timeout when performing requests with `bavapi`:

=== "Sync"

    ```py
    bavapi.brands("TOKEN", "Facebook", timeout=60)
    ```

=== "Async"

    ```py
    async with bavapi.Client("TOKEN", timeout=60) as bav:
        await bav.brands("Facebook")
    ```

## Error handling

!!! abstract "New in `v0.13`"

### Warn or raise when a page fails to download

You can control the error handling behavior of `bavapi` by changing the `on_errors` parameter in top-level functions and the `Client` interface.

Options and examples:

- `"warn"` (default): Will return all successfully downloaded data, and warn at the end about any pages that failed downloading so they can be manually retried.
- `"raise"`: Will raise any exception that occurs immediately. This was the default behavior until `v0.13`.

=== "Warn"

    ```py
    >>> bavapi.brands("TOKEN", "Facebook", verbose=False, on_errors="warn") # Fails page 1
    UserWarning: Could not fetch pages: ["page 1: Exception(...)"]  # Does not raise
    ```

=== "Raise"

    ```py
    >>> bavapi.brands("TOKEN", "Facebook", verbose=False, on_errors="raise") # Fails page 1
    Exception: ...  # Raised
    ```

!!! warning "Some requests may still raise"
    During the initial handshake between `bavapi` and the Fount API, only SSL errors are retried. Therefore, some queries may still raise exceptions even if `on_errors` is set to `"warn"`:

    - Invalid parameters will raise a `ValidationError` if they are not of the correct Python type
    - Server errors will raise an `APIError` with additional details about the issue
    - Queries with no results found will raise a `DataNotFoundError`
    - Requests which exceed the user's rate limit will raise a `RateLimitExceededError`

### Retry failed requests

`bavapi` will automatically retry requests that fail because of an exception. The number of retry attempts can be controlled via the `retries` parameter in top-level functions and the `Client` interface:

```py
bavapi.brands("TOKEN", retries=5)  # Will retry pages 5 times after original failure
```

!!! tip
    There are some additional, advanced options for controlling the behavior of `bavapi` requests. More info in the [Control `bavapi` batching behavior](advanced.md#control-bavapi-batching-behavior) section from the Advanced Usage documentation.
