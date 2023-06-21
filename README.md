# BAV API Python SDK

[![CI status](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/nachomaiz/32196acdc05431cd2bc7a8c73a587a8d/raw/covbadge.json)](https://github.com/wppbav/bavapi-sdk-python/actions/workflows/ci.yml)
[![docs](https://img.shields.io/badge/docs-passing-green)](https://fountapi-documentation.vercel.app/)
[![version](https://img.shields.io/badge/version-v0.4.0-blue)](https://github.com/wppbav/bavapi-sdk-python)
[![py-versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://github.com/wppbav/bavapi-sdk-python)

`bavapi` is a Python SDK for the WPP BAV API.

With `bavapi` you can access the full BAV data catalog, the largest and most comprehensive database of brand data in the world.

Queries are validated automatically thanks to `pydantic` and retrieved asynchronously via the `httpx` package.

For more information about the API, go to the [WPPBAV Developer Hub](https://developer.wppbav.com).

## Prerequisites

`bavapi` requires Python 3.9 or higher to run.

If you don't have Python installed, you can find it from the [official](https://www.python.org/downloads/) website or [Anaconda](https://www.anaconda.com/).

You will also need a BAV API token. For more information, go to the [Authentication](https://developer.wppbav.com/docs/2.x/authentication) section of the API documentation.

### Dependencies

- `httpx >= 0.20`
- `pandas >= 0.16.2`
- `pydantic >= 1.10, < 2.0`
- `tqdm >= 4.62`
- `nest-asyncio >= 1.5.6`
- `typing-extensions >= 3.10` for Python 3.9

## Installation

`bavapi` can be installed using `pip`.

```prompt
pip install wpp-bavapi
```

## Usage

Once you have acquired a token, you can start using this library directly in python or in a Jupyter Notebook. To do that, start by creating an instance of `Client`:

```py
>>> import bavapi
>>> result = bavapi.brands("TOKEN", name="Swatch") # (1)
>>> result
```

1. :lock: Replace `"TOKEN"` with your BAV API token:

|     | sector_id | sector_name           |  id | name   | ... |
| --: | --------: | --------------------- | --: | ------ | --- |
|   0 |        11 | Apparel & Accessories | 342 | Swatch | ... |
| ... |       ... | ...                   | ... | ...    | ... |

## Features

- Support for all endpoints in the Fount API. Extended support for the `audiences`, `brands`, `brandscape-data` and `studies` endpoints.
- Validates query parameters are of the correct types.
- Retrieve multiple pages of data simultaneously.

## Documentation

Read more about `bavapi` in the [documentation](https://fountapi-documentation.vercel.app/).

## Issues

Please file an issue on GitHub [here](https://github.com/wppbav/bavapi-sdk-python/issues).

## Contributing

Please see the [Contributing](https://fountapi-documentation.vercel.app/contributing/)
