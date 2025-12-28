"""
JSON API Scraper Strategy
For sites that expose product data via JSON endpoints
"""

import requests
import time
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.headers import JSON_HEADERS


def scrape_json(
    url: str,
    brand: str = "Unknown",
    data_path: List[str] = None,
    name_key: str = "name",
    image_key: str = "image",
    price_key: str = "price"
) -> List[Dict[str, Any]]:
    """
    Scrape products from a JSON API endpoint
    
    Args:
        url: API URL
        brand: Brand name
        data_path: List of keys to navigate to products array (e.g., ["data", "products"])
        name_key: Key for product name
        image_key: Key for product image
        price_key: Key for product price
    
    Returns:
        List of product dictionaries
    """
    data_path = data_path or []
    
    try:
        time.sleep(1)
        response = requests.get(url, headers=JSON_HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"    [JSON] HTTP {response.status_code} for {url}")
            return []
        
        data = response.json()
        
        # Navigate to products array
        for key in data_path:
            if isinstance(data, dict):
                data = data.get(key, [])
            elif isinstance(data, list) and key.isdigit():
                data = data[int(key)]
            else:
                break
        
        if not isinstance(data, list):
            data = [data] if data else []
        
        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
            
            # Extract name (try multiple keys)
            name = None
            for key in [name_key, "name", "title", "product_name", "nombre"]:
                name = item.get(key)
                if name:
                    break
            
            if not name:
                continue
            
            # Extract image
            image = None
            for key in [image_key, "image", "image_url", "img", "thumbnail", "imagen"]:
                image = item.get(key)
                if image:
                    break
            
            # Handle nested image objects
            if isinstance(image, dict):
                image = image.get("src") or image.get("url")
            elif isinstance(image, list) and image:
                img_item = image[0]
                image = img_item.get("src") if isinstance(img_item, dict) else img_item
            
            # Extract price
            price = None
            for key in [price_key, "price", "precio", "cost"]:
                price_val = item.get(key)
                if price_val:
                    try:
                        price = float(str(price_val).replace(",", ".").replace("$", "").replace("€", ""))
                    except ValueError:
                        pass
                    break
            
            results.append({
                "brand": brand,
                "name": str(name),
                "image": image,
                "price": price,
                "fuente_datos": "json_api"
            })
        
        return results
        
    except requests.RequestException as e:
        print(f"    [JSON] Request error: {e}")
        return []
    except Exception as e:
        print(f"    [JSON] Error: {e}")
        return []
