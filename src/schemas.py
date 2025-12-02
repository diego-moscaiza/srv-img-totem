from pydantic import BaseModel
from typing import Optional, Dict, Any


class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    imagen_listado: str
    imagen_caracteristicas: str
    imagen_caracteristicas_2: Optional[str] = None
    cuotas: Optional[Dict[str, float]] = None
    mes: str
    ano: int
    segmento: str = "fnb"
    estado: str = "disponible"
    stock: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    categoria: Optional[str] = None
    imagen_listado: Optional[str] = None
    imagen_caracteristicas: Optional[str] = None
    imagen_caracteristicas_2: Optional[str] = None
    cuotas: Optional[Dict[str, float]] = None
    mes: Optional[str] = None
    ano: Optional[int] = None
    segmento: Optional[str] = None
    estado: Optional[str] = None
    stock: Optional[bool] = None


class Producto(ProductoBase):
    id: int

    class Config:
        from_attributes = True
