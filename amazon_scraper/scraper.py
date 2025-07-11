import requests
from bs4 import BeautifulSoup
import csv
import json
import random
import argparse
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin
from contextlib import contextmanager
from tqdm import tqdm


class AmazonScraperError(Exception):
    """Custom exception for Amazon scraper errors"""
    pass


class FileManager:
    """Manages file operations for CSV and JSON outputs"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.files = {}
        
    @contextmanager
    def get_files(self, review: bool = False):
        """Context manager for file handling"""
        try:
            # Product files
            product_csv_path = self.output_dir / 'amazon_products.csv'
            product_json_path = self.output_dir / 'amazon_products.json'
            
            self.files['product_csv'] = open(product_csv_path, 'w', newline='', encoding='utf-8')
            self.files['product_json'] = open(product_json_path, 'w', encoding='utf-8')
            
            # Review files if needed
            if review:
                review_csv_path = self.output_dir / 'amazon_reviews.csv'
                review_json_path = self.output_dir / 'amazon_reviews.json'
                
                self.files['review_csv'] = open(review_csv_path, 'w', newline='', encoding='utf-8')
                self.files['review_json'] = open(review_json_path, 'w', encoding='utf-8')
            
            yield self.files
            
        finally:
            for file_obj in self.files.values():
                if file_obj and not file_obj.closed:
                    file_obj.close()
            self.files.clear()


class AmazonScraper:
    """Amazon scraper with ScraperAPI integration"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    SUPPORTED_LOCALES = {
        'com': 'amazon.com',
        'co.uk': 'amazon.co.uk',
        'de': 'amazon.de',
        'fr': 'amazon.fr',
        'it': 'amazon.it',
        'es': 'amazon.es',
        'ca': 'amazon.ca',
        'com.au': 'amazon.com.au',
        'co.jp': 'amazon.co.jp',
        'in': 'amazon.in'
    }
    
    def __init__(self, locale: str = "co.uk", keyword: Optional[str] = None, 
                 url: Optional[str] = None, api_key: Optional[str] = None, 
                 pages: int = 20, review: bool = False, output_dir: str = "output"):
        
        self.locale = self._validate_locale(locale)
        self.api_key = self._validate_api_key(api_key)
        self.pages = max(1, pages)
        self.review = review
        self.base_url = f"https://www.{self.SUPPORTED_LOCALES[self.locale]}"
        
        # Set up logging
        self._setup_logging()
        
        # Initialize file manager
        self.file_manager = FileManager(output_dir)
        
        # Build URL
        self.url = self._build_url(keyword, url)
        
        # Data storage
        self.product_data = []
        self.review_data = []
        
        # Request settings
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting
        self.request_delay = 1.0
        self.max_retries = 3
        
    def _validate_locale(self, locale: str) -> str:
        """Validate and return locale"""
        if locale not in self.SUPPORTED_LOCALES:
            raise AmazonScraperError(f"Unsupported locale: {locale}. Supported: {list(self.SUPPORTED_LOCALES.keys())}")
        return locale
    
    def _validate_api_key(self, api_key: Optional[str]) -> str:
        """Validate API key"""
        if not api_key:
            raise AmazonScraperError("ScraperAPI key is required")
        return api_key
    
    def _setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('amazon_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _build_url(self, keyword: Optional[str], url: Optional[str]) -> str:
        """Build scraping URL"""
        if keyword:
            search_url = f"{self.base_url}/s?k={keyword.replace(' ', '+')}"
        elif url:
            search_url = url
        else:
            raise AmazonScraperError("Either keyword or URL must be provided")
        
        scraper_url = f"http://api.scraperapi.com?api_key={self.api_key}&url={search_url}"
        self.logger.info(f"Built URL: {scraper_url}")
        return scraper_url
    
    def _make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        
        try:
            time.sleep(self.request_delay)
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request failed: {e}")
            
            if retries < self.max_retries:
                wait_time = (retries + 1) * 2
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                return self._make_request(url, retries + 1)
            
            self.logger.error(f"Failed to fetch {url} after {self.max_retries} retries")
            return None
    
    def _extract_product_data(self, product_element) -> Optional[Dict]:
        """Extract product data from HTML element"""
        try:
            # Product name
            name_element = product_element.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
            if not name_element:
                name_element = product_element.find("h2", {"class": "a-size-mini"})
            
            if not name_element:
                return None
                
            name = name_element.get_text(strip=True)
            
            # Product images
            images = []
            img_elements = product_element.find_all("img", {"class": "s-image"})
            for img in img_elements:
                if img.get('src'):
                    images.append(img['src'])
            
            # Number of reviews
            review_count = ""
            review_element = product_element.find("span", {"class": "a-size-base"})
            if review_element:
                review_count = review_element.get_text(strip=True)
            
            # Price
            price = ""
            price_element = product_element.find("span", {"class": "a-offscreen"})
            if price_element:
                price = price_element.get_text(strip=True)
            
            # Product URL
            product_url = ""
            url_element = product_element.find("a", {"class": "a-link-normal"})
            if url_element and url_element.get('href'):
                product_url = urljoin(self.base_url, url_element['href'])
            
            # ASIN
            asin = ""
            if "/dp/" in product_url:
                try:
                    asin = product_url.split("/dp/")[1].split("/")[0]
                except IndexError:
                    pass
            
            return {
                "product_name": name,
                "product_images": images,
                "number_of_reviews": review_count,
                "price": price,
                "product_url": product_url,
                "asin": asin
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting product data: {e}")
            return None
    
    def _scrape_reviews(self, asin: str, product_name: str, product_url: str) -> List[str]:
        """Scrape product reviews"""
        if not asin:
            return []
            
        review_url = f"{self.base_url}/product-reviews/{asin}"
        scraper_review_url = f"http://api.scraperapi.com?api_key={self.api_key}&url={review_url}"
        
        response = self._make_request(scraper_review_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        reviews = []
        
        review_elements = soup.find_all("span", {"data-hook": "review-body"})
        for review_element in review_elements:
            review_text = review_element.get_text(strip=True)
            if review_text:
                reviews.append(review_text)
        
        return reviews
    
    def start_scraping(self):
        """Main scraping method"""
        self.logger.info(f"Starting scraping for {self.pages} pages")
        
        with self.file_manager.get_files(self.review) as files:
            # Set up CSV writers
            product_writer = csv.writer(files['product_csv'])
            product_writer.writerow(["product_name", "product_images", "number_of_reviews", "price", "product_url", "asin"])
            
            review_writer = None
            if self.review:
                review_writer = csv.writer(files['review_csv'])
                review_writer.writerow(["product_name", "product_reviews", "product_url", "asin"])
            
            # Scrape pages
            for page in tqdm(range(1, self.pages + 1), desc="Scraping Pages"):
                self.logger.info(f"Scraping page {page}")
                
                page_url = f"{self.url}&page={page}"
                response = self._make_request(page_url)
                
                if not response:
                    self.logger.warning(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Find product containers
                product_containers = soup.find_all("div", {"class": "sg-col-inner"})
                if not product_containers:
                    product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
                
                self.logger.info(f"Found {len(product_containers)} products on page {page}")
                
                for container in product_containers:
                    product_data = self._extract_product_data(container)
                    
                    if not product_data:
                        continue
                    
                    # Write to CSV
                    product_writer.writerow([
                        product_data["product_name"],
                        ", ".join(product_data["product_images"]),
                        product_data["number_of_reviews"],
                        product_data["price"],
                        product_data["product_url"],
                        product_data["asin"]
                    ])
                    
                    # Add to JSON data
                    self.product_data.append(product_data)
                    
                    # Scrape reviews if requested
                    if self.review and product_data["asin"]:
                        reviews = self._scrape_reviews(
                            product_data["asin"],
                            product_data["product_name"],
                            product_data["product_url"]
                        )
                        
                        if reviews:
                            review_entry = {
                                "product_name": product_data["product_name"],
                                "product_reviews": reviews,
                                "product_url": product_data["product_url"],
                                "asin": product_data["asin"]
                            }
                            
                            self.review_data.append(review_entry)
                            
                            if review_writer:
                                review_writer.writerow([
                                    review_entry["product_name"],
                                    ", ".join(reviews),
                                    review_entry["product_url"],
                                    review_entry["asin"]
                                ])
            
            # Write JSON files
            json.dump(self.product_data, files['product_json'], indent=4, ensure_ascii=False)
            if self.review:
                json.dump(self.review_data, files['review_json'], indent=4, ensure_ascii=False)
        
        self.logger.info(f"Scraping completed. Found {len(self.product_data)} products")
        if self.review:
            self.logger.info(f"Scraped reviews for {len(self.review_data)} products")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Amazon Scraper with ScraperAPI")
    parser.add_argument('--locale', type=str, default='co.uk', 
                       help='Amazon locale (e.g., "com", "co.uk", "de", etc.)')
    parser.add_argument('--keywords', type=str, help='Search keywords')
    parser.add_argument('--url', type=str, help='Amazon URL')
    parser.add_argument('--api-key', type=str, required=True, help='ScraperAPI Key')
    parser.add_argument('--pages', type=int, default=20, help='Number of pages to scrape')
    parser.add_argument('--review', action='store_true', help='Scrape reviews')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        scraper = AmazonScraper(
            locale=args.locale,
            keyword=args.keywords,
            url=args.url,
            api_key=args.api_key,
            pages=args.pages,
            review=args.review,
            output_dir=args.output_dir
        )
        
        scraper.start_scraping()
        
    except AmazonScraperError as e:
        print(f"Scraper Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())