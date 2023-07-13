# `bavapi` Roadmap

This is a non-exhaustive list of potential features & changes to `bavapi` before it is ready for full release:

## Core tooling

- ~~`pydantic` V2 support~~ :white_check_mark:
- Strict `mypy` support with [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `Unpack` and `TypedDict`

## New fully-supported endpoints

Eventually, the plan is to support all endpoints. This is the current priority list:

1. Categories
2. Collections
3. Brand Metrics
4. Sectors
5. Brand Metric Groups

## Stretch goals

- Smarter flattening of JSON responses, possibly through `pandas.json_normalize`.
