from sqlalchemy import BigInteger, Boolean, Column, Date, Float, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import relationship
from src.database.postgres_client import Base


# ==========================================
# TABLAS DE DIMENSIÓN (Dimensiones)
# ==========================================

class DimArtista(Base):
    __tablename__ = "dim_artista"

    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_artista = Column(String(255), nullable=False, index=True)

    escuchas = relationship("FactEscuchas", back_populates="artista")


class DimCancion(Base):
    __tablename__ = "dim_cancion"

    track_id = Column(Integer, primary_key=True, autoincrement=True)
    uri_spotify = Column(String(255), nullable=True, index=True)
    nombre_cancion = Column(String(255), nullable=False, index=True)

    escuchas = relationship("FactEscuchas", back_populates="cancion")


class DimTiempo(Base):
    __tablename__ = "dim_tiempo"

    fecha_id = Column(Integer, primary_key=True)  # Formato AAAAMMDD (Ej: 20240520)
    fecha = Column(Date, nullable=False, unique=True)
    anio = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False)
    dia = Column(Integer, nullable=False)
    nombre_dia = Column(String(20), nullable=False)
    trimestre = Column(Integer, nullable=False)

    escuchas = relationship("FactEscuchas", back_populates="tiempo")


# ==========================================
# TABLA DE HECHOS (Fact Table)
# ==========================================

class FactEscuchas(Base):
    __tablename__ = "fact_escuchas"

    escucha_id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Claves foráneas hacia las dimensiones
    fecha_id = Column(Integer, ForeignKey("dim_tiempo.fecha_id"), nullable=False, index=True)
    artist_id = Column(Integer, ForeignKey("dim_artista.artist_id"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("dim_cancion.track_id"), nullable=False, index=True)

    # Atributos de tiempo en hora local Colombia (UTC-5) y auditoría
    hora_local = Column(SmallInteger, nullable=False, index=True)  # 0 a 23
    franja_dia = Column(String(20), nullable=False)               # 'Madrugada', 'Mañana', 'Tarde', 'Noche'
    es_fin_semana = Column(Boolean, nullable=False)
    ts_utc = Column(String(50), nullable=False)                   # Timestamp original en UTC

    # Métricas cuantitativas y flags de auditoría
    ms_reproducidos = Column(BigInteger, nullable=False)
    min_reproducidos = Column(Float, nullable=False)
    es_skip = Column(Boolean, nullable=False, default=False, index=True)  # True si ms_reproducidos < 30000
    modo_incognito = Column(Boolean, default=False)

    # Relaciones SQLAlchemy
    artista = relationship("DimArtista", back_populates="escuchas")
    cancion = relationship("DimCancion", back_populates="escuchas")
    tiempo = relationship("DimTiempo", back_populates="escuchas")