import os
import datetime
import pandas as pd
from pymongo import MongoClient
from zoneinfo import ZoneInfo
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.database.postgres_client import SessionLocal, engine
from src.models.star_schema import DimArtista, DimCancion, DimTiempo, FactEscuchas

# Cargar variables de entorno desde el archivo .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "spotify_raw_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "streaming_history_raw")


def obtener_datos_bronze():
    """Conecta a MongoDB y extrae todos los eventos de escucha crudos."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    coleccion = db[MONGO_COLLECTION]

    cursor = coleccion.find({}, {"_id": 0})
    df = pd.DataFrame(list(cursor))
    client.close()
    return df


def extraer_artista_fallback(row):
    """Extrae el nombre del artista priorizando metadatos oficiales y luego campos locales."""
    # 1. Intentar con el metadato principal de Spotify
    val = row.get("master_metadata_album_artist_name")
    if pd.notna(val) and str(val).strip() != "":
        return str(val).strip()

    # 2. Intentar con la columna legacy 'artistName'
    val_legacy = row.get("artistName")
    if pd.notna(val_legacy) and str(val_legacy).strip() != "":
        return str(val_legacy).strip()

    # 3. Extraer desde 'spotify_track_uri' si es un archivo local (spotify:local:Artista:...)
    uri = str(row.get("spotify_track_uri", ""))
    if uri.startswith("spotify:local:"):
        partes = uri.split(":")
        if len(partes) >= 3 and partes[2]:
            return partes[2].replace("+", " ").strip()

    return "Desconocido"


def extraer_cancion_fallback(row):
    """Extrae el nombre de la canción priorizando metadatos oficiales y luego campos locales."""
    # 1. Intentar con el metadato principal
    val = row.get("master_metadata_track_name")
    if pd.notna(val) and str(val).strip() != "":
        return str(val).strip()

    # 2. Intentar con 'trackName' legacy
    val_legacy = row.get("trackName")
    if pd.notna(val_legacy) and str(val_legacy).strip() != "":
        return str(val_legacy).strip()

    # 3. Extraer desde 'spotify_track_uri' local (spotify:local:Artista:Album:Cancion:Duracion)
    uri = str(row.get("spotify_track_uri", ""))
    if uri.startswith("spotify:local:"):
        partes = uri.split(":")
        if len(partes) >= 5 and partes[4]:
            return partes[4].replace("+", " ").strip()

    return "Sin Información"


def transformar_y_cargar_silver():
    print("Extrayendo datos crudos desde MongoDB (Capa Bronze)...")
    df = obtener_datos_bronze()
    print(f"Registros recuperados de Mongo: {len(df)}")

    if df.empty:
        print("No se encontraron registros en MongoDB.")
        return

    uri_col = "spotify_track_uri" if "spotify_track_uri" in df.columns else "spotifyTrackUri"

    db: Session = SessionLocal()

    try:
        # ----------------------------------------------------
        # 1. TRATAMIENTO DE ARTISTAS Y CANCIONES (CON FALLBACK LOCAL)
        # ----------------------------------------------------
        print("Procesando metadatos de artistas y canciones (archivos locales incluidos)...")
        df["artista_normalizado"] = df.apply(extraer_artista_fallback, axis=1)
        df["cancion_normalizada"] = df.apply(extraer_cancion_fallback, axis=1)
        df[uri_col] = df[uri_col].fillna("uri:desconocida").astype(str).str.strip()

        print("Poblando dimension dim_artista...")
        artistas_unicos = df["artista_normalizado"].unique()
        for nombre in artistas_unicos:
            stmt = insert(DimArtista).values(nombre_artista=nombre).on_conflict_do_nothing()
            db.execute(stmt)
        db.commit()

        # Mapa de Artistas (Nombre -> ID)
        artistas_db = db.query(DimArtista).all()
        mapa_artistas = {a.nombre_artista: a.artist_id for a in artistas_db}

        print("Poblando dimension dim_cancion...")
        canciones_unicas = df[[uri_col, "cancion_normalizada"]].drop_duplicates()
        for _, row in canciones_unicas.iterrows():
            stmt = insert(DimCancion).values(
                uri_spotify=row[uri_col],
                nombre_cancion=row["cancion_normalizada"]
            ).on_conflict_do_nothing()
            db.execute(stmt)
        db.commit()

        # Mapa de Canciones (URI -> ID)
        canciones_db = db.query(DimCancion).all()
        mapa_canciones = {c.uri_spotify: c.track_id for c in canciones_db}

        # ----------------------------------------------------
        # 2. TRANSFORMACIONES TEMPORALES (UTC -> America/Bogota)
        # ----------------------------------------------------
        print("Procesando marcas temporales y hora local de Colombia...")
        tz_bogota = ZoneInfo("America/Bogota")

        df["ts_dt"] = pd.to_datetime(df["ts"], utc=True)
        df["ts_bogota"] = df["ts_dt"].dt.tz_convert(tz_bogota)

        df["fecha"] = df["ts_bogota"].dt.date
        df["fecha_id"] = df["ts_bogota"].dt.strftime("%Y%m%d").astype(int)
        df["hora_local"] = df["ts_bogota"].dt.hour
        df["dia_semana_num"] = df["ts_bogota"].dt.weekday

        # Mapeo de Franja del Día
        def obtener_franja(hora):
            if 0 <= hora < 6:
                return "Madrugada"
            elif 6 <= hora < 12:
                return "Mañana"
            elif 12 <= hora < 18:
                return "Tarde"
            else:
                return "Noche"

        df["franja_dia"] = df["hora_local"].apply(obtener_franja)
        df["es_fin_semana"] = df["dia_semana_num"].isin([5, 6])

        # Poblar dim_tiempo
        print("Poblando dimension dim_tiempo...")
        fechas_unicas = df[["fecha_id", "fecha", "ts_bogota"]].drop_duplicates(subset=["fecha_id"])

        dias_espanol = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
        }

        for _, row in fechas_unicas.iterrows():
            f_dt = row["ts_bogota"]
            nombre_dia = dias_espanol.get(f_dt.strftime("%A"), f_dt.strftime("%A"))
            trimestre = (f_dt.month - 1) // 3 + 1

            stmt = insert(DimTiempo).values(
                fecha_id=int(row["fecha_id"]),
                fecha=row["fecha"],
                anio=int(f_dt.year),
                mes=int(f_dt.month),
                dia=int(f_dt.day),
                nombre_dia=nombre_dia,
                trimestre=int(trimestre)
            ).on_conflict_do_nothing()
            db.execute(stmt)
        db.commit()

        # ----------------------------------------------------
        # 3. CONSTRUCCIÓN DE LA TABLA DE HECHOS (fact_escuchas)
        # ----------------------------------------------------
        print("Cargando hechos en fact_escuchas...")
        df["artist_id"] = df["artista_normalizado"].map(mapa_artistas)
        df["track_id"] = df[uri_col].map(mapa_canciones)
        df["es_skip"] = df["ms_played"] < 30000
        df["min_reproducidos"] = (df["ms_played"] / 60000.0).round(2)
        df["incognito"] = df["incognito_mode"].fillna(False).astype(bool) if "incognito_mode" in df.columns else False

        lote = []
        tamano_lote = 5000

        for idx, row in df.iterrows():
            hecho = {
                "fecha_id": int(row["fecha_id"]),
                "artist_id": int(row["artist_id"]),
                "track_id": int(row["track_id"]),
                "hora_local": int(row["hora_local"]),
                "franja_dia": row["franja_dia"],
                "es_fin_semana": bool(row["es_fin_semana"]),
                "ts_utc": str(row["ts"]),
                "ms_reproducidos": int(row["ms_played"]),
                "min_reproducidos": float(row["min_reproducidos"]),
                "es_skip": bool(row["es_skip"]),
                "modo_incognito": bool(row["incognito"])
            }
            lote.append(hecho)

            if len(lote) >= tamano_lote:
                db.bulk_insert_mappings(FactEscuchas, lote)
                db.commit()
                lote = []

        if lote:
            db.bulk_insert_mappings(FactEscuchas, lote)
            db.commit()

        print("Migración de Bronze a Silver completada con éxito.")

    except Exception as e:
        db.rollback()
        print(f"Error durante el proceso ETL: {str(e)}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    transformar_y_cargar_silver()