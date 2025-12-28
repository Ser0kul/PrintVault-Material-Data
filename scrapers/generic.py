"""
Generic scraper that works with common e-commerce patterns
Handles: Shopify, WooCommerce, custom sites
"""

from typing import List, Dict, Any, Optional
from .base import BaseScraper
import re


class GenericScraper(BaseScraper):
    """
    Generic scraper using common CSS selectors
    Works with most e-commerce sites
    """
    
    # Common CSS selectors for product listings
    PRODUCT_SELECTORS = [
        # Shopify
        ".product-card", ".product-item", ".product-grid-item",
        # WooCommerce
        ".product", ".woocommerce-loop-product",
        # Generic
        "[data-product]", ".product-tile", ".product-box",
        ".card-product", ".material-card", ".item-card"
    ]
    
    # Common selectors for product info
    TITLE_SELECTORS = ["h1", "h2", "h3", ".product-title", ".product-name", "[data-product-title]"]
    IMAGE_SELECTORS = ["img.product-image", "img.featured-image", ".product-image img", "img[data-src]", "img"]
    PRICE_SELECTORS = [".price", ".product-price", "[data-price]", ".amount"]
    LINK_SELECTORS = ["a"]
    
    def __init__(self, brand: str, base_url: str, product_type: str = "resin"):
        super().__init__(brand, base_url)
        self.product_type = product_type
    
    def find_products_on_page(self, soup) -> List[Dict]:
        """Find product elements using common selectors"""
        products = []
        
        for selector in self.PRODUCT_SELECTORS:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    product = self.extract_product_from_element(el)
                    if product and product.get("name"):
                        products.append(product)
                break  # Use first successful selector
        
        return products
    
    def extract_product_from_element(self, el) -> Optional[Dict]:
        """Extract product info from a DOM element"""
        product = {"brand": self.brand, "fuente_datos": "web"}
        
        # Title
        for sel in self.TITLE_SELECTORS:
            title_el = el.select_one(sel)
            if title_el:
                product["name"] = self.clean_text(title_el.get_text())
                break
        
        # Image
        for sel in self.IMAGE_SELECTORS:
            img_el = el.select_one(sel)
            if img_el:
                product["image"] = img_el.get("src") or img_el.get("data-src")
                if product["image"] and product["image"].startswith("//"):
                    product["image"] = "https:" + product["image"]
                break
        
        # Link
        link_el = el.select_one("a[href]")
        if link_el:
            href = link_el.get("href", "")
            if href.startswith("/"):
                # Relative URL
                base = self.base_url.rstrip("/")
                product["url"] = f"{base}{href}"
            elif href.startswith("http"):
                product["url"] = href
        
        # Price
        for sel in self.PRICE_SELECTORS:
            price_el = el.select_one(sel)
            if price_el:
                product["price"] = self.extract_price(price_el.get_text())
                break
        
        return product
    
    def detect_type_from_name(self, name: str) -> str:
        """Guess product type from name"""
        name_lower = name.lower()
        
        if self.product_type == "resin":
            type_keywords = {
                "tough": "Tough",
                "abs-like": "ABS-Like",
                "abs like": "ABS-Like",
                "flexible": "Flexible",
                "elastic": "Elastic",
                "water wash": "Water Washable",
                "plant": "Plant Based",
                "castable": "Castable",
                "dental": "Dental",
                "high temp": "High Temp",
                "ceramic": "Ceramic",
                "clear": "Transparent",
                "transparent": "Transparent",
                "glow": "Glow in Dark",
            }
        else:  # filament
            type_keywords = {
                "pla+": "PLA+",
                "pla plus": "PLA+",
                "petg": "PETG",
                "abs": "ABS",
                "asa": "ASA",
                "tpu": "TPU",
                "tpe": "TPE",
                "nylon": "Nylon",
                "pc": "PC",
                "carbon": "Carbon Fiber",
                "silk": "Silk",
                "matte": "Matte",
                "wood": "Wood",
                "metal": "Metal Fill",
                "glow": "Glow",
            }
        
        for keyword, type_name in type_keywords.items():
            if keyword in name_lower:
                return type_name
        
        return "Standard" if self.product_type == "resin" else "PLA"
    
    def detect_color_from_name(self, name: str) -> tuple:
        """Guess color from product name"""
        name_lower = name.lower()
        
        color_map = {
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
            "beige": ("#d4a574", "Beige"),
            "skin": ("#d4a574", "Skin"),
            "navy": ("#3f4756", "Navy"),
        }
        
        for keyword, (hex_color, color_name) in color_map.items():
            if keyword in name_lower:
                return (hex_color, color_name)
        
        return ("#808080", "Grey")  # Default
    
    def scrape_products(self) -> List[Dict[str, Any]]:
        """Scrape all products from the brand's page"""
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        raw_products = self.find_products_on_page(soup)
        
        # Enrich with type/color detection
        enriched = []
        for p in raw_products:
            if not p.get("name"):
                continue
            
            p["type"] = self.detect_type_from_name(p.get("name", ""))
            color, color_name = self.detect_color_from_name(p.get("name", ""))
            p["color"] = color
            p["color_name"] = color_name
            p["tags"] = [p["type"]]
            
            enriched.append(p)
        
        print(f"[{self.brand}] Found {len(enriched)} products")
        return enriched
    
    def scrape_product_details(self, product_url: str) -> Dict[str, Any]:
        """Get more details from individual product page"""
        soup = self.get_page(product_url)
        if not soup:
            return {}
        
        details = {}
        
        # Try to find description
        desc_selectors = [".product-description", ".description", "[data-description]", ".product-details"]
        for sel in desc_selectors:
            desc_el = soup.select_one(sel)
            if desc_el:
                details["description"] = self.clean_text(desc_el.get_text())[:500]
                break
        
        # Try to find specs
        spec_text = soup.get_text()
        
        # Density
        density_match = re.search(r'densit[ya].*?([\d.]+)\s*(g/ml|g/cm)', spec_text, re.IGNORECASE)
        if density_match:
            details["density"] = float(density_match.group(1))
        
        # Viscosity
        visc_match = re.search(r'viscosit[ya].*?([\d,]+)\s*c?[Pp]', spec_text, re.IGNORECASE)
        if visc_match:
            details["viscosity"] = int(visc_match.group(1).replace(",", ""))
        
        return details
