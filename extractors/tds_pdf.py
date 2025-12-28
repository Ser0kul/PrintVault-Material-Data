"""
TDS (Technical Data Sheet) PDF Extractor
Extracts physical and mechanical properties from manufacturer datasheets
"""

import re
from typing import Dict, Any, Optional

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("Warning: pdfplumber not installed. PDF extraction disabled.")


class TDSExtractor:
    """Extract data from Technical Data Sheet PDFs"""
    
    # Regex patterns for common properties
    PATTERNS = {
        # Density
        "density": [
            r"densit[ya].*?([\d.]+)\s*(g/ml|g/cm³|g/cm3)",
            r"specific\s+gravity.*?([\d.]+)",
        ],
        # Viscosity
        "viscosity": [
            r"viscosit[ya].*?([\d,]+)\s*(cps|mpa|cp)",
        ],
        # Shore Hardness
        "hardness": [
            r"hardness.*?(\d+)\s*([AD])",
            r"shore\s*([AD]).*?(\d+)",
        ],
        # Tensile Strength
        "tensile_strength": [
            r"tensile\s+strength.*?([\d.]+)\s*(mpa|psi)",
            r"resistencia.*?tracción.*?([\d.]+)\s*(mpa)?",
        ],
        # Elongation
        "elongation": [
            r"elongation.*?([\d.]+)\s*%",
            r"alargamiento.*?([\d.]+)\s*%",
        ],
        # Flexural Modulus
        "flexural_modulus": [
            r"flexural\s+modulus.*?([\d.]+)\s*(mpa|gpa)",
            r"módulo\s+flexión.*?([\d.]+)",
        ],
        # HDT (Heat Deflection Temperature)
        "hdt": [
            r"hdt.*?([\d.]+)\s*°?c",
            r"heat\s+deflection.*?([\d.]+)",
            r"deflexión.*?calor.*?([\d.]+)",
        ],
        # Glass Transition
        "tg": [
            r"t[g].*?([\d.]+)\s*°?c",
            r"glass\s+transition.*?([\d.]+)",
        ],
        # Shrinkage
        "shrinkage": [
            r"shrinkage.*?([\d.]+)\s*%",
            r"contracción.*?([\d.]+)",
        ],
        # Wavelength
        "wavelength": [
            r"(\d{3})\s*nm",
            r"wavelength.*?(\d{3})",
        ],
    }
    
    def __init__(self):
        if not HAS_PDFPLUMBER:
            print("TDSExtractor: pdfplumber not available")
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all available properties from a PDF"""
        if not HAS_PDFPLUMBER:
            return {}
        
        try:
            text = self._extract_text(pdf_path)
            return self._parse_text(text)
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return {}
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text for properties"""
        results = {}
        text_lower = text.lower()
        
        for prop_name, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).replace(",", "")
                        results[prop_name] = float(value)
                        
                        # Handle unit conversions
                        if len(match.groups()) > 1:
                            unit = match.group(2).lower()
                            if prop_name == "tensile_strength" and unit == "psi":
                                # Convert PSI to MPa
                                results[prop_name] = round(results[prop_name] * 0.00689476, 2)
                            elif prop_name == "flexural_modulus" and unit == "gpa":
                                # Convert GPa to MPa
                                results[prop_name] = round(results[prop_name] * 1000, 2)
                    except (ValueError, IndexError):
                        pass
                    break  # Use first match
        
        return results
    
    def extract_from_url(self, pdf_url: str) -> Dict[str, Any]:
        """Download and extract from a PDF URL"""
        import requests
        import tempfile
        import os
        
        try:
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            try:
                return self.extract_from_pdf(tmp_path)
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            print(f"Error downloading PDF from {pdf_url}: {e}")
            return {}
