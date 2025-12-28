"""
Base scraper class with common functionality
"""

import requests
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

import sys
sys.path.append('..')
from config import DEFAULT_HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, brand: str, base_url: str):
        self.brand = brand
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page"""
        try:
            time.sleep(REQUEST_DELAY)  # Be respectful
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.RequestException as e:
            print(f"[{self.brand}] Error fetching {url}: {e}")
            return None
    
    def get_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON data"""
        try:
            time.sleep(REQUEST_DELAY)
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[{self.brand}] Error fetching JSON {url}: {e}")
            return None
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean and normalize text"""
        if not text:
            return None
        return ' '.join(text.strip().split())
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text like '$29.99' or '29,99€'"""
        import re
        if not text:
            return None
        # Remove currency symbols and normalize
        cleaned = re.sub(r'[^\d.,]', '', text)
        cleaned = cleaned.replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def extract_number(self, text: str) -> Optional[float]:
        """Extract first number from text"""
        import re
        if not text:
            return None
        match = re.search(r'[\d.]+', text)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    @abstractmethod
    def scrape_products(self) -> List[Dict[str, Any]]:
        """Scrape all products from this brand. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def scrape_product_details(self, product_url: str) -> Dict[str, Any]:
        """Scrape detailed info from a product page. Must be implemented by subclasses."""
        pass
