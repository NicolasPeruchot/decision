"""Manage dependencies."""
import pathlib

from typing import List

from setuptools import find_packages, setup


def _read(fname: str) -> str:
    with open(pathlib.Path(fname)) as fh:
        data = fh.read()
    return data


base_packages: List[str] = []

dev_packages = [
    "pandas",
    "Jinja2",
    "black",
    "ipykernel",
    "isort",
    "pre-commit",
    "gurobipy",
    "black",
    "plotly",
]


setup(
    name="decision",
    version="0.0.1",
    packages=find_packages(exclude=["notebooks"]),
    long_description=_read("README.md"),
    install_requires=base_packages,
    extras_require={
        "dev": dev_packages,
    },
)
