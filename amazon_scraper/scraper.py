import requests
from bs4 import BeautifulSoup
import csv
import json
import random
import argparse

class AmazonScraper:
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
    ]

    def __init__(self, locale="co.uk", keyword=None, url=None, api_key=None, pages=20):
        base_url = f"https://www.amazon.{locale}/s"
        if keyword:
            self.url = f"http://api.scraperapi.com?api_key={api_key}&url={base_url}?k={keyword}"
        else:
            self.url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"
        self.api_key = api_key
        self.pages = pages
        self.csv_file = open('amazon_products.csv', 'w', newline='')
        self.json_file = open('amazon_products.json', 'w')
        self.writer = csv.writer(self.csv_file)
        self.json_data = []
        self.locale = locale

    def start_scraping(self):
        self.writer.writerow(["product_name", "product_images", "number_of_reviews", "price", "product_url", "asin"])
        for page in range(1, self.pages + 1):
            url = self.url + "&page=" + str(page)
            headers = {"User-Agent": random.choice(self.user_agents)}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.find_all("div", {"class": "sg-col-inner"})

            for product in products:
                # Product name
                name = product.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
                if name is not None:
                    name = name.text
                else:
                    continue  # Skip if no product name

                # Product images
                images = product.find_all("img", {"class": "s-image"})
                if images is not None:
                    images = [image['src'] for image in images]
                else:
                    images = []

                # Number of Reviews
                number_of_reviews = product.find("span", {"class": "a-size-base"})
                if number_of_reviews is not None:
                    number_of_reviews = number_of_reviews.text
                else:
                    number_of_reviews = ''

                # Price
                price = product.find("span", {"class": "a-offscreen"})
                if price is not None:
                    price = price.text
                else:
                    price = ''

                # Product URL
                product_url = product.find("a", {"class": "a-link-normal"})
                if product_url is not None:
                    product_url = f'https://www.amazon.{self.locale}' + product_url['href']
                else:
                    product_url = ''

                # ASIN
                asin = product_url.split("/dp/")[1].split("/")[0] if "/dp/" in product_url else ''

                # Write to CSV
                self.writer.writerow([name, ", ".join(images), number_of_reviews, price, product_url, asin])

                # Add to JSON data
                self.json_data.append({
                    "product_name": name,
                    "product_images": images,
                    "number_of_reviews": number_of_reviews,
                    "price": price,
                    "product_url": product_url,
                    "asin": asin
                })

        json.dump(self.json_data, self.json_file, indent=4)

    def close_files(self):
        self.csv_file.close()
        self.json_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--locale', type=str, default='co.uk', help='Amazon locale (e.g., "com", "co.uk", "de", etc.)')
    parser.add_argument('--keywords', type=str, help='Search keywords')
    parser.add_argument('--url', type=str, help='Amazon URL')
    parser.add_argument('--proxy_api_key', type=str, help='API Key')
    parser.add_argument('--pages', type=int, default=20, help='Number of pages to scrape')
    args = parser.parse_args()

    scraper = AmazonScraper(args.locale, args.keywords, args.url, args.proxy_api_key, args.pages)
    scraper.start_scraping()
    scraper.close_files()

if __name__ == '__main__':
    main()
