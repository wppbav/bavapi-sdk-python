"""Package tooling session definitions for `nox`"""

import json
import os
import pathlib
from typing import Dict, List, cast

import nox

python_versions = ("3.8", "3.9", "3.10", "3.11")


@nox.session(python=python_versions)
def tests(session: nox.Session) -> None:
    """Run tests on CI/CD pipeline."""
    session.install("-e", ".[test]")

    session.run(
        "coverage",
        "run",
        "-m",
        "--parallel",
        "pytest",
        "-m",
        "not e2e",
        *session.posargs,
    )


@nox.session(python=python_versions)
def tests_nocov(session: nox.Session) -> None:
    """Run tests on CI/CD pipeline with no coverage."""
    session.install("-e", ".[test]")

    session.run("pytest", "-m", "not e2e", *session.posargs)


@nox.session(python="3.11")
def tests_e2e(session: nox.Session) -> None:
    """Run end to end tests on CI/CD pipeline."""
    session.install("-e", ".[test]")

    session.run(
        "coverage",
        "run",
        "-m",
        "--parallel",
        "pytest",
        "-m",
        "e2e",
        *session.posargs,
    )


@nox.session(python="3.11")
def tests_e2e_nocov(session: nox.Session) -> None:
    """Run end to end tests on CI/CD pipeline with no coverage."""
    session.install("-e", ".[test]")

    session.run("pytest", "-m", "e2e", *session.posargs)


@nox.session(python=python_versions, venv_backend="mamba", reuse_venv=True)
def tests_mamba(session: nox.Session) -> None:
    """Run tests locally with `mamba` as the backend."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(
        "coverage",
        "run",
        "-m",
        "--parallel",
        "pytest",
        "-m",
        "not e2e",
        *session.posargs,
        external=True,
    )


@nox.session(python=python_versions, venv_backend="mamba", reuse_venv=True)
def tests_mamba_nocov(session: nox.Session) -> None:
    """Run tests locally with `mamba` as the backend with no coverage."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run("pytest", "-m", "not e2e", *session.posargs, external=True)


@nox.session(python="3.11", venv_backend="mamba", reuse_venv=True)
def tests_mamba_e2e(session: nox.Session) -> None:
    """Run end to end tests locally with `mamba` as the backend."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(
        "coverage",
        "run",
        "-m",
        "--parallel",
        "pytest",
        "-m",
        "e2e",
        *session.posargs,
        external=True,
    )


@nox.session(python="3.11", venv_backend="mamba", reuse_venv=True)
def tests_mamba_e2e_nocov(session: nox.Session) -> None:
    """Run end to end tests locally with `mamba` as the backend with no coverage."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run("pytest", "-m", "e2e", *session.posargs, external=True)


@nox.session(python="3.11")
def coverage(session: nox.Session) -> None:
    """Compile and process coverage reports."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(pathlib.Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)

    if os.getenv("CI"):
        session.run("coverage", "json")

        with open("coverage.json", encoding="utf-8") as file:
            total: str = json.load(file)["totals"]["percent_covered_display"]

        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as file:
            file.write(f"total={total}")

        print(f"{total=} added to GITHUB_ENV.")

        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
            file.write(f"### Total coverage: {total}%")


@nox.session(python="3.11")
def lint(session: nox.Session) -> None:
    """Lint package."""
    session.install("-e", ".[lint]")

    session.run("mypy", "bavapi")
    session.run("pylint", "bavapi")
    session.run("pylint", "tests")
    session.run("isort", "-l", "100", ".")
    session.run("black", ".")


@nox.session(python=None)
def requirements(session: nox.Session) -> None:
    """Run pip-tools to prepare `requirements.txt` files."""

    # nox should only run this function in python 3.11 so this should be safe
    import tomllib  # pylint: disable=import-outside-toplevel

    session.install("pip-tools")

    if "all-extras" not in session.posargs:
        session.run(
            "pip-compile", "--resolver=backtracking", "pyproject.toml", *session.posargs
        )
    else:
        session.posargs.remove("all-extras")
        with open("pyproject.toml", "rb") as file:
            deps: Dict[str, List[str]] = tomllib.load(file)["project"].get(
                "optional-dependencies", {}
            )

        for dep in deps:
            session.run(
                "pip-compile",
                f"--extra={dep}",
                f"--output-file={dep}-requirements.txt",
                "--resolver=backtracking",
                "pyproject.toml",
                *session.posargs,
            )


@nox.session(python=None)
def build(session: nox.Session) -> None:
    """Build package wheel and source distribution into dist folder."""
    session.install("build")

    session.run("python", "-m", "build")


@nox.session(python=False)
def docs_deploy(session: nox.Session) -> None:
    """Build and deploy documentation with version handling.

    If package minor version is latest, deploy docs version and assign to `latest`.
    If package minor version is not latest, deploy docs version.
    If package minor version exists, update docs version.

    Arguments
    ---------
    --push: flag
        Check versions from GitHub branch and deploy to branch.
    --version: str
        Override version from package

    Examples
    --------
    Run docs_deploy locally

    `nox -s docs_deploy`

    Run docs_deploy for remote branch

    `nox -s docs_deploy -- --push`

    Override package version

    `nox -s docs_deploy -- --version=2.0.0`
    """

    # Get current package version

    try:
        import tomllib
    except ImportError:
        session.install("tomli")
        import tomli as tomllib

    def version_tuple(string: str) -> tuple[int, ...]:
        return tuple(int(i) for i in string.split("."))

    if not any(
        version_args := [i for i in session.posargs if i.startswith("--version=")]
    ):
        with open("pyproject.toml", "rb") as file:
            version = version_tuple(tomllib.load(file)["project"]["version"])
    else:
        version = version_tuple(version_args[0].rpartition("=")[-1])

    minor_str = ".".join(str(i) for i in version[:2])

    remote = "--push" in session.posargs
    remote_str = "remotely " if remote else ""
    list_args = ("-b", "gh-pages") if remote else ()
    deploy_args = ["--push", minor_str] if remote else [minor_str]

    # Get deployed versions from branch
    out = cast(str, session.run("mike", "list", *list_args, silent=True))
    versions = [
        tuple(int(i) for i in v.partition(" ")[0].split(".")) for v in out.splitlines()
    ]

    if version[:2] in versions:
        print(f"Updating docs {remote_str}for version {minor_str}...")

    elif all(version[:2] > v for v in versions):
        print(f"Deploying docs {remote_str}for version {minor_str} as latest...")
        deploy_args.extend(("--update-aliases", "latest"))
    else:
        print(f"Deploying docs {remote_str}for version {minor_str} as latest...")
        deploy_args.append("latest")

    print(f"Calling deploy with args: {deploy_args}")
    # session.run("mike", "deploy", *deploy_args)
