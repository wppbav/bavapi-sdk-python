# `bavapi` Roadmap

!!! warning
    `bavapi` is currently in alpha stage of development.

This is a non-exhaustive list of potential features & changes to `bavapi` before it is ready for full release:

## Core tooling

- ~~`pydantic` V2 support~~ :white_check_mark: `v0.6.0`
- ~~Strict `mypy` support with [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `Unpack` and `TypedDict`~~ :white_check_mark: `v0.9.0`

## Known issues

- Sporadic `SSL: CERTIFICATE_VERIFY_FAILED` errors when making requests to the Fount API. Currently, retrying the request usually fixes the issue.

## New fully-supported endpoints

Eventually, the plan is to support all endpoints. This is the current priority list:

1. ~~Categories~~ :white_check_mark: `v0.10.0`
2. ~~Collections~~ :white_check_mark: `v0.10.0`
3. ~~Brand Metrics~~ :white_check_mark: `v0.10.0`
4. ~~Sectors~~ :white_check_mark: `v0.10.0`
5. ~~Brand Metric Groups~~ :white_check_mark: `v0.10.0`

## Stretch goals

- ~~Smarter flattening of JSON responses, possibly through `pandas.json_normalize`.~~ :white_check_mark: `v0.8.1`
- Parse datetime values to `pandas` datetime.
