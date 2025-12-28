"""
WooCommerce Scraper Strategy
For WordPress/WooCommerce sites like AmeraLabs
"""

import requests
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.headers import HEADERS

def scrape_woocommerce(
    url: str,
    brand: str = "Unknown",
    title_selector: str = ".woocommerce-loop-product__title",
    price_selector: str = ".price",
    img_selector: str = "img"
) -> List[Dict[str, Any]]:
    """
    Scrape products from a WooCommerce shop page
    """
    try:
        time.sleep(1)
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        # Encoding fix for compressed/weird responses
        html_content = response.content.decode("utf-8", errors="ignore")
        
        soup = BeautifulSoup(html_content, "lxml") # Use lxml for robustness
        products = []
        
        # WooCommerce standard loop item - try multiple common wrappers
        items = soup.select(".product") 
        if not items: items = soup.select("li.product")
        if not items: items = soup.select(".type-product")
        if not items: items = soup.select(".product_item") # Ameralabs custom?
        
        for item in items:
            # Title
            title_el = item.select_one(title_selector)
            if not title_el: title_el = item.select_one("h2")
            if not title_el: title_el = item.select_one(".product-title") # ColorFabb
            
            if not title_el:
                continue
            name = title_el.get_text(strip=True)
            
            # Image
            img_el = item.select_one(img_selector)
            image_url = None
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src")
            
            # Price
            price_el = item.select_one(price_selector)
            price = None
            if price_el:
                import re
                match = re.search(r'[\d.,]+', price_el.get_text())
                if match:
                    try:
                        price = float(match.group().replace(',', '.'))
                    except ValueError:
                        pass
            
            # URL
            link_el = item.select_one("a.woocommerce-LoopProduct-link") or item.select_one("a")
            product_url = None
            if link_el:
                product_url = link_el.get("href")

            products.append({
                "brand": brand,
                "name": name,
                "image": image_url,
                "price": price,
                "url": product_url,
                "fuente_datos": "woocommerce_scrape"
            })
            
        return products

    except Exception as e:
        print(f"    [WooCommerce] Error: {e}")
        return []
