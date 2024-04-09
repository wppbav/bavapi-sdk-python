# `bavapi` Roadmap

!!! success "`bavapi` has now reached **stable** (`v1`) status"


## `v2` Roadmap

This is a non-exhaustive list of potential features & changes to `bavapi` for the release of `v2.0`:

### New features

- [ ] Support for the `tools` BAV API namespace and endpoints
- [ ] Support for the `best-countries` BAV API endpoint
- [ ] Support for retrieval of custom aggregations generated via background process in the Fount

### Deprecations

- [ ] Filters and query parameters specified as function arguments. `Query` and the classes in the `bavapi.filters` module should be used instead.
- [ ] Reference generation functionality. It was conceived when references like Audience and Country were static, but custom audiences will remove its usefulness.

#### Changes to filters and query parameters

In `v1`, it is possible to create these valid function calls (all equivalent):

```python
# No pydantic models
bavapi.brands(TOKEN, "Facebook", "US", 2022, filters={"studies": [1, 2, 3]}, include="category")

# Filters as arguments, query as pydantic model
bavapi.brands(TOKEN, "Facebook", "US", 2022, filters={"studies": [1, 2, 3]}, query=Query(include="category"))

# Combined filters into pydantic model
bavapi.brands(
    TOKEN,
    filters=BrandsFilters(
        name="Facebook",
        country_codes="US",
        year_numbers=2022,
        studies=[1, 2, 3]
    ),
    include="category")

# Filters and query as pydantic models, passed separately
bavapi.brands(
    TOKEN,
    filters=BrandsFilters(
        name="Facebook",
        country_codes="US",
        year_numbers=2022,
        studies=[1, 2, 3]
    ),
    query=Query(include="category")
)

# Filters as parameter to query, query as pydantic model
bavapi.brands(
    TOKEN,
    query=Query(
        filters=BrandsFilters(
            name="Facebook",
            country_codes="US",
            year_numbers=2022,
            studies=[1, 2, 3]
        ),
        include="category"
    )
)

# All of the above also work with `bavapi.Client` methods
async with bavapi.Client(TOKEN) as bav:
    client.brands("Facebook", "US", 2022, filters={"studies": [1, 2, 3]}, query=Query(include="category"))
```

It is still undecided which way should be the appropriate call, but it is likely that this will change in favor of a more standardized approach.

## `v1` Roadmap - COMPLETED

This is a non-exhaustive list of potential features & changes to `bavapi` before it is ready for full release:

### Core tooling

- [x] `v0.6.0` ~~`pydantic` V2 support~~
- [x] `v0.9.0` ~~Strict `mypy` support with [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `Unpack` and `TypedDict`~~
- [x] `v0.11.0` ~~Ability to use custom `bavapi.Query` objects in endpoint methods and functions~~
- [x] `v0.11.0` ~~Improved importing experiece when using reference classes created via the `bavapi-gen-refs` command~~
- [x] `v0.12.0` ~~Ability to control pagination for performing a lot of requests.~~

### Known issues

- [x] `v0.13.0` ~~Sporadic `SSL: CERTIFICATE_VERIFY_FAILED` errors when making requests to the Fount API.~~

### Fully-supported endpoints

Eventually, the plan is to support almost all endpoints. This is the current priority list:

- [x] `v0.1.0` ~~Brands~~
- [x] `v0.1.0` ~~Brandscape Data~~
- [x] `v0.1.0` ~~Studies~~
- [x] `v0.4.0` ~~Audiences~~
- [x] `v0.10.0` ~~Categories~~
- [x] `v0.10.0` ~~Collections~~
- [x] `v0.10.0` ~~Brand Metrics~~
- [x] `v0.10.0` ~~Sectors~~
- [x] `v0.10.0` ~~Brand Metric Groups~~
- [x] `v1.0.0` ~~Cities~~
- [x] `v1.0.0` ~~Companies~~
- [x] `v1.0.0` ~~Countries~~
- [x] `v1.0.0` ~~Regions~~
- [x] `v1.0.0` ~~Years~~

### Stretch goals

- [x] `v0.8.1` ~~Smarter flattening of JSON responses, possibly through `pandas.json_normalize`.~~
