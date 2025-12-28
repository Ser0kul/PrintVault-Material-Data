#!/usr/bin/env python3
"""
Material Database Scraper v2.6 (Industrial Grade)
Multi-strategy scraper with hybrid Auto/Manual/JS/HTML capabilities.

Usage:
    python scraper.py [--resins] [--filaments] [--dry-run]
"""

import json
import argparse
import os
import sys
import re
from typing import List, Dict, Any

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.shopify import scrape_shopify
from strategies.html import scrape_html
from strategies.json_api import scrape_json
from strategies.woocommerce import scrape_woocommerce
# Try to import JS scraper
try:
    from strategies.js_fallback import scrape_js
except ImportError:
    scrape_js = None

from utils.image_downloader import download_image

def scrape_manual(config: Dict) -> List[Dict]:
    """Manually curated strategy for sites where scraping is not viable"""
    products = []
    brand = config.get("brand")
    default_image = config.get("default_image", "https://placehold.co/600x600/1a1a1a/cccccc?text=No+Image")
    
    for name in config.get("products", []):
         products.append({
             "brand": brand,
             "name": name,
             "type": "Standard",
             "image": default_image,
             "fuente_datos": "manual_curated"
         })
    return products

# Global Blacklist for Resins
FILAMENT_BLACKLIST = [
    r'\bfilament\b', r'\bpla\b', r'\bpetg\b', r'\bpet-cf\b', r'\btpu\b', 
    r'\bpeba\b', r'\bpa-cf\b', r'\bnylon\b', r'\basa\b', r'\bspidermaker\b',
    r'フィラメント'
]

HARDWARE_BLACKLIST = [
    r'\bhalot\b', r'\bmage\b', r'\bcombo\b', r'\bplate\b', 
    r'\btoolkit\b', r'\blcd\b', r'\bscreen\b', r'\bfep\b', r'\bnfep\b', r'\bfilm\b',
    r'\bcuring station\b', r'\bwashing station\b', r'\bwash.*cure\b', r'\bcure.*wash\b',
    r'\bheater\b', r'\bretrofit\b', r'\bdryer\b', r'\bkobra\b', r'\bneptune\b',
    r'\bnozzle\b', r'\bhotend\b', r'\bextruder\b', r'\bplatform\b', r'\bmagnetic\b',
    r'\bairpure\b', r'\btube\b', r'\bhub\b', r'\bkit\b', r'\bpart\b', r'\badhesive\b',
    r'\bsheet\b', r'\bglass\b', r'\bboard\b', r'\bcontroller\b', r'\bcable\b', 
    r'\bmodule\b', r'\bsensor\b', r'\bfan\b', r'\bmotor\b', r'\bcamera\b', r'\bled\b',
    r'\bcfs\b', r'\bspacepi\b', r'\bstorage\b', r'\bbox\b', r'\bsystem\b',
    r'\bscrew\b', r'\bwiper\b', r'\bcutter\b', r'\bassembly\b', r'\bpcba\b', 
    r'\bantenna\b', r'\bpower\s*supply\b', r'\bwire\b', r'\btools\b', r'\bshaft\b',
    r'\bnut\b', r'filter', r'switch', r'coupler', r'holder', r'ace\s*pro', r'belt', 
    r'touchscreen', r'screen', r'relay', r'spring', r'lock', r'\bhose\b', r'reusable\s*spool',
    r'coating'
]

NON_PRODUCT_BLACKLIST = [
    r'guide', r'review', r'recensione', r'guarantee', r'support', r'shipping', r'service', 
    r'years of', r'black friday', r'deal', r'campfire', r'202.', r'bundle', r'pack', 
    r'set', r'gift', r'protection', r'deposit', r'claim', r'link', r'coupon', r'discount', 
    r'sale', r'clearance', r'refurbished', r'renewed', r'usado', r'reacondicionado',
    r'membership', r'subscription', r'prize', r'reward', r'seel', r'insurance', 
    r'soleyin', r'3d\s*pen'
]

RESIN_BLACKLIST = [
    r'resin', r'wash', r'cure', r'dlp', r'sla', r'photon', r'mono', r'halot', 
    r'creality\s*3d\s*printer', r'anycubic\s*3d\s*printer', r'elegoo\s*3d\s*printer'
]

def validate_product(product, category="resin"):
    name_lower = product.get('name', '').lower()
    tags = [t.lower() for t in product.get('tags', [])]
    
    # Combination of name and tags for filtering
    all_text = name_lower + " " + " ".join(tags)
    
    # Only apply strict filament filters for resin category
    if category == "resin":
        # Check Filaments
        for pat in FILAMENT_BLACKLIST:
            if re.search(pat, all_text):
                print(f"Skipping filament in resin DB: {product['name']}")
                return False
        
        # Check Hardware/Printers
        for pat in HARDWARE_BLACKLIST:
            if re.search(pat, all_text):
                print(f"Skipping hardware in resin DB: {product['name']}")
                return False

        # Check Non-Product/Spam
        for pat in NON_PRODUCT_BLACKLIST:
            if re.search(pat, all_text):
                print(f"Skipping spam/service in resin DB: {product['name']}")
                return False
        
        # ABS check (Manual to handle ABS-Like)
        if re.search(r'\babs\b', name_lower) and 'like' not in name_lower:
             return False

    elif category == "filament":
        # Check Resins (Name only)
        for pat in RESIN_BLACKLIST:
             if re.search(pat, name_lower):
                print(f"Skipping resin in filament DB: {product['name']} (Matched: {pat})")
                return False

        # Check Hardware/Printers (Name only)
        for pat in HARDWARE_BLACKLIST:
            if re.search(pat, name_lower):
                print(f"Skipping hardware in filament DB: {product['name']} (Matched: {pat})")
                return False

        # Check Non-Product/Spam (Name + Tags)
        for pat in NON_PRODUCT_BLACKLIST:
            if re.search(pat, all_text):
                print(f"Skipping spam/service in filament DB: {product['name']} (Matched: {pat})")
                return False

    return True

# ============= BRAND CONFIGURATIONS =============

RESIN_BRANDS = [
    # Top Tier (Shopify) - Auto
    {
        "brand": "Anycubic",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "last_verified": "2025-12-27",
        "url": "https://store.anycubic.com/collections/uv-resin"
    },
    {
        "brand": "ELEGOO",
        "strategy": "shopify", 
        "scraping_mode": "auto",
        "last_verified": "2025-12-27",
        "url": "https://www.elegoo.com/collections/resin"
    },
    {
        "brand": "Siraya Tech",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "last_verified": "2025-12-27",
        "url": "https://siraya.tech/collections/all"
    },
    # JS / Playwright (Semi-Auto)
    {
        "brand": "Phrozen",
        "strategy": "js",
        "scraping_mode": "js",
        "last_verified": "2025-12-27",
        "url": "https://phrozen3d.com/collections/resins",
        "card_selector": ".product-item"
    },
    # Sunlu switched to Manual due to spam/junk in JS scrape
    {
        "brand": "Sunlu",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["Standard Resin", "ABS-Like Resin", "Water Washable Resin", "Plant Based Resin", "High Toughness Resin", "Standard-Plus Resin"],
        "default_image": "https://placehold.co/600x600/1a1a1a/cccccc?text=SUNLU"
    },
    {
        "brand": "Creality",
        "strategy": "js",
        "scraping_mode": "js_intercept",
        "last_verified": "2025-12-27",
        "url": "https://store.creality.com/eu",
        "card_selector": ".product-card", 
        "filter": "resin" 
    },
    # Manual Curated (Industrial Fallback for Unstable Sites)
    {
        "brand": "Monocure 3D",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "last_verified": "2025-12-27",
        "products": ["RAPID Resin", "TENACIOUS Resin", "Standard Resin", "Gunmetal Grey Resin"]
    },
    {
        "brand": "eSUN",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "last_verified": "2025-12-27",
        "products": ["General Purpose Resin", "Water Washable Resin", "ABS-Like Resin", "Plant-based Resin", "Standard Resin"]
    },
    {
        "brand": "AmeraLabs",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "last_verified": "2025-12-27",
        "products": ["AMD-3 LED", "TGM-7 LED", "XV Light", "DMD-31 Dental Model", "DMD-21 Dental Model"]
    }
]

FILAMENT_BRANDS = [
    # Top Tier (Shopify) - Auto
    {
        "brand": "Polymaker",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://us.polymaker.com/collections/all"
    },
    {
        "brand": "Hatchbox",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://www.hatchbox3d.com/collections/all"
    },
    {
        "brand": "Overture",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://overture3d.com/collections/filaments"
    },
    {
        "brand": "Eryone",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://eryone3d.com/collections/filament"
    },
    {
        "brand": "Anycubic",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://store.anycubic.com/collections/filament"
    },
    {
        "brand": "ELEGOO",
        "strategy": "shopify",
        "scraping_mode": "auto",
        "url": "https://www.elegoo.com/collections/pla-filament"
    },
    # JS / Difficult (Working)
    {
        "brand": "Creality",
        "strategy": "js",
        "scraping_mode": "js_intercept",
        "url": "https://store.creality.com/eu",
        "filter": "filament"
    },
    # Manual Curated (Industrial Fallback for Unstable Sites)
    {
        "brand": "Prusament",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["Prusament PLA", "Prusament PETG", "Prusament ASA", "Prusament PC Blend", "Prusament PVB"],
        "default_image": "https://placehold.co/600x600/fa6831/ffffff?text=Prusament"
    },
    {
        "brand": "Bambu Lab",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["Bambu PLA Basic", "Bambu PLA Matte", "Bambu PETG Basic", "Bambu ABS", "Bambu PAHT-CF"],
        "default_image": "https://placehold.co/600x600/00AE42/ffffff?text=Bambu+Lab"
    },
    {
        "brand": "Fillamentum",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["PLA Extrafill", "CPE HG100", "Flexfill 98A", "Nylon FX256", "Timberfill"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=Fillamentum"
    },
    {
        "brand": "ColorFabb",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["PLA/PHA", "nGen", "XT-CF20", "woodFill", "bronzeFill"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=ColorFabb"
    },
    {
        "brand": "NinjaTek",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["NinjaFlex", "Cheetah", "Armadillo", "Chinchilla"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=NinjaTek"
    },
    {
        "brand": "Fiberlogy",
        "strategy": "manual", 
        "scraping_mode": "manual_curated",
        "products": ["Easy PLA", "Fiberlogy REFILL", "FiberSatin", "FiberSilk", "FiberWood"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=Fiberlogy"
    },
    # Manual Fallback for eSUN & Sunlu
    {
        "brand": "eSUN",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["PLA+ Filament", "PETG Filament", "ABS+ Filament", "eSilk-PLA", "ePA-CF"],
        "default_image": "https://placehold.co/600x600/2665b5/ffffff?text=eSUN"
    },
    {
        "brand": "Sunlu",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["Sunlu PLA", "Sunlu PETG", "Sunlu ABS", "Sunlu PLA+", "Sunlu TPU"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=Sunlu"
    }
]


def scrape_brand(config: Dict, category: str = "filament") -> List[Dict]:
    """Scrape a single brand using its configured strategy"""
    brand = config.get("brand", "Unknown")
    strategy = config.get("strategy", "shopify")
    
    # Check for manual strategy first
    if strategy == "manual":
        return scrape_manual(config)
        
    urls = config.get("url", "")
    if isinstance(urls, str):
        urls = [urls]
        
    all_products = []
    
    for url in urls:
        # Create temp config for single URL
        single_config = config.copy()
        single_config["url"] = url
        
        products = _scrape_single_url(single_config, category)
        all_products.extend(products)
        
    return all_products

def _scrape_single_url(config: Dict, category: str) -> List[Dict]:
    strategy = config.get("strategy", "shopify")
    brand = config.get("brand", "Unknown")
    url = config.get("url", "")
    keyword_filter = config.get("filter")
    
    products = []
    try:
        if strategy == "shopify":
            products = scrape_shopify(url, brand, category)
        
        elif strategy == "html":
            selectors = config.get("selectors", {})
            products = scrape_html(
                url=url,
                brand=brand,
                card_selector=selectors.get("card", ".product-card"),
                name_selector=selectors.get("name", ".product-title"),
                img_selector=selectors.get("img", "img"),
                price_selector=selectors.get("price", ".price")
            )
        
        elif strategy == "json":
            products = scrape_json(
                url=url,
                brand=brand,
                data_path=config.get("data_path", []),
                name_key=config.get("name_key", "name"),
                image_key=config.get("image_key", "image")
            )
        
        elif strategy == "woocommerce":
            products = scrape_woocommerce(
                url, 
                brand,
                title_selector=config.get("title_selector", ".woocommerce-loop-product__title")
            )
            
        elif strategy == "js":
            if scrape_js:
                products = scrape_js(
                    url=url,
                    brand=brand,
                    card_selector=config.get("card_selector", "article, div.product, .product-card")
                )
            else:
                print(f"  [Skipping] {brand} requires Playwright (not installed/imported)")
                return []
        
        else:
            print(f"  Unknown strategy: {strategy}")
            return []
            
        # Apply Keyword Filter if configured
        if keyword_filter and products:
            original_len = len(products)
            products = [
                p for p in products 
                if keyword_filter.lower() in p.get("name", "").lower() 
                or keyword_filter.lower() in p.get("url", "").lower()
            ]
            if len(products) < original_len:
                print(f"    (Filtered {original_len} -> {len(products)} using '{keyword_filter}')")

        return products
            
    except Exception as e:
        print(f"  Error: {e}")
        return []


def enrich_product(product: Dict, category: str) -> Dict:
    """Add missing fields with defaults"""
    # Import specific detection logic if needed, or keep simple
    from strategies.shopify import detect_product_type, detect_color
    
    name = product.get("name", "")
    if isinstance(name, dict): # Handle WP rendered title object
        name = name.get("rendered", str(name))
        product["name"] = name

    # Detect type if missing
    if not product.get("type"):
        product["type"] = detect_product_type(name)
    
    # Detect color if missing
    if not product.get("color"):
        color_hex, color_name = detect_color(name)
        product["color"] = color_hex
        product["color_name"] = color_name
    
    # Add tags if missing
    if not product.get("tags"):
        product["tags"] = [product.get("type", "Standard")]
    
    return product


def get_sla_profiles(brand: str, resin_type: str) -> Dict:
    """Returns a set of common printer profiles for a given resin brand/type"""
    base = {
        "Default": {
            "layerHeight": 0.05, "bottomLayerCount": 5, "exposureTime": 2.5,
            "bottomExposure": 30, "liftDistance1": 5, "liftSpeed1": 60, "retractSpeed1": 150
        }
    }
    
    # Add common printer variations
    printers = [
        ("Anycubic Photon Mono X", 2.0, 25),
        ("Anycubic Photon M3 Plus", 1.8, 20),
        ("Elegoo Mars 3", 2.5, 30),
        ("Elegoo Saturn 2", 2.2, 25),
        ("Phrozen Sonic Mighty 8K", 2.1, 25),
        ("Creality Halot Mage", 2.3, 28)
    ]
    
    for name, exp, b_exp in printers:
        base[name] = {
            "layerHeight": 0.05,
            "bottomLayerCount": 6,
            "exposureTime": exp,
            "bottomExposure": b_exp,
            "liftDistance1": 6,
            "liftSpeed1": 65,
            "retractSpeed1": 180
        }
    
    return base

def get_fdm_profiles(brand: str, material: str) -> Dict:
    """Returns a set of common FDM profiles"""
    temp = 210 if material.upper() in ["PLA", "PLA+"] else (240 if material.upper() == "PETG" else 250)
    bed = 60 if material.upper() in ["PLA", "PLA+"] else (80 if material.upper() == "PETG" else 100)
    
    return {
        "Default": {"printTemp": temp, "bedTemp": bed, "fanSpeed": 100, "retractionDistance": 1.0, "retractionSpeed": 40},
        "Fast / Draft (0.28mm)": {"printTemp": temp + 5, "bedTemp": bed, "fanSpeed": 100, "retractionDistance": 1.2, "retractionSpeed": 45},
        "Fine Detail (0.12mm)": {"printTemp": temp - 5, "bedTemp": bed, "fanSpeed": 100, "retractionDistance": 0.8, "retractionSpeed": 35},
        "Bambu Lab X1C / P1S": {"printTemp": temp + 10, "bedTemp": bed, "fanSpeed": 100, "retractionDistance": 0.8, "retractionSpeed": 50}
    }

def convert_to_frontend_schema(products: List[Dict], category: str, output_root: str = ".") -> List[Dict]:
    """Convert scraped data to frontend schema format and download images"""
    result = []
    
    for p in products:
        brand = p.get("brand", "Generic")
        name = p.get("name", "Unknown")
        image_url = p.get("image")
        
        # Download image if URL is present
        local_image_path = None
        if image_url:
            local_image_path = download_image(image_url, category, brand, name, output_root)
            # Normalizar separadores de ruta para JSON (usar barra inclinada)
            if local_image_path:
                local_image_path = local_image_path.replace("\\", "/")

        if category == "resin":
            resin_type = p.get("type", "Standard")
            result.append({
                "brand": brand,
                "name": name,
                "image": local_image_path or image_url,
                "type": resin_type,
                "description": p.get("description"),
                "color": p.get("color", "#808080"),
                "colorName": p.get("color_name", "Grey"),
                "tags": p.get("tags", ["Standard"]),
                "profiles": get_sla_profiles(brand, resin_type)
            })
        else:  # filament
            material = p.get("type", "PLA")
            result.append({
                "brand": brand,
                "name": name,
                "material": material,
                "image": local_image_path or image_url,
                "description": p.get("description"),
                "color": p.get("color", "#808080"),
                "colorName": p.get("color_name", "Grey"),
                "tags": p.get("tags", [material]),
                "profiles": get_fdm_profiles(brand, material)
            })
    
    return result


def merge_with_existing(new_data: List[Dict], filepath: str) -> List[Dict]:
    """Merge new data with existing, avoiding duplicates"""
    if not os.path.exists(filepath):
        return new_data
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # Create set of existing (brand, name) pairs
        # Merge new data into existing
        added = 0
        updated = 0
        for item in new_data:
            key = (item.get("brand", "").lower(), item.get("name", "").lower())
            
            # Find existing item to update or append new
            found = False
            for existing_item in existing:
                if (existing_item.get("brand", "").lower(), existing_item.get("name", "").lower()) == key:
                    # Update fields that might have changed or been enriched
                    existing_item.update({
                        "profiles": item.get("profiles", existing_item.get("profiles")),
                        "params": item.get("params", existing_item.get("params")),
                        "image": item.get("image") or existing_item.get("image"),
                        "description": item.get("description") or existing_item.get("description"),
                        "tags": item.get("tags") or existing_item.get("tags")
                    })
                    updated += 1
                    found = True
                    break
            
            if not found:
                existing.append(item)
                added += 1
        
        # RE-VALIDATE EVERYTHING: This removes items that are now blacklisted
        category = "resin" if "resin" in filepath else "filament"
        final_list = [item for item in existing if validate_product(item, category)]
        
        removed = len(existing) - len(final_list)
        if removed > 0:
            print(f"  Cleanup: {removed} blacklisted items removed from database")
            
        print(f"  Merged: {added} new, {updated} updated. Total: {len(final_list)}")
        return final_list
        
    except Exception as e:
        print(f"  Could not merge: {e}")
        return new_data


def main():
    parser = argparse.ArgumentParser(description="Scrape material databases")
    parser.add_argument("--resins", action="store_true", help="Scrape resins only")
    parser.add_argument("--filaments", action="store_true", help="Scrape filaments only")
    parser.add_argument("--dry-run", action="store_true", help="Don't save, just preview")
    parser.add_argument("--no-merge", action="store_true", help="Replace instead of merge")
    args = parser.parse_args()
    
    do_resins = args.resins or (not args.resins and not args.filaments)
    do_filaments = args.filaments or (not args.resins and not args.filaments)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.abspath(__file__)) # For the new repo, this will be the root
    
    print("=" * 60)
    print("Material Database Scraper v2.7 (Auto-Archive Edition)")
    print("=" * 60)
    
    if scrape_js:
        print("✅ Playwright module loaded successfully")
    else:
        print("⚠️  Playwright module NOT found (JS sites will be skipped)")
    
    # Scrape Resins
    if do_resins:
        print(f"\nScraping {len(RESIN_BRANDS)} resin brands...")
        all_resins = []
        
        for config in RESIN_BRANDS:
            print(f"  {config['brand']} ({config['strategy']})...", end=" ", flush=True)
            products = scrape_brand(config, "resin")
            
            # Filter filaments from resin list
            products = [p for p in products if validate_product(p, "resin")]
            
            products = [enrich_product(p, "resin") for p in products]
            print(f"Found {len(products)}")
            all_resins.extend(products)
        
        print(f"Total resins: {len(all_resins)}")
        
        # Convert and save
        frontend_resins = convert_to_frontend_schema(all_resins, "resin", repo_root)
        
        if not args.dry_run:
            filepath = os.path.join(output_dir, "resins_db.json")
            if not args.no_merge:
                frontend_resins = merge_with_existing(frontend_resins, filepath)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(frontend_resins, f, indent=4, ensure_ascii=False)
            print(f"Saved to {filepath}")
        else:
            print("(dry-run, not saving)")
            for r in frontend_resins[:5]:
                print(f"  - {r['brand']}: {r['name']}")
    
    # Scrape Filaments
    if do_filaments:
        print(f"\nScraping {len(FILAMENT_BRANDS)} filament brands...")
        all_filaments = []
        
        for config in FILAMENT_BRANDS:
            print(f"  {config['brand']} ({config['strategy']})...", end=" ", flush=True)
            products = scrape_brand(config, "filament")
            
            # Filtro para eliminar resinas, packs y hardware de la lista de filamentos
            products = [p for p in products if validate_product(p, "filament")]
            
            products = [enrich_product(p, "filament") for p in products]
            print(f"Found {len(products)}")
            all_filaments.extend(products)
        
        print(f"Total filaments: {len(all_filaments)}")
        
        # Convert and save
        frontend_filaments = convert_to_frontend_schema(all_filaments, "filament", repo_root)
        
        if not args.dry_run:
            filepath = os.path.join(output_dir, "filaments_db.json")
            if not args.no_merge:
                frontend_filaments = merge_with_existing(frontend_filaments, filepath)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(frontend_filaments, f, indent=4, ensure_ascii=False)
            print(f"Saved to {filepath}")
        else:
            print("(dry-run, not saving)")
            for f in frontend_filaments[:5]:
                print(f"  - {f['brand']}: {f['name']}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
