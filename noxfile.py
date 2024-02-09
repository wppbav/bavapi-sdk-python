# pylint: disable=import-outside-toplevel

"""Package tooling session definitions for `nox`"""

import json
import os
import pathlib
from typing import Iterable, Tuple, cast

import nox

PY_VERSIONS = ("3.8", "3.9", "3.10", "3.11", "3.12")
PY_LATEST = PY_VERSIONS[-1]

COV_ARGS = ("coverage", "run", "-m", "--parallel")
PYTEST_ARGS = ("pytest", "-k")


@nox.session(python=PY_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run tests on CI/CD pipeline."""
    session.install("-e", ".[test]")

    session.run(*COV_ARGS, *PYTEST_ARGS, "not e2e", *session.posargs)


@nox.session(python=PY_VERSIONS)
def tests_nocov(session: nox.Session) -> None:
    """Run tests on CI/CD pipeline with no coverage."""
    session.install("-e", ".[test]")

    session.run(*PYTEST_ARGS, "not e2e", *session.posargs)


@nox.session(python=PY_LATEST)
def tests_e2e(session: nox.Session) -> None:
    """Run end to end tests on CI/CD pipeline."""
    session.install("-e", ".[test]")

    session.run(*COV_ARGS, *PYTEST_ARGS, "e2e", *session.posargs)


@nox.session(python=PY_LATEST)
def tests_e2e_nocov(session: nox.Session) -> None:
    """Run end to end tests on CI/CD pipeline with no coverage."""
    session.install("-e", ".[test]")

    session.run(*PYTEST_ARGS, "e2e", *session.posargs)


@nox.session(python=PY_VERSIONS, venv_backend="mamba", reuse_venv=True)
def tests_mamba(session: nox.Session) -> None:
    """Run tests locally with `mamba` as the backend."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(*COV_ARGS, *PYTEST_ARGS, "not e2e", *session.posargs)


@nox.session(python=PY_VERSIONS, venv_backend="mamba", reuse_venv=True)
def tests_mamba_nocov(session: nox.Session) -> None:
    """Run tests locally with `mamba` as the backend with no coverage."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(*PYTEST_ARGS, "not e2e", *session.posargs, external=True)


@nox.session(python=PY_LATEST, venv_backend="mamba", reuse_venv=True)
def tests_mamba_e2e(session: nox.Session) -> None:
    """Run end to end tests locally with `mamba` as the backend."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(*COV_ARGS, *PYTEST_ARGS, "e2e", *session.posargs)


@nox.session(python=PY_LATEST, venv_backend="mamba", reuse_venv=True)
def tests_mamba_e2e_nocov(session: nox.Session) -> None:
    """Run end to end tests locally with `mamba` as the backend with no coverage."""
    session.conda_install("--file", "requirements.txt", channel="conda-forge")
    session.install("-e", ".[test]")

    session.run(*PYTEST_ARGS, "e2e", *session.posargs, external=True)


@nox.session(python=PY_LATEST)
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


@nox.session(python=PY_LATEST)
def lint(session: nox.Session) -> None:
    """Lint package."""
    session.install("-e", ".[lint]")

    session.run("isort", "--profile", "black", ".")
    session.run("black", ".")
    session.run("mypy", "bavapi")
    session.run("pylint", "bavapi")
    session.run("pylint", "tests")


@nox.session(python=None)
def build(session: nox.Session) -> None:
    """Build package wheel and source distribution into dist folder."""
    session.install("build")

    session.run("python", "-m", "build")


@nox.session(python=False)
def docs_deploy(session: nox.Session) -> None:
    """Build and deploy documentation with version handling.

    If package minor version is not latest, deploy docs version.
    If package minor version is latest, deploy docs version and assign to `latest`.
    If package minor version exists, update docs version.

    Arguments
    ---------
    --push : flag (`--push`)
        Check versions from GitHub branch and deploy to branch.
    --version : str
        Override version from package (`--version=1.0`)

    Examples
    --------
    Run docs_deploy locally:

    `nox -s docs_deploy`

    Run docs_deploy for remote branch:

    `nox -s docs_deploy -- --push`

    Override package version:

    `nox -s docs_deploy -- --version=2.0.0`
    """
    try:
        import tomllib
    except ImportError:
        # Usually runs on latest version of python, just in case
        print("`tomllib` not found in system. Installing `tomli`...")
        session.run("pip", "install", "tomli")
        import tomli as tomllib

    def version_tuple(version: str) -> Tuple[int, ...]:
        return tuple(int(i) for i in version.split("."))

    def get_versions(args: Iterable[str]) -> set[Tuple[int, ...]]:
        out = cast(str, session.run("mike", "list", *args, silent=True))
        return {
            tuple(int(i) for i in v.partition(" ")[0].split("."))
            for v in out.splitlines()
        }

    if not (version_args := [i for i in session.posargs if i.startswith("--version=")]):
        # Get current package version
        with open("pyproject.toml", "rb") as file:
            version = version_tuple(tomllib.load(file)["project"]["version"])
    else:
        version = version_tuple(version_args[0].rpartition("=")[2])

    minor_str = ".".join(str(i) for i in version[:2])

    remote = "--push" in session.posargs
    remote_str = "remotely " if remote else ""
    list_args = ("-b", "gh-pages") if remote else ()
    deploy_args = ["--push", minor_str] if remote else [minor_str]

    versions = get_versions(list_args)

    if version[:2] in versions:
        print(f"Updating docs {remote_str}for version {minor_str}...")
    elif not all(version[:2] > v for v in versions):
        print(f"Deploying docs {remote_str}for version {minor_str}...")
    else:
        print(f"Deploying docs {remote_str}for version {minor_str} as latest...")
        deploy_args.extend(("latest", "--update-aliases"))

    session.run("mike", "deploy", *deploy_args)


@nox.session(python=False)
def docs_serve(session: nox.Session) -> None:
    """Serve documentation. Suitable for local development."""
    session.run("mkdocs", "serve")
