---
hide:
    - navigation
---

<!--If linking to a docs page, must be linked to /latest/ version-->
<!--If linking to a section with an index page, must add "/index" to URL-->

# Contributing to `bavapi`

`bavapi` is an open source library provided by WPPBAV, and we're happy to accept contributions from the community.

In order to keep a high level of quality and accessibility for our users, there are certain code style and testing requirements that we ask to accept your contributions.

`bavapi` uses `nox` to run development scripts.

## Issues

The easiest way to contribute when you see something wrong is to open an issue on GitHub. You can do so [here](https://github.com/wppbav/bavapi-sdk-python/issues).

Please read the instructions in the issue template and fill out as much information as possible.

This should be your first stop to start contributing to `bavapi`. We kindly ask that you let us know if you would like to contribute any changes to the code base by opening an issue on GitHub.

Please return to this page once you have opened an issue on GitHub and are ready to start contributing.

## Cloning `bavapi` repository

In order to make sure you work on the latest version of `bavapi`, please *fork* the GitHub repository into your account and clone your fork of `bavapi` into your machine:

```prompt
git clone https://github.com/{your-username}/bavapi-sdk-python
```

Once cloned, enter the newly created directory, create a virtual environment and install all optional dependencies in *edit* mode:

```prompt
pip install -e .[dev, doc, test, lint]
```

This will install all optional dependencies which are necessary for contributing to the code base.

## Fount API Key

You will need a Fount API key to perform requests to the API through `bavapi`.

To get and use an API key, see the [Authentication](getting-started/authentication.md) section of the Getting Started guide.

In order to run integration tests, you will need to use an `.env` file to store your Fount API key as `FOUNT_API_KEY` (you can also set the environment variable directly). See the [instructions](getting-started/authentication.md#recommended-way-to-manage-api-keys) for more details.

## Tools and frameworks

`bavapi` uses the following frameworks for development:

- Fully type-hinted and tested with [`mypy`](https://www.mypy-lang.org/).
- Unit and integration tests using [`pytest`](https://docs.pytest.org/en/stable/contents.html).
- Full test coverage using [`coverage`](https://coverage.readthedocs.io/en/).
- Run development scripts in multiple Python versions with [`nox`](https://nox.thea.codes/en/stable/).
- Documentation using [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/).
- Code auto-formatting with [`black`](https://black.readthedocs.io/en/stable/).
- Linting with [`pylint`](https://docs.pylint.org/).

Please familiarize yourself with using these libraries in order to get started with contributing to `bavapi`.

## Developing in Windows

It is highly recommended that you use [`mamba`](https://mamba.readthedocs.io/en/latest/) to manage Python environments in Windows. It is a faster implementation of `conda` and testing of `bavapi` on multiple versions of Python is set up to use `mamba` on Windows.

Once you have `mamba` installed in your system, and you have set up an environment with `nox`, you should be able to run the `nox` commands for `bavapi`.

## Nox commands

To run `nox` commands, run the following command in your terminal:

```prompt
nox -s {command_name}
```

### Available `nox` commands

To see a list of all available `nox` commands, run `nox -l` in your terminal. Here is a quick summary:

- `tests` and `tests_e2e`: run `pytest` unit (or end-to-end) tests and collect `coverage` information. Suitable for CI/CD pipeline and for Linux (would require `pyenv` to manage Python versions).
- `tests_mamba` and `tests_mamba_e2e`: run `pytest` unit (or end-to-end) tests and collect `coverage` information, using `mamba` to run multiple versions of Python. Suitable for local testing on Windows.
- The commands above, ending with `_nocov`: run `pytest` unit (or end-to-end) tests without collecting `coverage` information.
- `coverage`: combine and report coverage results.
- `build`: build distributable files for `bavapi`. Suitable for CI/CD pipeline.
- `docs_deploy`: publish `bavapi` documentation to GitHub Pages. Suitable for local development and CI/CD pipelines.
- `docs_serve`: serve `bavapi` documentation with `mike`. Suitable for local development.
- `docs_build_and_serve`: run both `docs_deploy` and `docs_serve`. Suitable for local development.

## Code Style Guidelines

`bavapi` supports Python 3.8 and above, so your code should be able to run in all the latest versions of python.

1. Run `black bavapi` after writing or modifying code. This way the code style of the whole project will remain consistent.
2. Run `mypy bavapi` after writing or modifying code to make sure type hints are correctly defined.
3. Fully test your code using `pytest` and make sure you covered all your changes in the repository by running all `tests_mamba`, `tests_mamba_e2e` and `coverage` sessions from `nox`.

## Documentation

If your contribution changes the functionality of the library, you will need to update the documentation.

`mkdocs-material` will automatically generate documentation for your code by parsing docstrings with `mkdocstrings`. Please make sure that the docstrings in your code follow the [`numpydoc`](https://numpydoc.readthedocs.io/en/latest/index.html) standard.

If your contribution changes the basic or advanced functionality of the library, or changes how the library is installed, please update those sections of the documentation.

Each fully implemented endpoint should have a corresponding documentation page in the `endpoints` folder. Please follow the same structure as other endpoint pages for consistency.

## CI/CD

`bavapi` has a CI/CD pipeline set up that checks for testing and coverage. All code must be tested and will fail integration if test coverage is not 100%.

One way to ensure success is to run the three testing commands mentioned above. You can copy/paste the following command for convenience:

```prompt
nox -s tests_mamba && nox -s tests_mamba_e2e && nox -s coverage
```

## Pull Requests

In order to integrate changes into `bavapi`, you must create a pull request on GitHub.

Please follow the instructions in the pull request template and fill out as much information as possible.

GitHub actions will automatically run tests on the pull request content.
