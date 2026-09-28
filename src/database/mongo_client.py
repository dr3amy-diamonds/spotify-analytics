import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Cargar variables de entorno
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASS = os.getenv("MONGO_PASS", "secret123")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "spotify_raw_db")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"


def get_mongo_collection(collection_name: str = "streaming_history_raw"):
    """Establece conexión con MongoDB y retorna la colección especificada."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[collection_name]

    # Índice único para evitar duplicados
    collection.create_index(
        [("ts", 1), ("spotify_track_uri", 1), ("ms_played", 1)],
        unique=True,
        name="unique_stream_event",
    )

    return collection