import json
import os
from scraper import scrape_manual, BRANDS_CONFIG

# Filter only manual configs
manual_configs = [c for c in BRANDS_CONFIG if c.get("strategy") == "manual"]

# Generate new manual products
new_manual_products_resins = []
new_manual_products_filaments = []

print(f"Generating image-rich entries for {len(manual_configs)} manual brands...")

for config in manual_configs:
    brand = config.get("brand")
    products = scrape_manual(config)
    print(f"  - {brand}: Generated {len(products)} products with image: {config.get('default_image', 'N/A')}")
    
    # Heuristic to split into Resin/Filament (most manual are filaments in this config, assuming checked lists)
    # Actually, the config list has mixed? No, looking at scraper.py, scrape_brand takes a category
    # But scrape_manual ignores category and just returns products.
    # We need to know where they go.
    # Looking at BRANDS_CONFIG in scraper.py:
    # Most are filaments (Prusament, Bambu, etc).
    # AmeraLabs and Monocure are Resins.
    
    # Hardcoded classification based on brand knowledge
    if brand in ["AmeraLabs", "Monocure 3D", "Peopoly", "Siraya Tech"]: # Siraya is shopify but if it was manual...
        new_manual_products_resins.extend(products)
    else:
        new_manual_products_filaments.extend(products)

def update_db(path, new_products):
    if not os.path.exists(path):
        print(f"DB not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    initial_count = len(db)
    
    # Remove old manual entries for these specific brands to avoid duplicates
    # We identify them by "fuente_datos": "manual_curated" AND brand in our list
    updated_brands = [c.get("brand") for c in manual_configs]
    
    db_clean = [p for p in db if not (p.get("fuente_datos") == "manual_curated" and p.get("brand") in updated_brands)]
    
    # Add new ones
    db_clean.extend(new_products)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(db_clean, f, indent=4)
        
    print(f"Updated {path}: {initial_count} -> {len(db_clean)} items.")

print("Updating Databases...")
update_db('src/data/resins_db.json', new_manual_products_resins)
update_db('src/data/filaments_db.json', new_manual_products_filaments)
print("Done.")
