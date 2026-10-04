import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cargar variables de entorno desde el archivo .env
load_dotenv()

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret123")
HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = os.getenv("POSTGRES_PORT", "5432")
DB = os.getenv("POSTGRES_DB", "spotify_analytics_db")

# Cadena de conexión para PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

# Motor SQLAlchemy con soporte UTF-8 explícito
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "utf8"},
    echo=False
)

# Creador de sesiones para consultas futuras
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa compartida
Base = declarative_base()


def get_db():
    """Generador de sesiones de base de datos para la API o scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()