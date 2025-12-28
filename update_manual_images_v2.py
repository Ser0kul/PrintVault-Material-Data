import json
import os

# --- EMBEDDED LOGIC TO AVOID DEPENDENCIES ---

def scrape_manual(config):
    """Manually curated strategy (Embedded)"""
    products = []
    brand = config.get("brand")
    default_image = config.get("default_image", "https://placehold.co/600x600/1a1a1a/cccccc?text=No+Image")
    
    for name in config.get("products", []):
         products.append({
             "brand": brand,
             "name": name,
             "type": "Standard",
             "image": default_image, # Using the default image
             "fuente_datos": "manual_curated"
         })
    return products

# Manual Configs copied from scraper.py
manual_configs = [
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
    },
    {
        "brand": "AmeraLabs",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["AMD-3 LED", "TGM-7 LED", "XVN-50", "DMD-31 Dental", "DMD-21 Dental"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=AmeraLabs"
    },
    {
        "brand": "Monocure 3D",
        "strategy": "manual",
        "scraping_mode": "manual_curated",
        "products": ["Rapid Resin", "Big Vat Resin", "Tenacious VS", "CMYK Set"],
        "default_image": "https://placehold.co/600x600/1a1a1a/ffffff?text=Monocure+3D"
    }
]

# --- UPDATE LOGIC ---

new_manual_products_resins = []
new_manual_products_filaments = []

print(f"Generating image-rich entries for {len(manual_configs)} manual brands...")

for config in manual_configs:
    brand = config.get("brand")
    products = scrape_manual(config)
    print(f"  - {brand}: Generated {len(products)} products with image: {config.get('default_image', 'N/A')}")
    
    if brand in ["AmeraLabs", "Monocure 3D", "Peopoly", "Siraya Tech"]:
        new_manual_products_resins.extend(products)
    else:
        new_manual_products_filaments.extend(products)

def update_db(path, new_products):
    if not os.path.exists(path):
        print(f"DB not found: {path}")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return
    
    initial_count = len(db)
    
    # Identify manual brands to replace
    updated_brands = [c.get("brand") for c in manual_configs]
    
    # Remove old manual entries
    db_clean = [p for p in db if not (p.get("fuente_datos") == "manual_curated" and p.get("brand") in updated_brands)]
    
    # Add new ones
    db_clean.extend(new_products)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(db_clean, f, indent=4)
        
    print(f"Updated {path}: {initial_count} -> {len(db_clean)} items.")

print("Updating Databases...")
# Correct paths assuming script is in tools/material-scraper
# and stored is in src/data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESIN_PATH = os.path.join(BASE_DIR, 'src', 'data', 'resins_db.json')
FILAMENT_PATH = os.path.join(BASE_DIR, 'src', 'data', 'filaments_db.json')

# Fallback to direct relative path if abspath fails logic
if not os.path.exists(RESIN_PATH):
    RESIN_PATH = '../../src/data/resins_db.json'
    FILAMENT_PATH = '../../src/data/filaments_db.json'

update_db(RESIN_PATH, new_manual_products_resins)
update_db(FILAMENT_PATH, new_manual_products_filaments)
print("Done.")
