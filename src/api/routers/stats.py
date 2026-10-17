from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.postgres_client import get_db
from src.api.schemas.stats import TopTrackOut

router = APIRouter(prefix="/stats", tags=["Estadísticas Analíticas"])

@router.get("/monthly")
def get_monthly_stats(
    anio: Optional[int] = Query(None, description="Año de consulta"),
    artist_id: Optional[int] = Query(None, description="ID del artista"),
    include_skips: bool = Query(False, description="Incluir reproducciones < 30s"),
    db: Session = Depends(get_db)
):
    sql = """
        SELECT anio, mes, artist_id, nombre_artista, 
               SUM(total_escuchas) AS total_escuchas, 
               SUM(minutos_totales) AS minutos_totales
        FROM v_gold_monthly
        WHERE (:include_skips = TRUE OR es_skip = FALSE)
          AND (:anio IS NULL OR anio = :anio)
          AND (:artist_id IS NULL OR artist_id = :artist_id)
        GROUP BY anio, mes, artist_id, nombre_artista
        ORDER BY anio ASC, mes ASC, minutos_totales DESC;
    """
    result = db.execute(text(sql), {
        "include_skips": include_skips,
        "anio": anio,
        "artist_id": artist_id
    }).mappings().all()
    return list(result)

@router.get("/hourly")
def get_hourly_stats(
    artist_id: Optional[int] = Query(None),
    include_skips: bool = Query(False),
    db: Session = Depends(get_db)
):
    sql = """
        SELECT hora_local, nombre_dia, franja_dia, es_fin_semana,
               SUM(total_escuchas) AS total_escuchas,
               SUM(minutos_totales) AS minutos_totales
        FROM v_gold_hourly
        WHERE (:include_skips = TRUE OR es_skip = FALSE)
          AND (:artist_id IS NULL OR artist_id = :artist_id)
        GROUP BY hora_local, nombre_dia, franja_dia, es_fin_semana
        ORDER BY hora_local ASC;
    """
    result = db.execute(text(sql), {
        "include_skips": include_skips,
        "artist_id": artist_id
    }).mappings().all()
    return list(result)

@router.get("/flow")
def get_flow_stats(
    limit: int = Query(20, description="Top N artistas para el diagrama Sankey"),
    include_skips: bool = Query(False),
    db: Session = Depends(get_db)
):
    sql = """
        WITH top_artistas AS (
            SELECT nombre_artista, SUM(minutos_totales) AS total_min
            FROM v_gold_flow
            WHERE (:include_skips = TRUE OR es_skip = FALSE)
            GROUP BY nombre_artista
            ORDER BY total_min DESC
            LIMIT :limit
        )
        SELECT f.nombre_artista, f.franja_dia, 
               SUM(f.minutos_totales) AS minutos_totales
        FROM v_gold_flow f
        JOIN top_artistas ta ON f.nombre_artista = ta.nombre_artista
        WHERE (:include_skips = TRUE OR f.es_skip = FALSE)
        GROUP BY f.nombre_artista, f.franja_dia
        ORDER BY ta.total_min DESC;
    """
    result = db.execute(text(sql), {
        "include_skips": include_skips,
        "limit": limit
    }).mappings().all()
    return list(result)

@router.get("/artists")
def get_artists(
    q: Optional[str] = Query(None, description="Búsqueda por nombre de artista"),
    limit: int = Query(50, le=200, description="Máximo de artistas"),
    db: Session = Depends(get_db)
):
    sql = """
        SELECT artist_id, nombre_artista
        FROM dim_artista
        WHERE (CAST(:q AS TEXT) IS NULL OR nombre_artista ILIKE '%' || CAST(:q AS TEXT) || '%')
        ORDER BY nombre_artista ASC
        LIMIT :limit;
    """
    result = db.execute(text(sql), {
        "q": q,
        "limit": limit
    }).mappings().all()
    return list(result)

@router.get("/top-tracks", response_model=list[TopTrackOut])
def get_top_tracks(
    limit: int = Query(10, le=50, description="Top N canciones"),
    anio: Optional[int] = Query(None, description="Año de consulta"),
    artist_id: Optional[int] = Query(None, description="ID del artista"),
    include_skips: bool = Query(False, description="Incluir reproducciones < 30s"),
    db: Session = Depends(get_db),
) -> list[TopTrackOut]:
    sql = """
        SELECT c.track_id, c.nombre_cancion, a.nombre_artista,
               COUNT(f.escucha_id) AS total_escuchas,
               ROUND(SUM(f.min_reproducidos)::numeric, 2) AS minutos_totales
        FROM fact_escuchas f
        JOIN dim_cancion c ON f.track_id = c.track_id
        JOIN dim_artista a ON f.artist_id = a.artist_id
        JOIN dim_tiempo t ON f.fecha_id = t.fecha_id
        WHERE (:include_skips = TRUE OR f.es_skip = FALSE)
          AND (CAST(:anio AS INTEGER) IS NULL OR t.anio = :anio)
          AND (CAST(:artist_id AS INTEGER) IS NULL OR f.artist_id = :artist_id)
          AND f.ms_reproducidos >= 45000
          AND c.nombre_cancion NOT IN (
              'Sin Información', 'Desconocido', 'Archivo Local / Sin Metadata',
              'Pistas Locales - Susumu Hirasawa'
          )
          AND a.nombre_artista NOT IN ('Desconocido', 'Sin Información')
          AND a.nombre_artista NOT LIKE '[Podcast]%'
        GROUP BY c.track_id, c.nombre_cancion, a.nombre_artista
        ORDER BY total_escuchas DESC
        LIMIT :limit;
    """
    result = db.execute(text(sql), {
        "limit": limit,
        "anio": anio,
        "artist_id": artist_id,
        "include_skips": include_skips
    }).mappings().all()
    return [TopTrackOut.model_validate(dict(row)) for row in result]
