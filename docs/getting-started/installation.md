# Installation

## Pre-requisites

`bavapi` requires Python 3.8 or higher to run.

If you don't have Python installed, you can download it from the official Python [website](https://www.python.org/downloads/) or [Anaconda](https://www.anaconda.com/).

You will also need a Fount API bearer token to peform requests to the Fount. For instructions on how to get your own API token, see the [Authentication](authentication.md) section.

Once you have installed Python and have acquired your Fount API token, return to this page to continue.

## Dependencies

`bavapi` depends on the following excellent libraries:

- [`httpx`](https://www.python-httpx.org/) for communication with the Fount API.
- [`pandas`](https://pandas.pydata.org/docs/index.html) for processing retrieved data into tables.
- [`pydantic`](https://docs.pydantic.dev/latest/) to validate query and filter parameters.
- [`nest-asyncio`](https://github.com/erdewit/nest_asyncio) to support Jupyter notebooks.
- [`tqdm`](https://tqdm.github.io/) to show helpful progress bars.
- [`typing-extensions`](https://typing-extensions.readthedocs.io/en/latest/) for type-checking compatibility in Python < 3.12.

These libraries will be installed automatically when you install `bavapi`.

## Installing `bavapi`

Once you have your virtual (or conda) environment activated, you can install `bavapi` with the following command:

```prompt
pip install wpp-bavapi
```

!!! tip "Installing with `conda`"
    `bavapi` is not currently available from `conda` directly, though it should be possible to install and use it within a `conda` environment.

    You can use the following commands to maximize compatibility between `conda` and `pip`:

    ```prompt
    conda install httpx, pandas, pydantic, nest-asyncio, tqdm, typing_extensions

    pip install wpp-bavapi --no-deps
    ```

### Installing from source

To install from source, clone the GitHub repository into your local machine:

```prompt
git clone https://github.com/wppbav/bavapi-sdk-python.git
```

Go into the cloned directory and install `bavapi`:

```prompt
cd bavapi-sdk-python
pip install .
```
