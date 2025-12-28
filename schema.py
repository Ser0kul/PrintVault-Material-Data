"""
Material Database Schema - Pydantic Models
Rich schema for resins and filaments with full technical data
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# ============= RESIN SCHEMA =============

class PropiedadesFisicasResina(BaseModel):
    """Physical properties for resins"""
    densidad_g_ml: Optional[float] = Field(None, description="Density in g/ml")
    viscosidad_cps: Optional[int] = Field(None, description="Viscosity in centipoise")
    dureza_shore: Optional[str] = Field(None, description="Shore hardness (e.g., '85D')")
    contraccion_pct: Optional[float] = Field(None, description="Shrinkage percentage")
    resistencia_traccion_mpa: Optional[float] = Field(None, description="Tensile strength in MPa")
    elongacion_rotura_pct: Optional[float] = Field(None, description="Elongation at break %")
    modulo_flexion_mpa: Optional[float] = Field(None, description="Flexural modulus in MPa")
    temperatura_deflexion_c: Optional[float] = Field(None, description="HDT in Celsius")


class PropiedadesComerciales(BaseModel):
    """Commercial properties"""
    coste_unidad: Optional[float] = Field(None, description="Cost per unit (bottle)")
    moneda: str = "EUR"
    volumen_ml: Optional[int] = Field(None, description="Volume in ml (e.g., 500, 1000)")
    url_compra: Optional[str] = Field(None, description="Purchase URL")
    disponible: bool = True


class PerfilImpresionResina(BaseModel):
    """Print profile for a specific printer"""
    impresora_modelo: str
    altura_capa_mm: float = 0.05
    capas_base: int = 5
    tiempo_exposicion_s: float
    tiempo_exposicion_base_s: float
    distancia_elevacion_mm: float = 5.0
    velocidad_elevacion_mm_s: float = 60.0
    velocidad_retraccion_mm_s: float = 150.0
    tiempo_reposo_antes_s: float = 0.0
    tiempo_reposo_despues_s: float = 0.0


class Resina(BaseModel):
    """Full resin model"""
    id: str = Field(..., description="Unique ID like 'RES-0001'")
    marca: str
    nombre: str
    tipo: str = Field(..., description="Type: Standard, Tough, Flexible, Castable, etc.")
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    color: Optional[str] = Field(None, description="Hex color code")
    color_nombre: Optional[str] = None
    tags: List[str] = []
    
    propiedades_fisicas: PropiedadesFisicasResina = PropiedadesFisicasResina()
    propiedades_comerciales: PropiedadesComerciales = PropiedadesComerciales()
    
    certificaciones: List[str] = []
    longitud_onda_nm: List[int] = Field(default=[405], description="Compatible wavelengths")
    
    perfiles_impresion: List[PerfilImpresionResina] = []
    
    fecha_actualizacion: str = Field(default_factory=lambda: date.today().isoformat())
    fuente_datos: str = "manual"
    url_fabricante: Optional[str] = None
    url_tds: Optional[str] = None


# ============= FILAMENT SCHEMA =============

class PropiedadesFisicasFilamento(BaseModel):
    """Physical properties for filaments"""
    densidad_g_cm3: Optional[float] = Field(None, description="Density in g/cm³")
    diametro_mm: float = 1.75
    tolerancia_mm: float = 0.02
    resistencia_traccion_mpa: Optional[float] = None
    elongacion_rotura_pct: Optional[float] = None
    modulo_flexion_mpa: Optional[float] = None
    temperatura_fusion_c: Optional[float] = None
    temperatura_transicion_vitrea_c: Optional[float] = None
    absorcion_agua_pct: Optional[float] = None


class PerfilImpresionFilamento(BaseModel):
    """Print profile for filaments"""
    impresora_modelo: Optional[str] = None
    temp_extrusor_c: int
    temp_cama_c: int
    temp_extrusor_primera_capa_c: Optional[int] = None
    temp_cama_primera_capa_c: Optional[int] = None
    velocidad_impresion_mm_s: Optional[int] = None
    velocidad_primera_capa_mm_s: Optional[int] = None
    ventilador_pct: int = 100
    retraccion_mm: Optional[float] = None
    velocidad_retraccion_mm_s: Optional[int] = None
    requiere_camara_cerrada: bool = False


class Filamento(BaseModel):
    """Full filament model"""
    id: str = Field(..., description="Unique ID like 'FIL-0001'")
    marca: str
    nombre: str
    material: str = Field(..., description="Material type: PLA, PETG, ABS, TPU, etc.")
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    color: Optional[str] = Field(None, description="Hex color code")
    color_nombre: Optional[str] = None
    tags: List[str] = []
    
    propiedades_fisicas: PropiedadesFisicasFilamento = PropiedadesFisicasFilamento()
    propiedades_comerciales: PropiedadesComerciales = PropiedadesComerciales()
    
    certificaciones: List[str] = []
    
    perfiles_impresion: List[PerfilImpresionFilamento] = []
    
    fecha_actualizacion: str = Field(default_factory=lambda: date.today().isoformat())
    fuente_datos: str = "manual"
    url_fabricante: Optional[str] = None
    url_tds: Optional[str] = None


# ============= HELPER FUNCTIONS =============

def resina_to_simple_schema(resina: Resina) -> dict:
    """Convert rich schema to current simple frontend schema"""
    profiles = {}
    for p in resina.perfiles_impresion:
        profiles[p.impresora_modelo] = {
            "layerHeight": p.altura_capa_mm,
            "bottomLayerCount": p.capas_base,
            "exposureTime": p.tiempo_exposicion_s,
            "bottomExposure": p.tiempo_exposicion_base_s,
            "liftDistance1": p.distancia_elevacion_mm,
            "liftSpeed1": p.velocidad_elevacion_mm_s,
            "retractSpeed1": p.velocidad_retraccion_mm_s
        }
    
    return {
        "brand": resina.marca,
        "name": resina.nombre,
        "image": resina.imagen_url,
        "type": resina.tipo,
        "description": resina.descripcion,
        "color": resina.color,
        "colorName": resina.color_nombre,
        "tags": resina.tags,
        "profiles": profiles if profiles else {"Default": {
            "layerHeight": 0.05,
            "bottomLayerCount": 5,
            "exposureTime": 2.5,
            "bottomExposure": 30,
            "liftDistance1": 4,
            "liftSpeed1": 60,
            "retractSpeed1": 150
        }}
    }


def filamento_to_simple_schema(filamento: Filamento) -> dict:
    """Convert rich schema to current simple frontend schema"""
    params = {}
    if filamento.perfiles_impresion:
        p = filamento.perfiles_impresion[0]
        params = {
            "printTemp": p.temp_extrusor_c,
            "bedTemp": p.temp_cama_c,
            "fanSpeed": p.ventilador_pct,
            "density": filamento.propiedades_fisicas.densidad_g_cm3 or 1.24,
            "tensileStrength": filamento.propiedades_fisicas.resistencia_traccion_mpa,
            "glassTransition": filamento.propiedades_fisicas.temperatura_transicion_vitrea_c
        }
    else:
        params = {
            "printTemp": 200,
            "bedTemp": 50,
            "fanSpeed": 100,
            "density": filamento.propiedades_fisicas.densidad_g_cm3 or 1.24,
            "tensileStrength": filamento.propiedades_fisicas.resistencia_traccion_mpa,
            "glassTransition": filamento.propiedades_fisicas.temperatura_transicion_vitrea_c
        }
    
    return {
        "brand": filamento.marca,
        "name": filamento.nombre,
        "material": filamento.material,
        "image": filamento.imagen_url,
        "description": filamento.descripcion,
        "color": filamento.color,
        "colorName": filamento.color_nombre,
        "tags": filamento.tags,
        "params": params
    }
