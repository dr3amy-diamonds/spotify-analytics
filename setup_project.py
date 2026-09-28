import os
from pathlib import Path


def crear_estructura_proyecto():
    # 1. Lista de directorios a crear
    directorios = [
        "data/raw",
        "data/processed",
        "src/database",
        "src/ingestion",
        "src/etl",
        "src/analytics",
        "src/api/routers",
        "src/api/schemas",
        "tests",
    ]

    # 2. Lista de archivos a crear
    archivos = [
        ".env",
        ".gitignore",
        "README.md",
        "requirements.txt",
        "src/__init__.py",
        "src/database/__init__.py",
        "src/database/mongo_client.py",
        "src/database/postgres_client.py",
        "src/ingestion/__init__.py",
        "src/ingestion/ingest_raw.py",
        "src/etl/__init__.py",
        "src/etl/spotify_api.py",
        "src/etl/transform_data.py",
        "src/etl/load_star_schema.py",
        "src/analytics/__init__.py",
        "src/analytics/metrics.py",
        "src/analytics/clustering.py",
        "src/api/__init__.py",
        "src/api/main.py",
        "tests/__init__.py",
        "tests/test_ingestion.py",
        "tests/test_metrics.py",
    ]

    print("🚀 Creando estructura del proyecto Spotify Analytics...\n")

    # Crear directorios
    for folder in directorios:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio verificado/creado: {folder}")

    # Crear archivos vacíos si no existen
    for file_path in archivos:
        path = Path(file_path)
        if not path.exists():
            path.touch()
            print(f"📄 Archivo creado: {file_path}")
        else:
            print(f"⚠️ El archivo ya existe (se omitió): {file_path}")

    print("\n✅ ¡Estructura del proyecto creada con éxito!")


if __name__ == "__main__":
    crear_estructura_proyecto()