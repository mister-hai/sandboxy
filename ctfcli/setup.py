# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname), "r") as fp:
            return fp.read().strip()
    except IOError:
        return ""


setup(
    name="CTFCLI",
    version="wat",
    author="MRHAI",
    author_email="MRHAI@HAX.NET",
    license="Apache 2.0",
    description="Tool for creating and running Capture The Flag competitions",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords=["ctf"],
    classifiers=[],
    zip_safe=False,
    install_requires=[
        "cookiecutter==1.6.0",
        "fire==0.2.1",
        "pyyaml==5.4",
        "Pygments==2.7.4",
        "requests==2.22.0",
        "colorama==0.4.3",
        "gitpython",
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ctf = ctfcli:main"]},
)
