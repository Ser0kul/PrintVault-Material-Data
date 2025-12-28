"""
Shopify Store Scraper Strategy
Works with 80% of 3D printing stores (Anycubic, Creality, Phrozen, etc.)
Uses the public /products.json API endpoint
"""

import requests
import time
import re
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.headers import JSON_HEADERS


def get_shopify_json_url(base_url: str) -> str:
    """Convert any Shopify URL to products.json endpoint"""
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    # If it's a collection URL, use collection products
    if '/collections/' in base_url:
        return f"{base_url}/products.json?limit=250"
    
    # Otherwise use main products endpoint
    # Extract base domain
    match = re.match(r'(https?://[^/]+)', base_url)
    if match:
        return f"{match.group(1)}/products.json?limit=250"
    
    return f"{base_url}/products.json?limit=250"


def detect_product_type(title: str, product_type: str = "") -> str:
    """Detect material type from product title"""
    title_lower = (title + " " + product_type).lower()
    
    # Filament types
    if "pla+" in title_lower or "pla plus" in title_lower:
        return "PLA+"
    if "petg" in title_lower:
        return "PETG"
    if "abs" in title_lower:
        return "ABS"
    if "asa" in title_lower:
        return "ASA"
    if "tpu" in title_lower or "tpe" in title_lower or "flex" in title_lower:
        return "TPU"
    if "nylon" in title_lower or "pa12" in title_lower or "pa6" in title_lower:
        return "Nylon"
    if "silk" in title_lower:
        return "Silk PLA"
    if "matte" in title_lower:
        return "Matte PLA"
    if "wood" in title_lower:
        return "Wood"
    if "carbon" in title_lower or "cf" in title_lower:
        return "Carbon Fiber"
    if "pla" in title_lower:
        return "PLA"
    
    # Resin types
    if "water wash" in title_lower:
        return "Water Washable"
    if "abs-like" in title_lower or "abs like" in title_lower:
        return "ABS-Like"
    if "tough" in title_lower:
        return "Tough"
    if "flexible" in title_lower or "elastic" in title_lower:
        return "Flexible"
    if "dental" in title_lower:
        return "Dental"
    if "castable" in title_lower:
        return "Castable"
    if "clear" in title_lower or "transparent" in title_lower:
        return "Transparent"
    if "resin" in title_lower:
        return "Standard"
    
    return "Standard"


def detect_color(title: str, variant_title: str = "") -> tuple:
    """Detect color from title, returns (hex, name)"""
    text = (title + " " + variant_title).lower()
    
    colors = {
        "black": ("#000000", "Black"),
        "white": ("#ffffff", "White"),
        "grey": ("#808080", "Grey"),
        "gray": ("#808080", "Grey"),
        "red": ("#ef4444", "Red"),
        "blue": ("#3b82f6", "Blue"),
        "green": ("#22c55e", "Green"),
        "yellow": ("#eab308", "Yellow"),
        "orange": ("#f97316", "Orange"),
        "purple": ("#a855f7", "Purple"),
        "pink": ("#ec4899", "Pink"),
        "clear": ("#e5e7eb", "Clear"),
        "transparent": ("#e5e7eb", "Transparent"),
        "silver": ("#c0c0c0", "Silver"),
        "gold": ("#ffd700", "Gold"),
        "beige": ("#d4a574", "Beige"),
        "navy": ("#3f4756", "Navy"),
        "teal": ("#14b8a6", "Teal"),
        "cyan": ("#06b6d4", "Cyan"),
    }
    
    for keyword, (hex_code, name) in colors.items():
        if keyword in text:
            return (hex_code, name)
    
    return ("#808080", "Grey")


def scrape_shopify(base_url: str, brand: str = "Unknown", product_category: str = "filament") -> List[Dict[str, Any]]:
    """
    Scrape products from a Shopify store using products.json API
    Tries multiple endpoint patterns for robustness.
    """
    # Define potential endpoints
    base_clean = base_url.rstrip('/')
    endpoints = [
        f"{base_clean}/products.json?limit=250",
    ]
    
    # If it's a collection URL, add collection-specific endpoint
    if '/collections/' in base_clean:
         # Try /collections/name/products.json
        endpoints.append(f"{base_clean}/products.json?limit=250")
        # Try base domain products.json as fallback
        match = re.match(r'(https?://[^/]+)', base_clean)
        if match:
             endpoints.append(f"{match.group(1)}/products.json?limit=250")
    
    products_found = []
    
    # Try each endpoint until success
    for json_url in endpoints:
        try:
            time.sleep(1)  # Be respectful
            response = requests.get(json_url, headers=JSON_HEADERS, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            products = data.get("products", [])
            
            if not products:
                continue
                
            results = []
            for p in products:
                title = p.get("title", "")
                product_type = p.get("product_type", "")
                
                # Get first image
                images = p.get("images", [])
                image_url = images[0].get("src") if images else None
                
                # Get first variant for price
                variants = p.get("variants", [])
                price = None
                if variants:
                    price_str = variants[0].get("price")
                    if price_str:
                        try:
                            price = float(price_str)
                        except ValueError:
                            pass
                
                # Detect type and color
                material_type = detect_product_type(title, product_type)
                color_hex, color_name = detect_color(title)
                
                # Build tags
                tags = p.get("tags", [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(",")]
                
                results.append({
                    "brand": brand,
                    "name": title,
                    "type": material_type,
                    "image": image_url,
                    "color": color_hex,
                    "color_name": color_name,
                    "price": price,
                    "tags": tags[:5] if tags else [material_type],
                    "description": p.get("body_html", "")[:200] if p.get("body_html") else None,
                    "url": f"{base_clean.split('/collections')[0]}/products/{p.get('handle')}",
                    "fuente_datos": "shopify_api"
                })
            
            if results:
                return results # Return first successful batch
            
        except Exception:
            continue
            
    return []
