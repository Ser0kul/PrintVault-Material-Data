# Material Database Scraper

Sistema de scraping para generar bases de datos de resinas y filamentos para PrintVault.

## 🚀 Quick Start

```powershell
# 1. Crear entorno virtual
cd tools/material-scraper
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar (dry-run para ver qué haría)
python generate_db.py --dry-run

# 4. Ejecutar (guardar a src/data/)
python generate_db.py
```

## 📂 Estructura

```
material-scraper/
├── requirements.txt      # Dependencias Python
├── schema.py             # Modelos Pydantic (rico + simple)
├── config.py             # Lista de marcas y URLs
├── builder.py            # Convierte datos a modelos
├── generate_db.py        # Script principal
├── scrapers/
│   ├── base.py           # Clase abstracta
│   └── generic.py        # Scraper genérico (Shopify, etc)
└── extractors/
    └── tds_pdf.py        # Extractor de PDFs técnicos
```

## 📋 Opciones de Ejecución

```bash
# Solo resinas
python generate_db.py --resins

# Solo filamentos
python generate_db.py --filaments

# Exportar schema simple (compatible con frontend actual)
python generate_db.py --simple

# Merge con base de datos existente (no duplicar)
python generate_db.py --merge

# Dry-run (no guarda, solo muestra)
python generate_db.py --dry-run
```

## 🏭 Marcas Configuradas

### Resinas (15)

- **Premium**: Formlabs, Henkel Loctite, BASF Forward AM
- **Consumer**: Anycubic, ELEGOO, Siraya Tech, Phrozen, Sunlu, eSUN, Creality
- **Specialty**: BlueCast, AmeraLabs, Monocure 3D, SprintRay, NextDent

### Filamentos (18)

- **Premium**: Prusament, Polymaker, Bambu Lab, ColorFabb, Fillamentum
- **Consumer**: eSUN, Sunlu, Hatchbox, Overture, ELEGOO, Creality, Eryone, Inland, Anycubic
- **Specialty**: MatterHackers, NinjaTek, Proto-pasta, Fiberlogy

## ➕ Añadir Nueva Marca

1. Editar `config.py`
2. Añadir a `RESIN_BRANDS` o `FILAMENT_BRANDS`:

```python
{"name": "NuevaMarca", "url": "https://...", "type": "consumer"}
```

## 📦 Schema

### Schema Rico (recomendado)

Incluye: propiedades físicas, comerciales, certificaciones, perfiles de impresión.

### Schema Simple (compatible con frontend actual)

Convierte automáticamente con `resina_to_simple_schema()` o `filamento_to_simple_schema()`.

## ⚠️ Notas Legales

- Este scraper respeta `robots.txt` y usa delays entre requests
- Solo extrae datos públicos de páginas de producto
- No bypasea protecciones ni captchas
- Uso ético y responsable
