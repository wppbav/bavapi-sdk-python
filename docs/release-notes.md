# Release Notes

## Version 0.9

### Version 0.9.0 (October 11th, 2023)

#### Feature

- :rocket: Official support for Python 3.12.
- :watch: Added ability to [show/hide progress](usage/basic.md#suppressing-progress-bars) bar when making requests with the `verbose` parameter. This is available for all top-level endpoint functions and when creating an instance of `bavapi.Client`. To hide the progress bar, set `verbose` to `False` (by default `True`).

#### Docs

- :recycle: Added a section to the [Usage Tips](usage/project-tips.md) page explaining how to retry failed requests when an SSL exception is raised.
- :bug: Fix absolute/relative documentation links in the GitHub `CONTRIBUTING.md` file and the synced docs version.
- :notebook: Added documentation for changing the User Agent for HTTP requests.
- :bug: Fix incorrect code example in the `brandscape-data` endpoint page.
- :notebook: Added explicit documentation about which filters are available in top-level functions and methods to all [endpoint](endpoints/index.md) pages.

#### Internal

- :warning: Fix deprecation warning due to timezone-aware `datetime` usage when generating reference classes in Python 3.12.

#### CI

- :arrow_up: Upgraded `nox` GitHub Action versions.
- :rocket: Added Python 3.12 to GitHub Actions CI/testing.

#### Typing

- :white_check_mark: Enabled support for [PEP 692](https://docs.python.org/3.12/whatsnew/3.12.html#whatsnew312-pep692) `TypedDict` kwargs via `Unpack` on all endpoint functions and methods.

#### Dependencies

- :arrow_up: Updated minimum required version of `typing-extensions` for Python versions below 3.12.

## Version 0.8

### Version 0.8.1 (September 29th, 2023)

#### Performance

- :rocket: Improved response parsing performance by ~4x (about 0.6 seconds faster per Fount query).

#### Fix

- :bug: Fix required filters in `brandscape_data` functions and methods.
- :broom: Remove buried print statement in response flattening logic.

#### Docs

- :notebook: Fixed and clarified required filters in `brandscape_data` functions and methods.

#### Internal

- :lock: Renamed `jupyter` compatibility module as private. This will remove it from the code reference docs.

### Version 0.8.0 (September 15th, 2023)

#### Feature

- :rocket: It is now possible to set a `timeout` parameter from top-level sync endpoint functions.
- :woman_detective: It is now possible to set a `user_agent` parameter when creating a `bavapi.Client` instance.

#### Fix

- :test_tube: Fixed `bavapi-gen-refs` command tests overwriting reference files.

#### Internal

- :man_detective: `'BAVAPI SDK Python'` is now the default `User-Agent` for `bavapi`.

#### Docs

- :notebook: Documentation for `timeout` usage.
- :rocket: Automatically sync top level `CONTRIBUTING.md` file with the docs version.
- :bug: Fixed instructions to generate reference classes while specifying a token in the CLI command.
- :notebook: Added missing parameter documentation for `Query` methods.

#### CI

- :gear: Removed end-to-end tests from CI pipeline due to various issues. They will have to be run manually in the near future.

## Version 0.7

### Version 0.7.0 (August 22nd, 2023)

#### Feature

- :rocket: It is now possible to specify a token with `-t`/`--token` when generating reference files via the `bavapi-gen-refs` command.

#### Fix

- :bug: `bavapi-gen-refs` would not run if `python-dotenv` was not installed. Now it will require an explicit token with `-t`/`--token` or, if `dotenv` is not installed, will prompt the user to install it and set the right environment variables.

#### Docs

- :bug: Fixed some links not pointing to the correct documentation pages.
- :bulb: Added a "Usage Tips" section describing how to save queries for later use.

#### CI

- :rocket: Set up automatic building of docs using `mike` and Github Actions.
- :bug: Fix `deploy_docs` nox session to install dependencies and actually run the deploy command.

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

- :bug: Fixed use of `type` in type hints not compatible with Python 3.8.
- :broom: Cleaned up type hints in tests.
