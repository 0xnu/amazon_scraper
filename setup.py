# coding: utf-8

import sys
from setuptools import setup, find_packages  # noqa: H301
from distutils.core import Extension

NAME = "amazon_scrape"
VERSION = "1.0.1"
REQUIRES = ["beautifulsoup4", "requests"]

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'LONG_DESCRIPTION.rst')) as f:
    long_description = f.read()

macros = []
if sys.platform.startswith('freebsd') or sys.platform == 'darwin':
    macros.append(('PLATFORM_BSD', '1'))
elif 'linux' in sys.platform:
    macros.append(('_GNU_SOURCE', ''))

setup(
    name=NAME,
    version=VERSION,
    description="Scrape Amazon product data such as Product Name, Product Images, Product URL, Number of Reviews, ASIN, and Price.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Finbarrs Oketunji",
    author_email="f@finbarrs.eu",
    url="https://finbarrs.eu",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRES,
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points={
        'console_scripts': [
            'amazon_scraper = amazon_scraper.scraper:main',
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/0xnu/amazonproducts/issues",
        "Changes": "https://github.com/0xnu/amazonproducts/blob/main/CHANGELOG.md",
        "Documentation": "https://github.com/0xnu/amazonproducts/blob/main/README.md",
        "Source Code": "https://github.com/0xnu/amazonproducts",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["wheel"],
    keywords=["amazon", "products", "ecommerce", "price", "reviews", "ratings"],
    license='MIT',
)
