from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


# Determinar la ruta de la base de datos según el entorno
def get_database_url():
    """Obtiene la URL de la base de datos, compatible con Windows y Linux"""

    # Si hay una variable de entorno definida, usarla
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Ruta por defecto relativa al directorio del proyecto
    # Funciona tanto en Windows como en Linux
    base_dir = Path(__file__).parent.parent  # srv-img-totem/
    db_path = base_dir / "catalogos.db"

    # SQLite usa formato diferente según el SO
    # Windows: sqlite:///C:/path/to/db.db
    # Linux: sqlite:////srv/data/db.db o sqlite:///./db.db
    return f"sqlite:///{db_path}"


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True)
    nombre = Column(String(200))
    descripcion = Column(String(500))
    precio = Column(Float)
    categoria = Column(String(100))
    imagen_listado = Column(String(500))
    imagen_caracteristicas = Column(String(500))
    imagen_caracteristicas_2 = Column(String(500), nullable=True, default=None)
    cuotas = Column(JSON)  # {"3": 338.85, "6": 178.87, ...}
    mes = Column(String(20))
    ano = Column(Integer)
    segmento = Column(String(50), default="fnb", index=True)  # fnb, gaso, etc.
    estado = Column(
        String(50), default="disponible", index=True
    )  # disponible, no disponible, agotado, etc.
    stock = Column(Boolean, default=True)
    stock = Column(Boolean, default=True)


# Crear las tablas
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
