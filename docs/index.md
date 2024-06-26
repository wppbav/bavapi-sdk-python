# BAV API Python SDK - `bavapi` documentation

[![CI status](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/nachomaiz/32196acdc05431cd2bc7a8c73a587a8d/raw/covbadge.json)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml)
[![release status](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/release.yml/badge.svg)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/release.yml)
[![docs status](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/docs.yml/badge.svg)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/docs.yml)
[![PyPI](https://img.shields.io/pypi/v/wpp-bavapi)](https://pypi.org/project/wpp-bavapi/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wpp-bavapi)
](https://pypi.org/project/wpp-bavapi/)

WPPBAV provides a python consumer for the [WPPBAV Fount](https://fount.wppbav.com) API.

It is published as `wpp-bavapi` in [PyPI](https://pypi.org/project/wpp-bavapi/) and hosted on [GitHub](https://github.com/wppbav/bavapi-sdk-python/).

With `bavapi` you can access the full BAV data catalog, the largest and most comprehensive database of brand data in the world.

Queries are validated automatically thanks to `pydantic` and retrieved asynchronously via the `httpx` package.

For more information about the Fount API, see the API [documentation](https://developer.wppbav.com/docs/2.x/intro) website.

## Installing `bavapi`

`bavapi` should work with any Python installation above version 3.8.

Install `bavapi` using pip:

```prompt
pip install wpp-bavapi
```

See [Installation](getting-started/installation.md) for more detailed instructions.

## Example usage

!!! info "Protected access"
    :lock: To use `bavapi`, you will need a Fount API token. Read more in the [Authentication](getting-started/authentication.md) section.

```py
>>> import bavapi
>>> result = bavapi.brands("TOKEN", name="Swatch") # (1)
>>> result
```

1. :lock: Replace `"TOKEN"` with your Fount API token.

|     | sector_id | sector_name           | id   | name   | ... |
| --: | :-------- | :-------------------- | :--- | :----- | :-- |
|   0 | 233       | Apparel & Accessories | 8635 | Swatch | ... |
| ... | ...       | ...                   | ...  | ...    | ... |

## Features

- Support for all endpoints in the Fount API.
    - Extended support for the following endpoints:
        - [`audiences`](endpoints/audiences.md)
        - [`audience-groups`](endpoints/audience-groups.md)
        - [`brand-metrics`](endpoints/brand-metrics.md)
        - [`brand-metric-groups`](endpoints/brand-metric-groups.md)
        - [`brands`](endpoints/brands.md)
        - [`brandscape-data`](endpoints/brandscape-data.md)
        - [`categories`](endpoints/categories.md)
        - [`cities`](endpoints/cities.md)
        - [`collections`](endpoints/collections.md)
        - [`companies`](endpoints/companies.md)
        - [`countries`](endpoints/countries.md)
        - [`sectors`](endpoints/sectors.md)
        - [`studies`](endpoints/studies.md)
        - [`years`](endpoints/years.md)
    - Other endpoints are available via the [`raw_query`](endpoints/index.md#other-endpoints) functions and methods.
    - Extended support for Fount API [Tools/TurboPitch](usage/tools.md) endpoints.
- Validates query parameters are of the correct types and provides type hints for better IDE support.
- Retrieve multiple pages of data simultaneously, monitoring and preventing exceeding API rate limit.
- Both synchronous and asynchronous APIs for accessing BAV data.

## Documentation

To start using `bavapi`, go to the [Getting Started](getting-started/authentication.md) section.

After going through the "Getting Started" section, please see [Basic Usage](usage/basic.md).

For more advanced topics, see the [Advanced Usage](usage/advanced.md) section.

Each Fount API endpoint may behave slightly differently. You can find detailed explanations in the [Endpoints](endpoints/index.md) section.

You can also find a detailed SDK reference in the [Code Reference](reference/client.md) section.

## Issues

For bug reports and feature requests, please open an issue on [GitHub](https://github.com/wppbav/bavapi-sdk-python/issues/).

## Contributing

To contribute to `bavapi`, please read the [Contributing](contributing.md) section of the documentation.
