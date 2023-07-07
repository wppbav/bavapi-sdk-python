"""Package tooling session definitions for `nox`"""

import json
import os
import pathlib
from typing import Dict, List

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
    session.conda_install("--file", "requirements.txt")
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
    session.conda_install("--file", "requirements.txt")
    session.install("-e", ".[test]")

    session.run("pytest", "-m", "not e2e", *session.posargs, external=True)


@nox.session(python="3.11", venv_backend="mamba", reuse_venv=True)
def tests_mamba_e2e(session: nox.Session) -> None:
    """Run end to end tests locally with `mamba` as the backend."""
    session.conda_install("--file", "requirements.txt")
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
    session.conda_install("--file", "requirements.txt")
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
    session.install("pylint", "mypy")
    session.install("-e", ".")

    session.run("pylint", "bavapi")
    session.run("mypy", "bavapi")


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


@nox.session(python=None)
def publish(session: nox.Session) -> None:
    """Publish package wheel and source distribution to PyPI."""
    session.install("twine")

    session.run("twine", "upload", "dist/*")
