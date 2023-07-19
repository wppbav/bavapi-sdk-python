# Release Notes

## Version 0.6

### Version 0.6.1 (July 19th, 2023)

#### Fix

- :bug: Fix `metric_keys` incorrectly categorized as a filter instead of a top-level parameter within the `Query` class.

#### Internal

- :wrench: Changed the custom `IntEnum` implementation to not override the standard lib's `IntEnum.__str__`.
- :hammer: Added `nox` session for deploying docs.

#### Tests

- :test_tube: Added tests for checking that filters and parameters are assigned correctly in `Client` methods.

#### Docs

- :notebook: Added warning about potential SSL errors outside of `bavapi` when using the Fount API.

### Version 0.6.0 (July 13th, 2023)

#### Internal

- :rocket: Upgraded [`pydantic`](https://pypi.org/project/pydantic/) to v2. Use `bavapi` v0.5 for compatibility with `pydantic` v1.

#### Typing

- :bug: Fixed use of `type` in type hints not compatible with Python. 3.8
- :broom: Cleaned up type hints in tests.
