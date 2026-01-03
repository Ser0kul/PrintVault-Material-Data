"""
Text Cleaning Utilities
Functions for converting HTML to clean text and normalizing descriptions
"""

from bs4 import BeautifulSoup
import re
from typing import Optional


def clean_html_to_text(html: str, max_length: int = 500) -> Optional[str]:
    """
    Convert HTML to clean text, removing tags and extra whitespace.
    
    Args:
        html: Raw HTML string
        max_length: Maximum characters to return (default 500)
    
    Returns:
        Clean text string or None if empty
    """
    if not html:
        return None
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text with spaces between elements
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove multiple spaces and normalize whitespace
        text = ' '.join(text.split())
        
        # Remove common boilerplate phrases
        boilerplate = [
            r'javascript.*?;',
            r'click here',
            r'read more',
            r'ver más',
            r'leer más',
        ]
        for pattern in boilerplate:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up result
        text = text.strip()
        
        if not text or len(text) < 10:
            return None
        
        # Truncate to max length, trying to end at a sentence or period
        if len(text) > max_length:
            truncated = text[:max_length]
            # Try to end at a period
            last_period = truncated.rfind('.')
            if last_period > max_length // 2:
                truncated = truncated[:last_period + 1]
            else:
                truncated = truncated.rsplit(' ', 1)[0] + '...'
            text = truncated
        
        return text
        
    except Exception as e:
        print(f"    [TextCleaner] Error cleaning HTML: {e}")
        return None


def extract_meta_description(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract meta description from a BeautifulSoup parsed page.
    
    Args:
        soup: Parsed BeautifulSoup object
    
    Returns:
        Meta description text or None
    """
    # Try various meta description patterns
    selectors = [
        ('meta[name="description"]', 'content'),
        ('meta[property="og:description"]', 'content'),
        ('meta[name="twitter:description"]', 'content'),
    ]
    
    for selector, attr in selectors:
        meta = soup.select_one(selector)
        if meta and meta.get(attr):
            description = meta.get(attr).strip()
            if len(description) > 20:
                return description
    
    return None
