"""
Material Database Builder
Converts scraped data into schema-compliant JSON
"""

from datetime import date
from typing import List, Dict, Any
from schema import (
    Resina, Filamento,
    PropiedadesFisicasResina, PropiedadesFisicasFilamento,
    PropiedadesComerciales, PerfilImpresionResina, PerfilImpresionFilamento,
    resina_to_simple_schema, filamento_to_simple_schema
)


class ResinBuilder:
    """Build Resina objects from raw scraped data"""
    
    def __init__(self):
        self.counter = 0
    
    def build(self, raw: Dict[str, Any]) -> Resina:
        """Convert raw scraped data to Resina model"""
        self.counter += 1
        
        # Build physical properties
        props_fisicas = PropiedadesFisicasResina(
            densidad_g_ml=raw.get("density"),
            viscosidad_cps=raw.get("viscosity"),
            dureza_shore=raw.get("hardness"),
            resistencia_traccion_mpa=raw.get("tensile_strength"),
            elongacion_rotura_pct=raw.get("elongation"),
            modulo_flexion_mpa=raw.get("flexural_modulus"),
            temperatura_deflexion_c=raw.get("hdt"),
            contraccion_pct=raw.get("shrinkage"),
        )
        
        # Build commercial properties
        props_comerciales = PropiedadesComerciales(
            coste_unidad=raw.get("price"),
            moneda="EUR",
            volumen_ml=raw.get("volume"),
            url_compra=raw.get("url"),
        )
        
        return Resina(
            id=f"RES-{self.counter:04d}",
            marca=raw.get("brand", "Unknown"),
            nombre=raw.get("name", "Unknown"),
            tipo=raw.get("type", "Standard"),
            descripcion=raw.get("description"),
            imagen_url=raw.get("image"),
            color=raw.get("color"),
            color_nombre=raw.get("color_name"),
            tags=raw.get("tags", []),
            propiedades_fisicas=props_fisicas,
            propiedades_comerciales=props_comerciales,
            certificaciones=raw.get("certifications", []),
            longitud_onda_nm=raw.get("wavelengths", [405]),
            fecha_actualizacion=date.today().isoformat(),
            fuente_datos=raw.get("fuente_datos", "web"),
            url_fabricante=raw.get("url"),
        )


class FilamentBuilder:
    """Build Filamento objects from raw scraped data"""
    
    def __init__(self):
        self.counter = 0
    
    def build(self, raw: Dict[str, Any]) -> Filamento:
        """Convert raw scraped data to Filamento model"""
        self.counter += 1
        
        # Build physical properties
        props_fisicas = PropiedadesFisicasFilamento(
            densidad_g_cm3=raw.get("density"),
            diametro_mm=raw.get("diameter", 1.75),
            tolerancia_mm=raw.get("tolerance", 0.02),
            resistencia_traccion_mpa=raw.get("tensile_strength"),
            elongacion_rotura_pct=raw.get("elongation"),
            modulo_flexion_mpa=raw.get("flexural_modulus"),
            temperatura_transicion_vitrea_c=raw.get("tg"),
        )
        
        # Build commercial properties
        props_comerciales = PropiedadesComerciales(
            coste_unidad=raw.get("price"),
            moneda="EUR",
            url_compra=raw.get("url"),
        )
        
        # Build default print profile if we have temps
        profiles = []
        if raw.get("print_temp") or raw.get("bed_temp"):
            profiles.append(PerfilImpresionFilamento(
                temp_extrusor_c=raw.get("print_temp", 200),
                temp_cama_c=raw.get("bed_temp", 50),
                ventilador_pct=raw.get("fan_speed", 100),
            ))
        
        return Filamento(
            id=f"FIL-{self.counter:04d}",
            marca=raw.get("brand", "Unknown"),
            nombre=raw.get("name", "Unknown"),
            material=raw.get("type", "PLA"),
            descripcion=raw.get("description"),
            imagen_url=raw.get("image"),
            color=raw.get("color"),
            color_nombre=raw.get("color_name"),
            tags=raw.get("tags", []),
            propiedades_fisicas=props_fisicas,
            propiedades_comerciales=props_comerciales,
            perfiles_impresion=profiles,
            fecha_actualizacion=date.today().isoformat(),
            fuente_datos=raw.get("fuente_datos", "web"),
            url_fabricante=raw.get("url"),
        )


def build_resins(raw_list: List[Dict]) -> List[Resina]:
    """Build list of Resina from raw data"""
    builder = ResinBuilder()
    return [builder.build(raw) for raw in raw_list if raw.get("name")]


def build_filaments(raw_list: List[Dict]) -> List[Filamento]:
    """Build list of Filamento from raw data"""
    builder = FilamentBuilder()
    return [builder.build(raw) for raw in raw_list if raw.get("name")]


def export_simple_schema(resins: List[Resina], filaments: List[Filamento]) -> tuple:
    """Export to current simple frontend schema"""
    simple_resins = [resina_to_simple_schema(r) for r in resins]
    simple_filaments = [filamento_to_simple_schema(f) for f in filaments]
    return simple_resins, simple_filaments


def export_rich_schema(resins: List[Resina], filaments: List[Filamento]) -> tuple:
    """Export full rich schema"""
    return (
        [r.model_dump() for r in resins],
        [f.model_dump() for f in filaments]
    )
