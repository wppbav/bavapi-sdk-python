"""Script to update reference classes with latest active definitions from the Fount."""

# pylint: disable=too-few-public-methods

import argparse
import asyncio
import datetime
import functools
import os
from pathlib import Path
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple

import pandas as pd

from bavapi import Client, Query
from bavapi.parsing.responses import parse_response
from bavapi.typing import JSONDict

ReferenceParser = Callable[[pd.Series], Dict[str, str]]


class Args:
    """Basic namespace for arguments with typing."""

    __slots__ = ("all", "name", "folder", "token")

    def __init__(self, namespace: argparse.Namespace) -> None:
        self.all: bool = namespace.all
        self.name: str = namespace.name
        self.folder: Path = namespace.dest_folder
        self.token: str = namespace.token


class RefConfig(NamedTuple):
    """Config information for updating Fount references

    Attributes
    ----------
    endpoint : str
        Fount API resource endpoint to use for updating references.
    filepath : str
        Path to write the updated references to.
    parser : Callable[[pd.Series], dict[str, str]]
        Function to parse the reference in pandas form to a dict of strings.
    resource_col : str, optional
        Column to get the names for each item in the reference, default "name"
    """

    endpoint: str
    filename: str
    parser: ReferenceParser
    resource_col: str = "name"


async def get_references(
    fount: Client, configs: Iterable[RefConfig]
) -> List[List[JSONDict]]:
    """Download items for the reference from the Fount.

    Parameters
    ----------
    fount : Client
        Client instance to perform requests with.
    configs : Iterable[RefConfig]
        Reference config objects, with information about the filepath, endpoint
        resource parser function and the resource column.

    Returns
    -------
    dict[str, str]
        Dictionary of reference information for generating reference files.
    """
    async with fount:
        tasks = [
            asyncio.create_task(fount.raw_query(config.endpoint, Query()))
            for config in configs
        ]
        return await asyncio.gather(*tasks)


def parse_reference(
    fetched: pd.Series, symbols: Dict[str, str], norm: Dict[str, str]
) -> Dict[str, str]:
    """Parse reference information from the Fount.

    Parameters
    ----------
    fetched : pd.Series
        Pandas Series with reference information
    symbols : dict[str, str]
        Symbols to replace
    norm : dict[str, str]
        Elements in reference to normalize

    Returns
    -------
    dict[str, str]
        Dictionary of reference information for generating reference files.
    """
    fetched = fetched.str.upper().replace(symbols, regex=True).replace(norm, regex=True)

    return {str(v): str(k) for k, v in fetched.to_dict().items()}


parse_audiences = functools.partial(
    parse_reference,
    symbols={r"\+": "_PLUS", r"\W+": "_"},
    norm={
        "MIDDLE_INCOME": "MEDIUM_INCOME",
        "29_AND_UNDER": "UNDER_30",
    },
)

parse_countries = functools.partial(
    parse_reference,
    symbols={r"\W+": "_"},
    norm={"TÜRKIYE": "TURKIYE"},
)


def process_items(data: Iterable[JSONDict], config: RefConfig) -> Dict[str, str]:
    """Process raw Fount response into a dictionary of name to filter code pairs.

    Parameters
    ----------
    data : Iterable[JSONDict]
        Iterable of JSON dictionaries representing each of the Fount reference items.
    config : RefConfig
        Reference configuration to use for processing items.

    Returns
    -------
    dict[str, str]
        Pairs of reference item names and their corresponding code.
    """
    res_df = parse_response(data, index="id")

    if "is_active" in res_df.columns:
        res_df = res_df[res_df["is_active"].astype(bool)]

    items = res_df[config.resource_col].drop_duplicates().pipe(config.parser).items()
    return dict(sorted(items))


def generate_source(
    ref_name: str,
    ref_items: Dict[str, str],
    updated: datetime.datetime,
    import_items: Tuple[str, str] = ("bavapi._reference.int_enum", "IntEnum"),
) -> str:
    """Generate updated module source from reference items.

    Parameters
    ----------
    ref_name : str
        Name of the reference to generate. This name will also be the name of the
        reference class ("countries" -> "Countries").
    ref_items : dict[str, str]
        Dictionary of reference information to generate from.
    updated : datetime.datetime
        Reference update timestamp.
    import_items : tuple[str, str], optional
        Elements for import statement, default ("bavapi.reference.base", "IntEnum")

    Returns
    -------
    str
        Updated source as a string.
    """
    updated_comment = (
        f"# This file was generated from active {ref_name.lower()} in the Fount.\n"
        f"# {ref_name.capitalize()} retrieved on {updated.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    class_docstring = f'"""{ref_name.capitalize()} IDs for Fount API queries."""'

    source_items = [
        f'"""{ref_name.capitalize()} class for holding {ref_name} IDs."""',
        updated_comment,
        f"from {import_items[0]} import {import_items[1]}\n",
        f"class {ref_name.capitalize()}({import_items[1]}):\n" f"    {class_docstring}",
        "\n".join(f"    {k} = {v}" for k, v in ref_items.items()),
    ]

    return "\n\n".join(source_items) + "\n"


def generate_init_source(dest_folder: Path) -> str:
    """Generate updated init module source from existing reference modules.

    Scans destination folder for reference modules.

    Parameters
    ----------
    dest_folder : Path
        Path to reference modules.

    Returns
    -------
    str
        Updated init source as a string.
    """
    ref_names = [
        file.stem for file in dest_folder.glob("*.py") if file.stem != "__init__"
    ]
    exports = ", ".join(f'"{name.capitalize()}"' for name in ref_names)
    if len(ref_names) == 1:
        exports += ","

    return "\n".join(
        [
            '"""`bavapi` Reference classes for holding Fount IDs.\n\n'
            'Use them in place of integers when filtering requests.\n"""\n',
        ]
        + [
            f"from {dest_folder.name}.{name} import {name.capitalize()}"
            for name in ref_names
        ]
        + ["\n" f"__all__ = ({exports})" "\n"]
    )


def write_to_file(source: str, filepath: Path) -> None:
    """Write updated module source to file.

    Parameters
    ----------
    source : str
        Updated module source as a string.
    filepath : pathlib.Path
        Path to write the source to.
    """
    if not filepath.parent.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(source)


def parse_args(argv: Optional[Sequence[str]] = None) -> Args:
    """Parse arguments given to the script.

    Parameters
    ----------
    argv : Sequence[str], optional
        Arguments from CLI command, default None

    Returns
    -------
    argparse.Namespace
        Object containing arguments and values for the script
    """
    parser = argparse.ArgumentParser(
        description="Generate reference files for commonly used BAV filters.\n\n"
        "The script will generate a set of reference files that contain "
        "helpful classes for filtering BAV data in readable form.\n\n"
        "The currently available reference classes are Audiences and Countries.\n"
        "These classess will be stored in a `bavapi_refs` folder in your "
        "current working directory. "
        "You can import them using `from bavapi_refs import Audiences`.\n"
        "Existing reference files will be overwritten.",
        epilog="DON'T PUSH REFERENCES TO GIT! Add `bavapi_refs/` to `.gitignore`.",
    )
    parser.add_argument("-t", "--token", default="", help="WPPBAV Fount API token")
    parser.add_argument(
        "-a", "--all", action="store_true", help="Generate all reference files"
    )
    parser.add_argument(
        "-n",
        "--name",
        default="",
        choices={"audiences", "countries"},
        help="Name of reference to generate",
    )
    parser.add_argument(
        "-d",
        "--dest-folder",
        default="./bavapi_refs/",
        type=Path,
        help="Path to destination folder, default './bavapi_refs/'",
    )
    return Args(parser.parse_args(argv))


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main function to generate reference classes.

    Parameters
    ----------
    argv : Sequence[str], optional
        Arguments from CLI command, default None

    Returns
    -------
    int
        CLI exit code

    Raises
    ______
    ValueError
        If Fount API token is not set or `python-dotenv` is not installed
    """
    args = parse_args(argv)
    if not args.token:
        try:
            from dotenv import load_dotenv  # pylint: disable=import-outside-toplevel

            load_dotenv()
        except ImportError as exc:
            raise ValueError(
                "You must specify a Fount API token with the `-t`/`--token` argument, "
                "or install `python-dotenv` and set `BAV_API_KEY` in a `.env` file."
            ) from exc

    fount = Client(os.getenv("BAV_API_KEY", args.token))

    ref_configs: Dict[str, RefConfig] = {
        "audiences": RefConfig("audiences", "audiences", parse_audiences),
        "countries": RefConfig(
            "studies",
            "countries",
            parse_countries,
            "country_name",
        ),
    }

    if args.all:
        names: Iterable[str] = ref_configs.keys()
        configs: Iterable[RefConfig] = ref_configs.values()
    elif not args.name:
        raise ValueError(
            "You must use either the `-a`/`--all` or the `-n`/`--name` arguments. "
            "Run `bavapi-gen-refs -h for more details and instructions."
        )
    else:
        names, configs = (args.name,), (ref_configs[args.name],)

    results = asyncio.run(get_references(fount, configs))

    for name, data, config in zip(names, results, configs):
        items = process_items(data, config)
        source = generate_source(
            name, items, datetime.datetime.now(datetime.timezone.utc)
        )
        path = args.folder / f"{name}.py"

        print(f"Writing {name} file with {len(items)} items to {path}")
        write_to_file(source, path)

    write_to_file(generate_init_source(args.folder), args.folder / "__init__.py")

    print("Success!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
