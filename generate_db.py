#!/usr/bin/env python3
"""
Material Database Generator
Main script to scrape and generate material databases

Usage:
    python generate_db.py [--resins] [--filaments] [--simple] [--dry-run]

Options:
    --resins      Only generate resins database
    --filaments   Only generate filaments database
    --simple      Export to simple schema (current frontend format)
    --dry-run     Don't write files, just print results
"""

import json
import argparse
import os
import sys
from typing import List, Dict

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RESIN_BRANDS, FILAMENT_BRANDS, RESINS_OUTPUT, FILAMENTS_OUTPUT
from scrapers.generic import GenericScraper
from builder import build_resins, build_filaments, export_simple_schema, export_rich_schema


def scrape_resins(brands: List[Dict] = None) -> List[Dict]:
    """Scrape resins from configured brands"""
    brands = brands or RESIN_BRANDS
    all_products = []
    
    print(f"\n📦 Scraping {len(brands)} resin brands...")
    
    for brand_info in brands:
        try:
            scraper = GenericScraper(
                brand=brand_info["name"],
                base_url=brand_info["url"],
                product_type="resin"
            )
            products = scraper.scrape_products()
            all_products.extend(products)
        except Exception as e:
            print(f"❌ Error scraping {brand_info['name']}: {e}")
    
    print(f"✅ Total resins scraped: {len(all_products)}")
    return all_products


def scrape_filaments(brands: List[Dict] = None) -> List[Dict]:
    """Scrape filaments from configured brands"""
    brands = brands or FILAMENT_BRANDS
    all_products = []
    
    print(f"\n🧵 Scraping {len(brands)} filament brands...")
    
    for brand_info in brands:
        try:
            scraper = GenericScraper(
                brand=brand_info["name"],
                base_url=brand_info["url"],
                product_type="filament"
            )
            products = scraper.scrape_products()
            all_products.extend(products)
        except Exception as e:
            print(f"❌ Error scraping {brand_info['name']}: {e}")
    
    print(f"✅ Total filaments scraped: {len(all_products)}")
    return all_products


def merge_with_existing(new_data: List[Dict], existing_path: str, key: str = "name") -> List[Dict]:
    """Merge new data with existing database, avoiding duplicates"""
    if os.path.exists(existing_path):
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            
            # Create set of existing names
            existing_names = {item.get(key, "").lower() for item in existing}
            
            # Add new items not already in existing
            for item in new_data:
                if item.get(key, "").lower() not in existing_names:
                    existing.append(item)
            
            print(f"  📝 Merged: {len(new_data)} new + {len(existing) - len(new_data)} existing = {len(existing)} total")
            return existing
        except Exception as e:
            print(f"  ⚠️ Could not merge with existing: {e}")
    
    return new_data


def save_json(data: List[Dict], path: str):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate material databases")
    parser.add_argument("--resins", action="store_true", help="Only generate resins")
    parser.add_argument("--filaments", action="store_true", help="Only generate filaments")
    parser.add_argument("--simple", action="store_true", help="Export simple schema")
    parser.add_argument("--dry-run", action="store_true", help="Don't save files")
    parser.add_argument("--merge", action="store_true", help="Merge with existing DB")
    args = parser.parse_args()
    
    # If neither specified, do both
    do_resins = args.resins or (not args.resins and not args.filaments)
    do_filaments = args.filaments or (not args.resins and not args.filaments)
    
    print("=" * 60)
    print("🔧 Material Database Generator")
    print("=" * 60)
    
    # Scrape
    if do_resins:
        raw_resins = scrape_resins()
        resins = build_resins(raw_resins)
        
        if args.simple:
            from schema import resina_to_simple_schema
            resin_data = [resina_to_simple_schema(r) for r in resins]
        else:
            resin_data = [r.model_dump() for r in resins]
        
        if args.merge:
            output_path = os.path.join(os.path.dirname(__file__), RESINS_OUTPUT)
            resin_data = merge_with_existing(resin_data, output_path, "name")
        
        if not args.dry_run:
            output_path = os.path.join(os.path.dirname(__file__), RESINS_OUTPUT)
            save_json(resin_data, output_path)
        else:
            print(f"\n📋 Would save {len(resin_data)} resins")
            for r in resin_data[:5]:
                print(f"  - {r.get('marca', r.get('brand'))}: {r.get('nombre', r.get('name'))}")
    
    if do_filaments:
        raw_filaments = scrape_filaments()
        filaments = build_filaments(raw_filaments)
        
        if args.simple:
            from schema import filamento_to_simple_schema
            filament_data = [filamento_to_simple_schema(f) for f in filaments]
        else:
            filament_data = [f.model_dump() for f in filaments]
        
        if args.merge:
            output_path = os.path.join(os.path.dirname(__file__), FILAMENTS_OUTPUT)
            filament_data = merge_with_existing(filament_data, output_path, "name")
        
        if not args.dry_run:
            output_path = os.path.join(os.path.dirname(__file__), FILAMENTS_OUTPUT)
            save_json(filament_data, output_path)
        else:
            print(f"\n📋 Would save {len(filament_data)} filaments")
            for f in filament_data[:5]:
                print(f"  - {f.get('marca', f.get('brand'))}: {f.get('nombre', f.get('name'))}")
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
