# Authentication

The first thing you will need to use `bavapi` is a Fount API authentication token (a.k.a. key).

This token is a specific code that is assigned to you and is needed to confirm that you have access to the Fount data.

## Getting a Fount API token

Please follow the instructions in the [Authentication](https://developer.wppbav.com/docs/2.x/authentication) section of the Fount API documentation.

!!! warning
    Do NOT share your API token publicly or with anyone else. That token is tied to your account exclusively. If somebody else needs a token, they should create their own from their account settings.

## Recommended way to manage API keys

In order to keep your API token secure, you should avoid using your token directly in your code and applications. Instead, place the code in a `.env` file at the top of your project directory, and use `python-dotenv` to load the token into your environment:

```prompt
my-project-folder
├─── .env
└─── ... (other stuff)
```

Create this `.env` file (note the leading dot) in the top level of your working directory, and write down your token like so:

```env
FOUNT_API_TOKEN = "your_token_here"
```

To now use this file, you will need to install the [`python-dotenv`](https://github.com/theskumar/python-dotenv) package:

```prompt
pip install python-dotenv
```

Now, paste this code at the top of your Python files or Jupyter Notebooks:

```py
import os
from dotenv import load_dotenv

load_dotenv()  # (1)
TOKEN = os.environ["FOUNT_API_TOKEN"]  # (2)
```

1. Load variables from `.env` into the system's environment
2. Assign "FOUNT_API_TOKEN" environment variable to `TOKEN`

Now you can use `TOKEN` in your API requests:

```py
bavapi.brands(TOKEN, name="Swatch")
```
