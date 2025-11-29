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
    cuotas: Dict[str, float]
    mes: str
    ano: int
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
    cuotas: Optional[Dict[str, float]] = None
    mes: Optional[str] = None
    ano: Optional[int] = None
    stock: Optional[bool] = None


class Producto(ProductoBase):
    id: int

    class Config:
        from_attributes = True
