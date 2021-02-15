#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(
    author="Casper van der Wel",
    author_email="caspervdw@gmail.com",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A fast interface between SQLAlchemy and Numpy",
    install_requires=["sqlalchemy>=1.1", "numpy>=1.13"],
    extras_require={"test": ["pytest>=3"], "geo": ["geoalchemy2>=0.6", "pygeos>=0.5"]},
    license="BSD license",
    long_description=readme,
    include_package_data=True,
    keywords="condenser",
    name="condenser",
    packages=["condenser"],
    url="https://github.com/nens/condenser",
    version="0.1.0",
    zip_safe=False,
)
