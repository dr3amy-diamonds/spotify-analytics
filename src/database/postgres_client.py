import os
from collections.abc import Iterator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# override=True obliga a recargar los valores del .env actual
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

# Si no existe DATABASE_URL, la construimos a partir de las variables individuales
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    
    if all([user, password, host, port, db]):
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Principio Fail-Fast: Si no hay URL, detenemos la ejecución por seguridad
if not DATABASE_URL:
    raise ValueError("CRÍTICO: No se encontró DATABASE_URL ni las variables POSTGRES_* en el archivo .env")

# SQLAlchemy 2.1 usa psycopg (v3) por defecto; venv trae psycopg2-binary
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_ctx():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def ping() -> bool:
    """Verifica la conectividad con PostgreSQL."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def init_db():
    """Crea las tablas definidas en los modelos SQLAlchemy si no existen."""
    Base.metadata.create_all(bind=engine)
