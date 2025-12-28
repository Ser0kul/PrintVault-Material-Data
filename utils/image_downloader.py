import os
import requests
import re
from typing import Optional
try:
    from utils.headers import get_headers
except ImportError:
    from .headers import get_headers

def slugify(text: str) -> str:
    """
    Normaliza un texto para usarlo como nombre de archivo.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text).strip('_')
    return text

def download_image(url: str, category: str, brand: str, name: str, output_root: str) -> Optional[str]:
    """
    Descarga una imagen y la guarda localmente si no existe.
    Retorna la ruta relativa de la imagen guardada.
    """
    if not url or url.startswith('data:'):
        return None

    # Limpiar y preparar carpetas
    category = "resins" if "resin" in category.lower() else "filaments"
    brand_slug = slugify(brand)
    name_slug = slugify(name)
    
    # Intentar detectar extensión de la URL
    ext = url.split('.')[-1].split('?')[0].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'webp', 'avif']:
        ext = 'jpg' # Default
        
    filename = f"{brand_slug}_{name_slug}.{ext}"
    relative_path = os.path.join("images", category, filename)
    absolute_path = os.path.join(output_root, relative_path)
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    
    # Si ya existe, no descargar de nuevo
    if os.path.exists(absolute_path) and os.path.getsize(absolute_path) > 0:
        return relative_path
        
    try:
        response = requests.get(url, headers=get_headers(), timeout=15, stream=True)
        if response.status_code == 200:
            with open(absolute_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return relative_path
        else:
            print(f"Error descargando imagen {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Excepción descargando imagen {url}: {str(e)}")
        
    return None
