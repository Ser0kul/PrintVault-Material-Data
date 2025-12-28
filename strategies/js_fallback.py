"""
JavaScript Fallback Strategy using Playwright
For sites heavily dependent on JavaScript rendering
NOTE: Requires playwright to be installed separately
"""

from typing import List, Dict, Any

# Check if playwright is available
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def scrape_js(
    url: str,
    brand: str = "Unknown",
    card_selector: str = "article, div.product, .product-card",
    wait_time: int = 3000
) -> List[Dict[str, Any]]:
    """
    Scrape products from JavaScript-heavy sites using Playwright
    
    Args:
        url: Page URL
        brand: Brand name
        card_selector: CSS selector for product cards
        wait_time: Time to wait for JS to render (ms)
    
    Returns:
        List of product dictionaries
    """
    if not HAS_PLAYWRIGHT:
        print("    [JS] Playwright not installed. Run: pip install playwright && playwright install")
        return []
    
    results = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                java_script_enabled=True
            )
            page = context.new_page()
            
            # Navigate with timeout
            # Use domcontentloaded as networkidle is too strict for many e-commerce sites
            # Special handling for Creality (Network Interception)
            creality_products = []
            if brand.lower() == "creality":
                def handle_response(response):
                    if "product" in response.url and response.status == 200:
                        try:
                            data = response.json()
                            items = data.get("data", [])
                            # Handle pagination or simple list
                            if isinstance(items, dict) and "rows" in items:
                                items = items["rows"]
                            
                            for p in items:
                                creality_products.append({
                                    "brand": "Creality",
                                    "name": p.get("name"),
                                    "image": p.get("image") or p.get("img"),
                                    "url": f"https://store.creality.com/eu/products/{p.get('slug', '')}",
                                    "fuente_datos": "playwright_intercept"
                                })
                        except:
                            pass
                page.on("response", handle_response)

            # Navigate with timeout
            try:
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"    [JS] Navigation timeout/error: {e}")

            # Human-like interaction (Bambu Lab / Sunlu)
            try:
                page.wait_for_timeout(2000)
                page.mouse.move(300, 400)
                page.wait_for_timeout(1000)
                page.mouse.wheel(0, 500) # Small initial scroll
                page.wait_for_timeout(1000)
            except:
                pass

            # Scroll down to trigger lazy loading (Aggressive)
            for _ in range(5):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1500)
            
            page.wait_for_timeout(wait_time)
            
            # Return intercept results immediately if present
            if creality_products:
                return creality_products

            # Find product cards - Try provided selector first, then fallbacks
            cards = page.query_selector_all(card_selector)
            
            if not cards:
                # Try common fallbacks if primary failed
                fallbacks = ["div.product-item", "li.grid__item", "div.product-card", "article", ".product", ".grid-product"]
                for fb in fallbacks:
                    cards = page.query_selector_all(fb)
                    if cards:
                        break
            
            for card in cards:
                try:
                    # Get text content
                    text = card.inner_text()
                    
                    # Try to find title element
                    title_search = ["h2", "h3", "h4", ".title", ".name", ".product-title", ".product-item-link", ".grid-product__title", ".product-grid-item__title", ".card-title"]
                    title_el = None
                    for ts in title_search:
                         title_el = card.query_selector(ts)
                         if title_el: break
                    
                    name = title_el.inner_text() if title_el else text.split('\n')[0]
                    
                    # Try to find image
                    img_el = card.query_selector("img")
                    image = None
                    if img_el:
                        image = img_el.get_attribute("src") or img_el.get_attribute("data-src") or img_el.get_attribute("srcset")
                    
                    # Try to find link
                    link_el = card.query_selector("a")
                    product_url = None
                    if link_el:
                        product_url = link_el.get_attribute("href")
                        if product_url and not product_url.startswith("http"):
                           # simple reconstruction
                           import urllib.parse
                           base_parts = urllib.parse.urlparse(url)
                           product_url = f"{base_parts.scheme}://{base_parts.netloc}{product_url}"
                    
                    if name and len(name) > 2:
                        results.append({
                            "brand": brand,
                            "name": name.strip()[:100],
                            "image": image,
                            "url": product_url,
                            "fuente_datos": "playwright_js"
                        })
                except Exception:
                    continue
            
            browser.close()
        
        return results
        
    except Exception as e:
        print(f"    [JS] Error: {e}")
        return []
