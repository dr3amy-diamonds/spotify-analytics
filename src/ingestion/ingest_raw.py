import json
from pathlib import Path
from pymongo import errors
from src.database.mongo_client import get_mongo_collection


def ingestar_carpeta_raw(directorio_raw: str = "data/raw"):
    """Escanea la carpeta raw y carga todos los archivos .json a MongoDB."""
    folder_path = Path(directorio_raw)

    if not folder_path.exists():
        print(f"❌ Error: La carpeta {directorio_raw} no existe.")
        return

    # Buscar todos los archivos .json en la carpeta
    archivos_json = sorted(list(folder_path.glob("*.json")))

    if not archivos_json:
        print(
            f"⚠️ No se encontraron archivos .json en '{directorio_raw}'. "
            "Asegúrate de copiar allí tus archivos de Spotify."
        )
        return

    print(
        f"📂 Se encontraron {len(archivos_json)} archivos JSON para procesar en la Capa Bronze.\n"
    )

    collection = get_mongo_collection()

    total_registros_procesados = 0
    total_insertados = 0
    total_duplicados = 0

    for archivo in archivos_json:
        print(f"Procesando: {archivo.name}...")
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(
                    f"  ⚠️ El archivo {archivo.name} no contiene una lista. Omitiendo..."
                )
                continue

            insertados_archivo = 0
            duplicados_archivo = 0

            for registro in data:
                total_registros_procesados += 1
                try:
                    collection.insert_one(registro)
                    insertados_archivo += 1
                except errors.DuplicateKeyError:
                    duplicados_archivo += 1

            total_insertados += insertados_archivo
            total_duplicados += duplicados_archivo
            print(
                f"  -> Insertados: {insertados_archivo} | Duplicados omitidos: {duplicados_archivo}"
            )

        except Exception as e:
            print(f"  ❌ Error leyendo {archivo.name}: {e}")

    print("\n" + "=" * 55)
    print("--- RESUMEN FINAL DE INGESTA (Bronze Layer) ---")
    print("=" * 55)
    print(f"Archivos JSON procesados:             {len(archivos_json)}")
    print(f"Total registros analizados:           {total_registros_procesados}")
    print(f"Nuevos documentos insertados en Mongo:{total_insertados}")
    print(f"Documentos duplicados omitidos:       {total_duplicados}")
    print(
        f"Total acumulado en la BDD (Mongo):    {collection.count_documents({})}"
    )
    print("=" * 55)


if __name__ == "__main__":
    ingestar_carpeta_raw("data/raw")