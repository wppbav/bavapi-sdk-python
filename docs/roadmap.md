# `bavapi` Roadmap

!!! note
    As of `v0.10.1`, `bavapi` is in **beta**. New features won't likely be developed until the full release of `bavapi`.

This is a non-exhaustive list of potential features & changes to `bavapi` before it is ready for full release:

## Core tooling

- [x] ~~`pydantic` V2 support~~ `v0.6.0`
- [x] ~~Strict `mypy` support with [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `Unpack` and `TypedDict`~~ `v0.9.0`

## Known issues

- Sporadic `SSL: CERTIFICATE_VERIFY_FAILED` errors when making requests to the Fount API. Currently, retrying the request usually fixes the issue.

## New fully-supported endpoints

Eventually, the plan is to support all endpoints. This is the current priority list:

- [x] ~~Categories~~ `v0.10.0`
- [x] ~~Collections~~ `v0.10.0`
- [x] ~~Brand Metrics~~ `v0.10.0`
- [x] ~~Sectors~~ `v0.10.0`
- [x] ~~Brand Metric Groups~~ `v0.10.0`

## Stretch goals

- [x] ~~Smarter flattening of JSON responses, possibly through `pandas.json_normalize`.~~ `v0.8.1`
- [ ] ~~Parse datetime values to `pandas` datetime.~~ `de-scoped`
