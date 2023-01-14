import setuptools
from visualisation_package import __version__

# Read in the requirements.txt file
with open("requirements.txt") as f:
    requirements = []
    for library in f.read().splitlines():
        requirements.append(library)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vistools_for_screening666",
    version=__version__,
    author="Ieva, Frances, Alistair",
    # I've created a specific email account before and forwarded to my own.
    author_email="ij229@exeter.ac.uk",
    license="The MIT License (MIT)",
    description="A collection of tools to aid with visualisation of screening\
        uptake data",
    # read in from readme.md and will appear on PyPi
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mangotangochick/visualisation-tools-for-screening.git",
    packages=setuptools.find_packages(),
    # if true look in MANIFEST.in for data files to include
    include_package_data=True,
    # these are for documentation 
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6.9',
    install_requires=requirements,
)