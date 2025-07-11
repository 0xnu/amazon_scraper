# Amazon Products Scraper

[![PyPI version](https://badge.fury.io/py/amazon-scrape.svg)](https://badge.fury.io/py/amazon-scrape)

Scrape Amazon product data such as Product Name, Product Images, Number of Reviews, Price, Product URL, and ASIN.

## Requirements

Python 2.7 and later.

## Setup

You can install this package by using the pip tool and installing:

```python
pip install amazon-scrape
## OR
easy_install amazon-scrape
```

Install from source with:

```python
python setup.py install --user

## or `sudo python setup.py install` to install the package for all users
```

## Scraper Help
Execute this command `amazon_scraper --help` in the terminal.

```text
usage: amazon_scraper [-h] [--locale LOCALE] [--keywords KEYWORDS] [--url URL] [--api-key PROXY_API_KEY] [--pages PAGES] [-r]

optional arguments:
  -h, --help            show this help message and exit
  --locale LOCALE       Amazon locale (e.g., "com", "co.uk", "de", etc.)
  --keywords KEYWORDS   Search keywords
  --url URL             Amazon URL
  --api-key             Scraper API Key
  --pages PAGES         Number of pages to scrape
  -r, --review          Scrape reviews
```

## Usage Example

```python
# Specify locale, keywords, API key, and number of pages to scrape:
amazon_scraper --locale com --keywords "laptop" --api-key "your_api_key" --pages 10

## Specify only keywords and API key (will default to "co.uk" locale and 20 pages):
amazon_scraper --keywords "iphone" --api-key "your_api_key"

## Specify a direct Amazon URL and API key (will default to "co.uk" locale and 20 pages):
amazon_scraper --url "https://www.amazon.de/s?k=iphone&crid=1OHYY6U6OGCK5&sprefix=ipho%2Caps%2C335&ref=nb_sb_noss_2" --api-key "your_api_key"

## Specify locale and Amazon URL (will default to 20 pages):
amazon_scraper --locale de --url "https://www.amazon.de/s?k=iphone&crid=1OHYY6U6OGCK5&sprefix=ipho%2Caps%2C335&ref=nb_sb_noss_2" --api-key "your_api_key"

## Specify review to scrape product(s) reviews:
amazon_scraper --keywords "watches" --api-key "your_api_key --review
```

## Create Scraper API Account

Sign up for a Scraper API [user account](https://www.scraperapi.com/?fp_ref=finbarrs11).


## License

This project is licensed under the [MIT License](./LICENSE).


## Copyright

(c) 2023 - 2025 [Finbarrs Oketunji](https://finbarrs.eu). All Rights Reserved.
