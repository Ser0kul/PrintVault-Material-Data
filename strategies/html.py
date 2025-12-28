"""
HTML Scraper Strategy
For sites that don't use Shopify but have standard HTML structure
"""

import requests
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.headers import HEADERS


def scrape_html(
    url: str,
    brand: str = "Unknown",
    card_selector: str = ".product-card",
    name_selector: str = ".product-title",
    img_selector: str = "img",
    price_selector: str = ".price",
    link_selector: str = "a"
) -> List[Dict[str, Any]]:
    """
    Scrape products from HTML page using CSS selectors
    
    Args:
        url: Page URL to scrape
        brand: Brand name
        card_selector: CSS selector for product cards
        name_selector: CSS selector for product name (within card)
        img_selector: CSS selector for product image (within card)
        price_selector: CSS selector for price (within card)
        link_selector: CSS selector for product link (within card)
    
    Returns:
        List of product dictionaries
    """
    try:
        time.sleep(1)  # Be respectful
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"    [HTML] HTTP {response.status_code} for {url}")
            return []
        
        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.select(card_selector)
        
        if not cards:
            # Try alternative common selectors
            alt_selectors = [
                ".product", ".product-item", ".product-tile",
                "[data-product]", ".grid-item", ".collection-product"
            ]
            for sel in alt_selectors:
                cards = soup.select(sel)
                if cards:
                    break
        
        results = []
        for card in cards:
            # Name
            name_el = card.select_one(name_selector)
            if not name_el:
                # Try alternatives
                for sel in ["h2", "h3", "h4", ".title", ".name", "[data-product-title]"]:
                    name_el = card.select_one(sel)
                    if name_el:
                        break
            
            name = name_el.get_text(strip=True) if name_el else None
            if not name:
                continue
            
            # Image
            img_el = card.select_one(img_selector)
            image_url = None
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src")
                if image_url and image_url.startswith("//"):
                    image_url = "https:" + image_url
            
            # Price
            price = None
            price_el = card.select_one(price_selector)
            if price_el:
                import re
                price_text = price_el.get_text()
                match = re.search(r'[\d.,]+', price_text.replace(',', '.'))
                if match:
                    try:
                        price = float(match.group().replace(',', '.'))
                    except ValueError:
                        pass
            
            # Link
            product_url = None
            link_el = card.select_one(link_selector)
            if link_el and link_el.has_attr("href"):
                href = link_el["href"]
                if href.startswith("/"):
                    # Make absolute
                    from urllib.parse import urljoin
                    product_url = urljoin(url, href)
                elif href.startswith("http"):
                    product_url = href
            
            results.append({
                "brand": brand,
                "name": name,
                "image": image_url,
                "price": price,
                "url": product_url,
                "fuente_datos": "html_scrape"
            })
        
        return results
        
    except requests.RequestException as e:
        print(f"    [HTML] Request error: {e}")
        return []
    except Exception as e:
        print(f"    [HTML] Error: {e}")
        return []
