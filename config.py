"""
Configuration for material scraper
"""

# Request settings
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 1.0  # Seconds between requests (be respectful)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Headers for requests
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Output paths (relative to project root)
OUTPUT_DIR = "../../src/data"
RESINS_OUTPUT = f"{OUTPUT_DIR}/resins_db.json"
FILAMENTS_OUTPUT = f"{OUTPUT_DIR}/filaments_db.json"

# Resin brands to scrape
RESIN_BRANDS = [
    # Premium/Industrial
    {"name": "Formlabs", "url": "https://formlabs.com/materials/", "type": "premium"},
    {"name": "Henkel Loctite", "url": "https://www.loctiteam.com/3d-printing-resins/", "type": "industrial"},
    {"name": "BASF Forward AM", "url": "https://forward-am.com/material-portfolio/", "type": "industrial"},
    
    # Consumer Popular
    {"name": "Anycubic", "url": "https://www.anycubic.com/collections/uv-resin", "type": "consumer"},
    {"name": "ELEGOO", "url": "https://www.elegoo.com/collections/resin", "type": "consumer"},
    {"name": "Siraya Tech", "url": "https://siraya.tech/collections/resins", "type": "consumer"},
    {"name": "Phrozen", "url": "https://phrozen3d.com/collections/resins", "type": "consumer"},
    {"name": "Sunlu", "url": "https://www.sunlu.com/collections/resin", "type": "consumer"},
    {"name": "eSUN", "url": "https://www.esun3d.com/eresins-product/", "type": "consumer"},
    {"name": "Creality", "url": "https://www.creality.com/products/resin", "type": "consumer"},
    
    # Specialty
    {"name": "BlueCast", "url": "https://www.bluecast.info/products/", "type": "specialty"},
    {"name": "AmeraLabs", "url": "https://ameralabs.com/shop/", "type": "specialty"},
    {"name": "Monocure 3D", "url": "https://monocure3d.com.au/product-category/resin/", "type": "specialty"},
    {"name": "SprintRay", "url": "https://sprintray.com/materials/", "type": "dental"},
    {"name": "NextDent", "url": "https://nextdent.com/products/", "type": "dental"},
]

# Filament brands to scrape
FILAMENT_BRANDS = [
    # Premium
    {"name": "Prusament", "url": "https://www.prusa3d.com/category/prusament/", "type": "premium"},
    {"name": "Polymaker", "url": "https://polymaker.com/products/", "type": "premium"},
    {"name": "Bambu Lab", "url": "https://bambulab.com/en/filament", "type": "premium"},
    {"name": "ColorFabb", "url": "https://colorfabb.com/filaments", "type": "premium"},
    {"name": "Fillamentum", "url": "https://fillamentum.com/collections/all", "type": "premium"},
    
    # Consumer Popular
    {"name": "eSUN", "url": "https://www.esun3d.com/pla-pro-product/", "type": "consumer"},
    {"name": "Sunlu", "url": "https://www.sunlu.com/collections/filaments", "type": "consumer"},
    {"name": "Hatchbox", "url": "https://www.hatchbox3d.com/collections/all", "type": "consumer"},
    {"name": "Overture", "url": "https://overture3d.com/collections/filaments", "type": "consumer"},
    {"name": "ELEGOO", "url": "https://www.elegoo.com/collections/pla-filament", "type": "consumer"},
    {"name": "Creality", "url": "https://www.creality.com/products/filament", "type": "consumer"},
    {"name": "Eryone", "url": "https://eryone3d.com/collections/filament", "type": "consumer"},
    {"name": "Inland", "url": "https://www.microcenter.com/category/4294866996/inland-filament", "type": "consumer"},
    {"name": "Anycubic", "url": "https://www.anycubic.com/collections/filament", "type": "consumer"},
    
    # Engineering/Specialty
    {"name": "MatterHackers", "url": "https://www.matterhackers.com/store/c/3d-printer-filament", "type": "specialty"},
    {"name": "NinjaTek", "url": "https://ninjatek.com/shop/", "type": "specialty"},
    {"name": "Proto-pasta", "url": "https://www.proto-pasta.com/", "type": "specialty"},
    {"name": "Fiberlogy", "url": "https://fiberlogy.com/en/filaments/", "type": "specialty"},
]

# Material types
RESIN_TYPES = [
    "Standard", "Tough", "ABS-Like", "Flexible", "Elastic", 
    "Water Washable", "Plant Based", "Castable", "Dental",
    "High Temp", "Ceramic", "Transparent", "Glow in Dark"
]

FILAMENT_MATERIALS = [
    "PLA", "PLA+", "PETG", "ABS", "ASA", "TPU", "TPE",
    "Nylon", "PC", "HIPS", "PVA", "Wood", "Carbon Fiber",
    "Silk", "Matte", "Marble", "Metal Fill", "Glow"
]
