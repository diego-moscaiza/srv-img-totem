from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from src.database import Producto as DBProducto, SessionLocal
from src.schemas import Producto, ProductoCreate, ProductoUpdate
from typing import List
from pathlib import Path

router = APIRouter(prefix="/api", tags=["productos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Panel de administración - carga HTML desde archivo externo"""
    template_path = Path(__file__).parent.parent / "templates" / "admin.html"
    if not template_path.exists():
        return "<h1>Error: Template no encontrado</h1>"
    return template_path.read_text(encoding="utf-8")


@router.get("/productos", response_model=List[Producto])
async def listar_productos(db=Depends(get_db)):
    """Listar todos los productos"""
    import json

    productos = db.query(DBProducto).all()
    # Convertir cuotas de string a dict si es necesario
    for p in productos:
        if isinstance(p.cuotas, str):
            try:
                p.cuotas = json.loads(p.cuotas)
            except:
                p.cuotas = {}
    return productos


@router.get("/productos/{producto_id}", response_model=Producto)
async def obtener_producto(producto_id: int, db=Depends(get_db)):
    """Obtener un producto por ID"""
    import json

    producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Convertir cuotas de string a dict si es necesario
    if isinstance(producto.cuotas, str):
        try:
            producto.cuotas = json.loads(producto.cuotas)
        except:
            producto.cuotas = {}
    return producto


@router.post("/productos", response_model=Producto)
async def crear_producto(producto: ProductoCreate, db=Depends(get_db)):
    """Crear un nuevo producto"""
    db_producto = DBProducto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.put("/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int, producto: ProductoUpdate, db=Depends(get_db)
):
    """Actualizar un producto"""
    db_producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = producto.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_producto, key, value)

    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@router.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int, db=Depends(get_db)):
    """Eliminar un producto"""
    db_producto = db.query(DBProducto).filter(DBProducto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}
