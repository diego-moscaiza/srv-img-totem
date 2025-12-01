from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from typing import List, Dict
from src.catalogos_manager import CatalogoManager
from src.database import Producto as DBProducto, SessionLocal, engine
from src.database import Base
from src.schemas import Producto, ProductoCreate, ProductoUpdate
from src.config import SERVER_URL, IMAGENES_DIR

# Crear instancia del gestor de catálogos
catalogo_mgr = CatalogoManager()

# Crear las tablas de la BD
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Servidor de Imágenes para Catálogos Dinámicos",
    description="API para servir imágenes y gestionar catálogos mensuales",
    version="2.0.0",
)

# Directorio base de imágenes (ya importado desde config)
Path(IMAGENES_DIR).mkdir(exist_ok=True)


# Clase personalizada para servir PDFs en línea
class InlinePDFResponse(FileResponse):
    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.headers["Content-Disposition"] = "inline"


@app.get("/")
async def root():
    segmentos = catalogo_mgr.obtener_segmentos_disponibles()
    return {
        "message": "Servidor de catálogos dinámicos funcionando",
        "admin": "/admin",
        "docs": "/docs",
        "segmentos_disponibles": segmentos,
        "endpoints": {
            "segmentos": {
                "listar_segmentos": "/api/segmentos",
            },
            "catalogos": {
                "catalogo_activo": "/api/catalogo/{segmento}/activo",
                "catalogo_mes": "/api/catalogo/{segmento}/{año}/{mes}",
                "categorias": "/api/catalogo/{segmento}/{año}/{mes}/{categoria}",
                "meses_disponibles": "/api/meses-disponibles",
            },
            "productos": {
                "listar_todos": "/api/productos",
                "obtener_uno": "/api/productos/{producto_id}",
                "crear": "POST /api/productos",
                "actualizar": "PUT /api/productos/{producto_id}",
                "eliminar": "DELETE /api/productos/{producto_id}",
                "producto_detallado": "/api/catalogo/{segmento}/{año}/{mes}/{categoria}/{producto_id}",
                "obtener_imagen": "/api/imagen/{segmento}/{año}/{mes}/{categoria}/{producto_id}/{tipo_imagen}",
                "nota_tipos_imagen": "tipo_imagen: 'caracteristicas' o 'precios'",
            },
            "imagenes": {
                "por_nombre": "/ver/{nombre_archivo}",
                "por_ruta_catalogos": "/api/catalogos/{ruta_completa}",
                "por_ruta_legacy": "/ver-ruta/{ruta_completa}",
            },
            "pdfs": {
                "pdf_categoria": "/api/pdf/{segmento}/{año}/{mes}/{categoria}",
                "pdfs_mes": "/api/pdfs/{segmento}/{año}/{mes}",
                "pdf_categoria_activo": "/api/pdf/{segmento}/activo/{categoria}",
                "pdfs_mes_activo": "/api/pdfs/{segmento}/activo",
            },
            "admin": {
                "panel": "/api/admin",
                "validar_producto": "POST /api/validar-producto",
            },
            "utilidades": {
                "diagnostico": "/diagnostico",
            },
            "ejemplos": {
                "catalogo_fnb_activo": "/api/catalogo/fnb/activo",
                "catalogo_gaso_noviembre_2025": "/api/catalogo/gaso/2025/11-noviembre",
                "celulares_gaso": "/api/catalogo/gaso/2025/11-noviembre/1-celulares",
                "producto_especifico": "/api/catalogo/fnb/2025/11-noviembre/1-celulares/CELCEL0091",
                "imagen_con_ruta": "/ver-ruta/catalogos/fnb/2025/11-noviembre/1-celulares/caracteristicas/01.png",
            },
        },
    }


@app.get("/api/segmentos")
async def obtener_segmentos():
    """Obtiene lista de segmentos disponibles"""
    try:
        segmentos = catalogo_mgr.obtener_segmentos_disponibles()
        return {
            "segmentos": segmentos,
            "total_segmentos": len(segmentos),
            "descripcion": "Segmentos de negocio disponibles para consultar catálogos",
            "ejemplo_uso": "/api/catalogo/activo?segmento=fnb",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener segmentos: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/activo")
async def obtener_catalogo_activo(segmento: str):
    """Obtiene el catálogo activo de un segmento"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        catalogo = catalogo_mgr.cargar_catalogo_mes(
            catalogo_info["año"], catalogo_info["mes"], segmento
        )

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "productos_por_categoria": {
                cat: len(prods) for cat, prods in catalogo.items()
            },
            "categorias_disponibles": list(catalogo.keys()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener catálogo activo: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/{anio}/{mes}")
async def obtener_catalogo_mes(segmento: str, anio: str, mes: str):
    """Obtiene catálogo de un mes específico de un segmento"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)
        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "catalogo": catalogo,
            "total_productos": sum(len(prods) for prods in catalogo.values()),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Catálogo no encontrado: {str(e)}")


@app.get("/api/catalogo/{segmento}/{anio}/{mes}/{categoria}")
async def obtener_categorias_mes(segmento: str, anio: str, mes: str, categoria: str):
    """Obtiene productos de una categoría específica"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if (
                cat_nombre.upper() == categoria.upper()
                or cat_key.upper() == categoria.upper()
            ):
                categoria_encontrada = cat_nombre
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        productos = catalogo[categoria_encontrada]

        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "categoria": categoria_encontrada,
            "total_productos": len(productos),
            "productos": productos,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Error al obtener categoría: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/{anio}/{mes}/{categoria}/{producto_id}")
async def obtener_producto_detallado(
    segmento: str, anio: str, mes: str, categoria: str, producto_id: str
):
    """Obtiene los detalles completos de un producto"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if (
                cat_nombre.upper() == categoria.upper()
                or cat_key.upper() == categoria.upper()
            ):
                categoria_encontrada = cat_nombre
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        # Buscar el producto
        producto = next(
            (
                p
                for p in catalogo[categoria_encontrada]
                if str(p.get("id")).strip() == str(producto_id).strip()
            ),
            None,
        )

        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{producto_id}' no encontrado",
            )

        # Agregar URLs de acceso directo
        producto_detalle = {
            **producto,
            "urls": {
                "imagen_listado": f"/api/imagen/{segmento}/{anio}/{mes}/{categoria_encontrada}/{producto_id}/listado",
                "imagen_caracteristicas": f"/api/imagen/{segmento}/{anio}/{mes}/{categoria_encontrada}/{producto_id}/caracteristicas",
            },
        }

        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "categoria": categoria_encontrada,
            "producto": producto_detalle,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener producto: {str(e)}"
        )


@app.get("/api/imagen/{segmento}/{anio}/{mes}/{categoria}/{producto_id}/{tipo_imagen}")
async def obtener_imagen_producto(
    segmento: str,
    anio: str,
    mes: str,
    categoria: str,
    producto_id: str,
    tipo_imagen: str,
):
    """Obtiene imagen de un producto (listado o caracteristicas)"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if (
                cat_nombre.upper() == categoria.upper()
                or cat_key.upper() == categoria.upper()
            ):
                categoria_encontrada = cat_nombre
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        # Buscar el producto
        producto = next(
            (
                p
                for p in catalogo[categoria_encontrada]
                if str(p.get("id")).strip() == str(producto_id).strip()
            ),
            None,
        )

        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{producto_id}' no encontrado",
            )

        # Obtener la imagen según tipo
        if tipo_imagen == "listado":
            imagen_path = producto.get("imagen")
        elif tipo_imagen == "caracteristicas":
            imagen_path = producto.get("imagen_caracteristicas")
        else:
            raise HTTPException(
                status_code=400,
                detail="tipo_imagen debe ser 'listado' o 'caracteristicas'",
            )

        if not imagen_path:
            raise HTTPException(
                status_code=404,
                detail=f"Imagen {tipo_imagen} no disponible para este producto",
            )

        ruta_imagen = Path(IMAGENES_DIR) / imagen_path

        if not ruta_imagen.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Imagen no encontrada: {imagen_path}",
            )

        return FileResponse(ruta_imagen, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener imagen: {str(e)}"
        )


@app.post("/api/validar-producto")
async def validar_producto(data: dict):
    """Valida la disponibilidad de un producto"""
    try:
        producto_id = data.get("producto_id")
        categoria = data.get("categoria")

        if not producto_id or not categoria:
            raise HTTPException(
                status_code=400, detail="producto_id y categoria son requeridos"
            )

        resultado = catalogo_mgr.validar_producto(producto_id, categoria)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al validar producto: {str(e)}"
        )


@app.get("/api/meses-disponibles")
async def obtener_meses_disponibles():
    """Obtiene lista de meses con catálogos disponibles"""
    try:
        meses = catalogo_mgr.obtener_meses_disponibles()
        return {"total_meses": len(meses), "meses": meses}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener meses disponibles: {str(e)}"
        )


# Endpoints para servir PDFs existentes
@app.get("/api/pdf/{segmento}/{anio}/{mes}/{categoria}")
async def obtener_pdf_categoria(segmento: str, anio: str, mes: str, categoria: str):
    """Obtiene el PDF de una categoría específica"""
    try:
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(anio, mes, categoria, segmento)

        if not ruta_pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF no encontrado para {categoria} en {mes}/{anio}",
            )

        return InlinePDFResponse(ruta_pdf, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener PDF: {str(e)}")


@app.get("/api/pdfs/{segmento}/{anio}/{mes}")
async def listar_pdfs_mes(segmento: str, anio: str, mes: str):
    """Lista todos los PDFs disponibles en un mes"""
    try:
        pdfs = catalogo_mgr.listar_pdfs_mes(anio, mes, segmento)

        if not pdfs:
            raise HTTPException(
                status_code=404, detail=f"No hay PDFs disponibles para {mes}/{anio}"
            )

        return {
            "segmento": segmento,
            "año": anio,
            "mes": mes,
            "pdfs_disponibles": pdfs,
            "total_pdfs": sum(1 for v in pdfs.values() if v is not None),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar PDFs: {str(e)}")


@app.get("/api/pdf/{segmento}/activo/{categoria}")
async def obtener_pdf_categoria_activa(segmento: str, categoria: str):
    """Obtiene el PDF de una categoría del catálogo activo (mes actual)"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            catalogo_info["año"], catalogo_info["mes"], categoria, segmento
        )

        if not ruta_pdf:
            raise HTTPException(
                status_code=404, detail=f"PDF no encontrado para {categoria}"
            )

        return InlinePDFResponse(ruta_pdf, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener PDF: {str(e)}")


@app.get("/api/pdfs/{segmento}/activo")
async def listar_pdfs_mes_activo(segmento: str):
    """Lista todos los PDFs disponibles del catálogo activo (mes actual)"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        pdfs = catalogo_mgr.listar_pdfs_mes(
            catalogo_info["año"], catalogo_info["mes"], segmento
        )

        if not pdfs:
            raise HTTPException(
                status_code=404, detail="No hay PDFs disponibles en el catálogo activo"
            )

        return {
            "segmento": segmento,
            "año": catalogo_info["año"],
            "mes": catalogo_info["mes"],
            "pdfs_disponibles": pdfs,
            "total_pdfs": sum(1 for v in pdfs.values() if v is not None),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar PDFs: {str(e)}")


@app.get("/ver/{nombre_archivo}")
async def ver_imagen(nombre_archivo: str):
    """Muestra la imagen directamente en el navegador (busca en subdirectorios)"""
    try:
        # Buscar en todos los subdirectorios
        for root, dirs, files in os.walk(IMAGENES_DIR):
            for file in files:
                if file == nombre_archivo:
                    ruta_completa = Path(root) / file
                    if ruta_completa.exists():
                        return FileResponse(ruta_completa)

        raise HTTPException(
            status_code=404, detail=f"Imagen no encontrada: {nombre_archivo}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar imagen: {str(e)}")


@app.get("/ver-ruta/{ruta:path}")
async def ver_imagen_con_ruta(ruta: str):
    """Muestra la imagen usando la ruta completa desde imágenes/"""
    try:
        ruta_imagen = Path(IMAGENES_DIR) / ruta

        if not ruta_imagen.exists():
            raise HTTPException(status_code=404, detail=f"Imagen no encontrada: {ruta}")

        if not ruta_imagen.is_file():
            raise HTTPException(status_code=400, detail="Ruta inválida")

        return FileResponse(ruta_imagen)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar imagen: {str(e)}")


@app.get("/api/catalogos/{ruta:path}")
async def obtener_imagen_catalogo(ruta: str):
    """Obtiene imágenes de catálogos desde /api/catalogos/..."""
    try:
        ruta_imagen = Path(IMAGENES_DIR) / "catalogos" / ruta

        if not ruta_imagen.exists():
            raise HTTPException(status_code=404, detail=f"Imagen no encontrada: {ruta}")

        if not ruta_imagen.is_file():
            raise HTTPException(status_code=400, detail="Ruta inválida")

        return FileResponse(ruta_imagen)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar imagen: {str(e)}")


@app.get("/diagnostico")
async def diagnostico():
    """Endpoint para diagnosticar problemas"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual()
        meses_disponibles = catalogo_mgr.obtener_meses_disponibles()

        diagnostico_info = {
            "servidor": "activo",
            "directorio_actual": os.getcwd(),
            "directorio_imagenes": IMAGENES_DIR,
            "existe_directorio": Path(IMAGENES_DIR).exists(),
            "catalogo_actual": catalogo_info,
            "meses_disponibles": meses_disponibles,
            "estructura_archivos": [],
        }

        if Path(IMAGENES_DIR).exists():
            for root, dirs, files in os.walk(IMAGENES_DIR):
                for file in files:
                    if file.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
                    ):
                        ruta_completa = Path(root) / file
                        ruta_relativa = ruta_completa.relative_to(IMAGENES_DIR)
                        diagnostico_info["estructura_archivos"].append(
                            {
                                "ruta_relativa": str(ruta_relativa),
                                "ruta_completa": str(ruta_completa),
                                "existe": ruta_completa.exists(),
                            }
                        )

        return diagnostico_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")


# Importar y registrar rutas CRUD
from src.crud_routes import router as crud_router

app.include_router(crud_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
