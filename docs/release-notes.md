# Release Notes

## `1.1`

### `1.1.0` (2024-??-??)

#### Feature

- :sparkles: Added new `bavapi.tools` module to support the [Tools/TurboPitch](usage/tools.md) endpoints in the BAV API.

#### Docs

- :broom: Fixed minor typos in docstrings for `bavapi.Client` and `sync` methods.
- :notebook: Blocked `config` module from appearing in API reference docs.
- :sparkles: Added documentation cross-linkage support for `pydantic` and `pandas`. References to `pydantic` and `pandas` functions or classes now link to their documentation page.

#### Internal

- :warning: Started setting up deprecation functionality for `v2`.
- :broom: New `config` module to hold the user agent and URL to use with the package.

#### Typing

- :bug: Fixed too-strict type definitions for `parsing.params.list_to_str`.

## `1.0`

### `1.0.4` (2024-04-09)

#### Feature

- :sparkles: Added new [Audience Groups](endpoints/audience-groups.md) endpoint to `bavapi`.

#### Docs

- :rocket: Added `v2` roadmap to the documentation.
- :notebook: Added documentation for Audience Groups.
- :broom: Fixed various typos.

#### Test

- :test_tube: Clean up testing of `http` and `client` modules through dependency injection.

#### Typing

- :duck: Moved commonly used protocols to `typing` module.
- :bug: Changed type of `exc_type` argument in the `aretry` function to correct `Tuple` instead of `Iterable`.

#### Internal

- :broom: Removed old `testing` code for reproducing SSL issues in earlier versions of `bavapi`.

### `1.0.3` (2024-02-09)

#### Fix

- :bug: Fix bug in custom dtype conversion within the response parsing logic.

### `1.0.2` (2024-02-08)

#### Fix

- :warning: Fix deprecation warning when parsing responses into dataframes with `pandas>=2.2`.

#### Docs

- :sparkles: Add ability to copy code blocks from the documentation.

#### Test

- :test_tube: Added tests for correct dtype conversions.

#### Internal

- :broom: Cleaned up unused and ignored logging for development scripts.

### `1.0.1` (2024-01-19)

#### Fix

- :bug: Fixed typo in `sectors` (previously spelled `sector`) parameter for `categories` endpoint queries.

#### Docs

- :sparkles: Fixed docs update script to execute only when the `CONTRIBUTING.md` file changes.
- :sparkles: Fixed version numbers to only have `major.minor` format in docs.
- :bug: Fix external library/package links.
- :notebook: Fix missing `name` parameter from various endpoint documentation pages.

#### Internal

- :sparkles: Cleaned up docs sessions in `nox` file, now will only use `mkdocs serve` for local development.

### `1.0.0` (2024-01-04)

#### Feature

- :tada: Added five new endpoints to `bavapi` with accompanying `FountFilters` classes:
    - [`cities`](endpoints/cities.md)
    - [`companies`](endpoints/companies.md)
    - [`countries`](endpoints/countries.md)
    - [`regions`](endpoints/regions.md)
    - [`years`](endpoints/years.md)

#### Changes

- :recycle: Initial handshake API request will now be retried on SSL errors.

#### Docs

- :broom: Reordered some sections in the [Basic usage](usage/basic.md) and [Advanced usage](usage/advanced.md) sections of the documentation.
- :broom: Updated and standardized Jupyter notebook demo.
- :broom: Clarified when a query is considered to be a single-page query in the [`bavapi.Query.is_single_page`][query.Query.is_single_page] docstring.
- :broom: Fixed some minor errors in `bavapi.Client` method docstrings.
- :tada: Added examples of the batch logic in the Jupyter demo notebook.
- :broom: Repurposed the getting started section on reference classes as the primary documentation page for the references functionality, rather than keeping a section in Basic usage.
- :sparkles: Changed Release notes dates to ISO-8601 format.

#### Internal

- :information_source: Cleaned up and added comments to documentation scripts.
- :sparkles: Removed `tqdm` as a dependency from the batching logic.
- :information_source: Added comments to `nox` session for deploying the docs.
- :broom: Simplified some logic in `Query.ensure`.
- :tada: Added support for specifying exceptions to retry on for `aretry` internal function.

#### CI

- :recycle: CI won't run unless a package or test file is changed, or the CI action file is changed.
- :sparkles: Added manual trigger to documentation so deploying fixes to the docs doesn't require a version change.

## `0.13`

### `0.13.0` (2023-12-11)

This version of `bavapi` is expected to be the last **beta** version before a release candidate.

#### Feature

- :tada: `bavapi` will now **retry** page requests upon failure. You can control the number of retry attempts with the `retries` parameter in top-level functions and the `Client` interface.
- :tada: It is now possible to control the behavior of errors in the request process. If `on_errors` is set to `"warn"` (default), successful requests will be returned and a warning will be issued detailing which pages resulted in errors and each exception associated with it. If `on_errors` is set to `"raise"` (old behavior) instead, an exception will be raised as soon as any request fails.
- :tada: Added `bav_study` and `released` filters to `studies` endpoint function and method.

#### Changes

- :rocket: Reduced the size of the initial request to 1 item if a paginated request is detected for improved performance.
- :rocket: Paginated requests are now performed in batches instead of starting every request from the start. This should mitigate several issues (like SSL errors) with large queries and improve overall run times. You can control this behavior through the `batch_size` and `n_workers` parameters in top-level functions and the `Client` interface.
- :hammer: Instead of having failed requests immediately raise exceptions, `bavapi` will continue downloading pages, collect successful responses, and warn the user about the pages that failed to be collected. This can be controlled by the `on_errors` parameter in top-level functions and the `Client` interface.
- :sparkles: Using `bavapi.Query` instances in request functions and methods will now combine method parameters with parameters in the query object. Parameters specified in the query object will take precedence over parameters specified in the function or method. Filter values in the method parameters will be ignored if the query object contains filters.

#### Fix

- :bug: Refactored the expanding step of the result parsing pipeline to fix undefined behavior when multiple expandable columns are found in the result.

#### Internal

- :broom: Removed trailing whitespaces
- :hammer: New data fetching algorithm based on asynchronous workers.
- :bug: Fixed unmatched checkout action versions in `ci`.
- :hammer: Refactored filter consolidation logic to avoid unnecessary copies of parameters.

#### Docs

- :notebook: Added clarification about prefixed column names in `brandscape-data` endpoint results.
- :sparkles: Various improvements to documentation, focused on warnings/tips and code snippets.

#### Test

- :test_tube: Added tests for new `_batched` and `_fetcher` modules.
- :test_tube: Added new test case for `parsing.responses` to test correct behavior with multiple expandable columns in the response.
- :test_tube: Added new tests for query consolidation logic.
- :wrench: Fixed `HTTPClient` tests to work with new architecture.
- :sparkles: Simplified integration tests thanks to the new retry functionality

## `0.12`

### `0.12.1` (2023-11-21)

#### Fix

- :bug: Incorrect `datetime` format used when formatting string values.
- :bug: Removed unused testing helper code that could lead to recursion errors.

#### Internal

- :broom: Removed unnecessary development flags for coverage and typing.

#### Tests

- :test_tube: Add tests for all arguments in `bavapi-gen-refs` argument parser.

#### Typing

- :sparkles: Improved typing of `generate_references` and `sync` modules.

#### Docs

- :broom: Fixed incorrect warning about mixing filters and endpoints.
- :white_check_mark: Normalized docstring default definitions to follow `numpydoc` spec.

### `0.12.0` (2023-11-15)

#### Feature

- :tada: Added support for `metric_group_keys`, for use with the `brandscape-data` endpoint.
- :tada: It is now possible to use `page` as the start page of a paginated request. Use `per_page` and/or `max_pages` to change the behavior of the pagination. More info in the [Basic Usage](usage/basic.md#pagination) section.
- :sparkles: As a result of the new paginated behavior, it is now possible to chunk requests by setting the start and end of the request with `page` and `per_page`, respectively. See more info in the [Project tips](usage/project-tips.md) section of the documentation.

#### Changes

- :warning: Exceptions `DataNotFoundError` and `RateLimitExceededError` are now subclasses of `APIError`.
- :hammer: Refactored pagination logic to allow for control over the start and end of the paginated request to the Fount. Shouldn't break existing uses of `page` unless `per_page` and/or `max_pages` were also in use. More info in the [Basic Usage](usage/basic.md#pagination) section.
- :gear: `Query.with_page` parameters are now optional and default to `None`.
- :wrench: `Query` attributes `page`, `per_page`, and `max_pages` must be greater than `0`.
- :stop_sign: (BREAKING) `Query.paginated` parameter order has changed to make `per_page` optional.

#### Fix

- :gear: Various issues and inconsistencies with pagination logic.
- :bug: Fixed `per_page` not applying to single page results.

#### Docs

- :sparkles: Added instructions for performing batched requests in the [Project Tips](usage/project-tips.md#batch-requests) section.

## `0.11`

### `0.11.0` (2023-09-27)

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

- :bug: Fixed typing of `tuple` internal `docs_deploy` function annotations not being compatible with Python `<3.9`.
- :rocket: Removed slow and unnecessary test for the `verbose` parameter in `HTTPClient`.
- :rocket: Refactored tests that instantiate `httpx.AsyncClient` instances for a 20x reduction in test run time.

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

### `0.10.1` (2023-10-17)

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

### `0.10.0` (2023-10-16)

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

### `0.9.0` (2023-10-11)

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

### `0.8.1` (2023-09-29)

#### Performance

- :rocket: Improved response parsing performance by ~4x (about 0.6 seconds faster per Fount query).

#### Fix

- :bug: Fix required filters in `brandscape_data` functions and methods.
- :broom: Remove buried print statement in response flattening logic.

#### Docs

- :notebook: Fixed and clarified required filters in `brandscape_data` functions and methods.

#### Internal

- :lock: Renamed `jupyter` compatibility module as private. This will remove it from the code reference docs.

### `0.8.0` (2023-09-15)

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

### `0.7.0` (2023-08-22)

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

### `0.6.1` (2023-07-19)

#### Fix

- :bug: Fix `metric_keys` incorrectly categorized as a filter instead of a top-level parameter within the `Query` class.

#### Internal

- :wrench: Changed the custom `IntEnum` implementation to not override the standard lib's `IntEnum.__str__`.
- :hammer: Added `nox` session for deploying docs.

#### Tests

- :test_tube: Added tests for checking that filters and parameters are assigned correctly in `Client` methods.

#### Docs

- :notebook: Added warning about potential SSL errors outside of `bavapi` when using the Fount API.

### `0.6.0` (2023-07-13)

#### Internal

- :rocket: Upgraded [`pydantic`](https://pypi.org/project/pydantic/) to `v2`. Use `bavapi` `v0.5` for compatibility with `pydantic` `v1`.

#### Typing

- :bug: Fixed use of `type` in type hints not compatible with Python 3.8.
- :broom: Cleaned up type hints in tests.
