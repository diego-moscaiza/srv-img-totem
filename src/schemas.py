from pydantic import BaseModel, field_serializer
from typing import Optional, Dict, Any
import os


class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    imagen_listado: str
    imagen_caracteristicas: Optional[str] = None
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

    def construct_image_url(self, imagen_path: Optional[str]) -> Optional[str]:
        """Construye URL absoluta para una imagen desde su ruta relativa"""
        if not imagen_path:
            return None
        
        # Si ya es una URL absoluta, devolverla tal cual
        if imagen_path.startswith("http://") or imagen_path.startswith("https://"):
            return imagen_path
        
        server_url = os.getenv("SERVER_URL", "http://localhost:8000").rstrip("/")
        # Asegurar que la ruta no comience con /
        imagen_path = imagen_path.lstrip("/")
        return f"{server_url}/api/catalogos/{imagen_path}"

    @field_serializer("imagen_listado", "imagen_caracteristicas", "imagen_caracteristicas_2")
    def serialize_imagenes(self, valor: Optional[str], _info) -> Optional[str]:
        """Serializa las rutas de imágenes como URLs absolutas"""
        return self.construct_image_url(valor)
