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

| Endpoint            | Filters class                                    |
| ------------------- | ------------------------------------------------ |
| `"audiences"`       | [`AudiencesFilters`][filters.AudiencesFilters]   |
| `"brands"`          | [`BrandsFilters`][filters.BrandsFilters]         |
| `"brandscape-data"` | [`BrandscapeFilters`][filters.BrandscapeFilters] |
| `"studies"`         | [`StudiesFilters`][filters.StudiesFilters]       |

!!! warning
    Using a filters class not meant for a specific endpoint will raise a `ValueError`.

    However, using a dictionary instead (as seen in the instructions below) won't raise errors if the dictionary doesn't match the expected filter types. Use the dictionary method with caution.

These classes are available in the `bavapi.filters` module.

Some of the more common filters for each endpoint have been added directly to the `bavapi` functions.

!!! example
    `bavapi.brands` has parameters such as `name`, `country_codes`, `year_numbers`, `brand_id` or `studies`, which you can use directly from the function without creating a filters instance.

However, less commonly used filters, as well as [value filters](#value-filters) must be specified by using the `filters` parameters in each function.

Filters can be specified using a Python dictionary (if you know the name of the filters you need), or directly creating a Filters instance (recommended method):

=== "Filters class"

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

"Value" filters refer to filtering on the values of the data returned by the endpoint, as opposed to filtering via query parameters specified in the Fount API [documentation](https://developer.wppbav.com/docs/2.x/customizing-respons). For example, filtering by category name or by sector in the `brandscape-data` endpoint.

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

These reference classes must be generated on your machine after installation. Please follow the instructions in the [Installation](../getting-started/installation.md#installing-bavapi-reference-classes) section.

The following reference classes are available:

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

## Other query parameters

### Fields

It is possible to specify which fields a response should contain. If so, the API will **only** return those fields.

```py
result = bavapi.brands(name="Swatch", fields=["id", "name"])
result.columns  # will only have ["id", "name"] as columns
```

### Sorting

It is possible to sort the data by a column from the response.

```py
# sorted by name
result = bavapi.brands(name="Swatch", sort="name")

# descending sorted by name (note the '-')
result = bavapi.brands(name="Swatch", sort="-name")
```

Responses are sorted by item id, in ascending order, by default.

### Related data (includes)

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

All requests to the Fount are "paginated", meaning that one must request and receive from the server one page at a time. `bavapi` then combines all responses into one data table.

While the default value for `bavapi` is 100, it is possible to set a custom number of `per_page` elements for each request:

```py
# will send requests for the specified number of elements.
result = bavapi.brands(name="Swatch", per_page=1000)
```

!!! info
    The maximum number of elements per page allowed by the Fount API is `1000`.

You can also set a custom number of `max_pages` for the request, or directly specify the `page` parameter to get a single page of results.

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

    For more advanced uses and significant performance benefits, see [Advanced Usage](advanced) next.
