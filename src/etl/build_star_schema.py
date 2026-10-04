from src.database.postgres_client import engine
from src.models.star_schema import Base


def crear_esquema_estrella():
    """Crea físicamente las tablas del Modelo Dimensional en PostgreSQL."""
    print(" Conectando a PostgreSQL y creando el Modelo Dimensional en español...")
    Base.metadata.create_all(bind=engine)
    print(" ¡Tablas creadas exitosamente en PostgreSQL!")


if __name__ == "__main__":
    crear_esquema_estrella()