from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Crear la conexión a SQLite (sin necesidad de PostgreSQL)
DATABASE_URL = "sqlite:///./catalogos.db"

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
    cuotas = Column(JSON)  # {"3": 338.85, "6": 178.87, ...}
    mes = Column(String(20))
    ano = Column(Integer)
    stock = Column(Boolean, default=True)


# Crear las tablas
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
