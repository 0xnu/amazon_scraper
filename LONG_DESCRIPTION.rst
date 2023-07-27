Amazon Products Scraper
=======================

.. image:: https://badge.fury.io/py/amazon_products_scraper.svg
    :target: https://badge.fury.io/py/amazon_products_scraper
    :alt: amazon_products_scraper Python Package Version

Scrape Amazon product data such as Product Name, Product Images, Rating Count, and Price.

Requirements
------------

Python 2.7 and later.


Setup
-----

You can install this package by using the pip tool and installing:

.. code-block:: bash

	$ pip install amazon-scrape

Or:

.. code-block:: bash

	$ easy_install amazon-scrape


Usage Example
-------------

.. code-block:: python

    ## Specify locale, keywords, API key, and number of pages to scrape
    amazon_scraper --locale com --keywords "laptop" --proxy_api_key "your_api_key" --pages 10

    ## Specify only keywords and API key (will default to "co.uk" locale and 20 pages):
    amazon_scraper --keywords "iphone" --proxy_api_key "your_api_key"

    ## Specify a direct Amazon URL and API key (will default to "co.uk" locale and 20 pages):
    amazon_scraper --url "https://www.amazon.de/s?k=iphone&crid=1OHYY6U6OGCK5&sprefix=ipho%2Caps%2C335&ref=nb_sb_noss_2" --proxy_api_key "your_api_key"

    ## Specify locale and Amazon URL (will default to 20 pages):
    amazon_scraper --locale de --url "https://www.amazon.de/s?k=iphone&crid=1OHYY6U6OGCK5&sprefix=ipho%2Caps%2C335&ref=nb_sb_noss_2" --proxy_api_key "your_api_key"


Create Scraper API Account
--------------------------

Sign up for a Scraper API `user account`_.

.. _user account: https://www.scraperapi.com/?fp_ref=finbarrs11


License
-------

This project is licensed under the `MIT License`_.  

.. _MIT License: https://github.com/0xnu/amazonproducts/blob/main/LICENSE


Copyright
---------

Copyright |copy| 2023 `Finbarrs Oketunji`_. All Rights Reserved.

.. |copy| unicode:: 0xA9 .. copyright sign
.. _Finbarrs Oketunji: https://finbarrs.eu