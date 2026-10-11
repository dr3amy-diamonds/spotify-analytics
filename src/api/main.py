from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.postgres_client import ping, init_db
from src.api.routers import stats

app = FastAPI(
    title="Spotify Analytics API",
    description="API REST de la Capa Gold para alimentar el dashboard interactivo en D3.js",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde React / Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se restringe al puerto del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(stats.router)

@app.on_event("startup")
def startup_db_check():
    """Inicializa la estructura de base de datos al arrancar el servidor."""
    init_db()

@app.get("/health", tags=["Health Check"])
def health_check():
    """Endpoint para verificar el estado de la API y la conexión a PostgreSQL."""
    db_ok = ping()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database_connected": db_ok
    }