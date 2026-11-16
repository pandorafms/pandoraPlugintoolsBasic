import os
import sys

from setuptools import find_packages, setup

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="pandoraPlugintools-basic",
    version="1.1.2",
    author="PandoraFMS projects department",
    author_email="<info@pandorafms.com>",
    description="A plugin tool set of basic functions for pandorafms",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pandorafms/pandoraPlugintoolsBasic",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
