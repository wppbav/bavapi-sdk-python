# Release Notes

## `0.11`

### `0.11.0` (October XXth, 2023)

In preparation for a stable release of `bavapi`, some aspects of the endpoint function/method interface have been normalized across the library.

This means that all endpoints now support a `query` parameter directly, to allow for better reproducibility and parametrization of queries. `raw_query` now also uses `query` instead of `params`, with `query` being required unlike with other endpoints.

Another change is that the order of parameters has been altered. The main reason for this is that parameters like `brand_id` were positional parameters before, when they are exclusive with almost all othe r parameters. This was also the case for parameters like `studies`, which are exclusive with `country_codes` and `year_numbers`. Now `{endpoint}_id` parameters and other exclusive or niche filters have been turned to keyword-only parameters. Filters like `inactive` and `not_in_most_influential` have been removed from endpoint functions. Use the `filters` parameter instead. See each [endpoint documentation](endpoints/index.md) page for more information.

#### Feature

- :tada: It is now possible to pass a [`bavapi.Query`][query.Query] object to all endpoint functions and methods with the `query` parameter. If `query` is used, all the parameters that would be used in the query (listed before `query` in each [endpoint documentation][sync]) will be ignored.
- :tada: It is now possible to specify a destination folder for the `bavapi-gen-refs` command with the `-d`/`--dest-folder` argument.
- :tada: Reference classes generated via `bavapi-gen-refs` can now be imported with `from bavapi_refs import Countries` for example.

#### Changes

- :stop_sign: (BREAKING) Changed `raw_query` `params` parameter name to `query` to match all other endpoints.
- :stop_sign: (BREAKING) Changed the order of several endpoint parameters for more effective queries. Now, each endpoint function has a set of parameters that can be set as positional arguments for exploratory filtering, while niche filters and IDs have become keyword only parameters.
    - `audiences`:
        - Positional filters: `name`, `active`, `public`
        - Keyword filters: `audience_id`, `private`, `groups`
    - `brand_metrics`:
        - Positional filters: `name`, `active`, `public`
        - Keyword filters: `metric_id`, `private`, `groups`
    - `brand_metric_groups`:
        - Positional filters: `name`, `active`
        - Keyword filters: `group_id`
    - `brands`:
        - Positional filters: `name`, `country_codes`, `year_numbers`
        - Keyword filters: `brand_id`, `studies`
    - `brandscape_data`:
        - Positional filters: `country_code`, `year_number`, `audiences`, `brand_name`
        - Keyword filters: `studies`
    - `categories`:
        - Positional filters: `name`, `sector`
        - Keyword filters: `category_id`
    - `collections`:
        - Positional filters: `name`, `public`
        - Keyword filters: `collection_id`, `shared_with_me`, `mine`
    - `sectors`:
        - Positional filters: `name`, `in_most_influential`
        - Keyword filters: `sector_id`
    - `studies`:
        - Positional filters: `country_codes`, `year_numbers`, `full_year`
        - Keyword filters: `study_id`

#### Error Messages

- :warning: Improved error message for `bavapi-gen-refs` command when neither `-a`/`--all` nor `-n`/`--name` arguments aren't used.

#### Fix

- :bug: Fixed that requests with `item_id` would ignore other query parameters.
- :bug: Addressed undefined behavior when `max_pages` is larger than the total number of pages as reported by the API. Now the max number of pages is always capped by the reported total.

#### Internal

- :bug: Fixed typing of `tuple` internal `docs_deploy` function annotations not being compatible with Python <3.9.

#### Docs

- :sparkles: Filter classes table in [Basic usage](usage/basic.md#filtering-responses) page now points to each endpoint function docs.
- :sparkles: Automatically add comment to `docs/contributing.md` to edit `./CONTRIBUTING.md` instead.
- :notebook: Updated Jupyter notebook demo with latest features and conventions.
- :notebook: Documented the [use of `bavapi.Query`](usage/basic.md#using-query-objects) object in functions and methods.
- :notebook: Improved code example for the [Using reference classes](usage/basic.md#using-reference-classes) section of the Basic usage page.
- :notebook: Clarified which endpoint filters are positional and keyword-only in respective [endpoint documentation](endpoints/index.md) pages
- :bug: Fixed incorrect rendering of tabs in the [Suppressing progess bar](usage/basic.md#suppressing-progress-bars) section of the Basic usage page.
- :x: Removed `datetime` formatting section from the [Basic usage](usage/basic.md) page.

## `0.10`

### `0.10.1` (October 17th, 2023)

#### Fix

- :stop_sign: (Breaking) Fix `metric_id` param to correct `group_id` name in [`bavapi.brand_metric_groups`][sync.brand_metric_groups] top level function.

#### Internal

- :lock: Renamed `reference` module as private. This will remove it from the code reference docs.
- :recycle: Set new dependency minimum versions for compatibility.

#### Docs

- :tada: Code reference section now directs to the [`sync`][sync] documentation by default.
- :notebook: Added all available filters to the summary table in the [Basic Usage](usage/basic.md) section.
- :notebook: More documentation for the [`sync`][sync] and [`client`][client] modules.
- :notebook: Added more clarity around expected environment variables when storing API keys. `bavapi` will always look for an API key in the `BAV_API_KEY` environment variable.
- :gear: Refactored code reference generation to support renaming of `reference` module.

### `0.10.0` (October 16th, 2023)

#### Feature

- :rocket: The following endpoints have been fully implmented with type hints and validation:
    - [`brand-metrics`](endpoints/brand-metrics.md)
    - [`brand-metric-groups`](endpoints/brand-metric-groups.md)
    - [`categories`](endpoints/categories.md)
    - [`collections`](endpoints/collections.md)
    - [`sectors`](endpoints/sectors.md)

#### Docs

- :notebook: Documentation for newly supported endpoints.
- :notebook: Documented the use of `"no_default"` as the `include` value for `brandscape_data` and `categories` functions/methods.

#### Internal

- :gear: Generalized internal `_default_includes` function to be able to reuse it with the `categories` endpoint.
- :bug: `nox` session `docs_build_and_serve` will now rebase local branch if local version data is not synced with GitHub.

## `0.9`

### `0.9.0` (October 11th, 2023)

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

## `0.8`

### `0.8.1` (September 29th, 2023)

#### Performance

- :rocket: Improved response parsing performance by ~4x (about 0.6 seconds faster per Fount query).

#### Fix

- :bug: Fix required filters in `brandscape_data` functions and methods.
- :broom: Remove buried print statement in response flattening logic.

#### Docs

- :notebook: Fixed and clarified required filters in `brandscape_data` functions and methods.

#### Internal

- :lock: Renamed `jupyter` compatibility module as private. This will remove it from the code reference docs.

### `0.8.0` (September 15th, 2023)

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

## `0.7`

### `0.7.0` (August 22nd, 2023)

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

## `0.6`

### `0.6.1` (July 19th, 2023)

#### Fix

- :bug: Fix `metric_keys` incorrectly categorized as a filter instead of a top-level parameter within the `Query` class.

#### Internal

- :wrench: Changed the custom `IntEnum` implementation to not override the standard lib's `IntEnum.__str__`.
- :hammer: Added `nox` session for deploying docs.

#### Tests

- :test_tube: Added tests for checking that filters and parameters are assigned correctly in `Client` methods.

#### Docs

- :notebook: Added warning about potential SSL errors outside of `bavapi` when using the Fount API.

### `0.6.0` (July 13th, 2023)

#### Internal

- :rocket: Upgraded [`pydantic`](https://pypi.org/project/pydantic/) to `v2`. Use `bavapi` `v0.5` for compatibility with `pydantic` `v1`.

#### Typing

- :bug: Fixed use of `type` in type hints not compatible with Python 3.8.
- :broom: Cleaned up type hints in tests.
