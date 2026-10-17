from pydantic import BaseModel


class TopTrackOut(BaseModel):
    track_id: int
    nombre_cancion: str
    nombre_artista: str
    total_escuchas: int
    minutos_totales: float
