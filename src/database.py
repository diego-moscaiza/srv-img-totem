from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cargar .env si existe (para desarrollo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # En Docker no necesita dotenv

# Importar la configuración centralizada de BD
from src.config import DATABASE_URL

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
    imagen_caracteristicas = Column(String(500), nullable=True, default=None)
    imagen_caracteristicas_2 = Column(String(500), nullable=True, default=None)
    cuotas = Column(JSON)  # {"3": 338.85, "6": 178.87, ...}
    mes = Column(String(20))
    ano = Column(Integer)
    segmento = Column(String(50), default="fnb", index=True)  # fnb, gaso, etc.
    estado = Column(
        String(50), default="disponible", index=True
    )  # disponible, no_disponible, agotado
    stock = Column(Boolean, default=True)


# Crear las tablas
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
