from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from typing import List, Dict
import catalogos_manager

app = FastAPI(
    title="Servidor de Imágenes para Catálogos Dinámicos",
    description="API para servir imágenes y gestionar catálogos mensuales",
    version="2.0.0",
)

# Directorio base de imágenes
IMAGENES_DIR = "imagenes"
Path(IMAGENES_DIR).mkdir(exist_ok=True)

# Clase personalizada para servir PDFs en línea
class InlinePDFResponse(FileResponse):
    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.headers["Content-Disposition"] = "inline"

# Montar directorio estático
app.mount("/static", StaticFiles(directory=IMAGENES_DIR), name="static")

# Instancia del gestor de catálogos
catalogo_mgr = catalogos_manager.catalogo_manager


@app.get("/")
async def root():
    return {
        "message": "Servidor de catálogos dinámicos funcionando",
        "endpoints": {
            "imagenes": {
                "imagen_categoria": "/imagen/{anio}/{mes}/{categoria}/{nombre_imagen}",
                "ver_imagen": "/ver/{nombre_archivo}",
                "ver_con_ruta": "/ver-ruta/{ruta:path}",
                "acceso_directo": "/static/{ruta:path}",
            },
            "catalogos": {
                "catalogo_activo": "/api/catalogo/activo",
                "catalogo_mes": "/api/catalogos/{año}/{mes}",
                "categorias": "/api/categorias/{año}/{mes}",
                "validar_producto": "/api/validar-producto",
                "meses_disponibles": "/api/meses-disponibles",
            },
            "productos": {
                "producto_detallado": "/api/producto/{año}/{mes}/{categoria}/{producto_id}",
                "imagen_caracteristicas": "/api/producto/caracteristicas/{año}/{mes}/{categoria}/{producto_id}",
                "imagen_productos": "/api/producto/listado/{año}/{mes}/{categoria}/{producto_id}",
            },
            "pdfs": {
                "pdf_categoria": "/api/pdf/{año}/{mes}/{categoria}",
                "pdfs_mes": "/api/pdfs/{año}/{mes}",
                "pdf_categoria_activo": "/api/pdf/activo/{categoria}",
                "pdfs_mes_activo": "/api/pdfs/activo",
            },
        },
    }


@app.get("/api/catalogo/activo")
async def obtener_catalogo_activo():
    """Obtiene el catálogo del mes actual"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual()
        catalogo = catalogo_mgr.cargar_catalogo_mes(
            catalogo_info["año"], catalogo_info["mes"]
        )

        return {
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


@app.get("/api/catalogos/{anio}/{mes}")
async def obtener_catalogo_mes(anio: str, mes: str):
    """Obtiene catálogo de un mes específico"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes)
        return {
            "anio": anio,
            "mes": mes,
            "catalogo": catalogo,
            "total_productos": sum(len(prods) for prods in catalogo.values()),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Catálogo no encontrado: {str(e)}")


@app.get("/api/categorias/{anio}/{mes}")
async def obtener_categorias_mes(anio: str, mes: str):
    """Obtiene categorías disponibles en un mes"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes)

        categorias = []
        for categoria, productos in catalogo.items():
            categorias.append(
                {
                    "nombre": categoria,
                    "total_productos": len(productos),
                    "productos": [
                        {"id": p["id"], "nombre": p["nombre"]} for p in productos
                    ],
                }
            )

        return categorias
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Error al obtener categorías: {str(e)}"
        )


@app.get("/api/producto/{anio}/{mes}/{categoria}/{producto_id}")
async def obtener_producto_detallado(anio: str, mes: str, categoria: str, producto_id: str):
    """Obtiene los detalles completos de un producto incluyendo imágenes"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes)
        
        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if cat_nombre.upper() == categoria.upper() or cat_key.upper() == categoria.upper():
                categoria_encontrada = cat_nombre
                break
        
        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404,
                detail=f"Categoría '{categoria}' no encontrada"
            )
        
        # Buscar el producto
        producto = next(
            (p for p in catalogo[categoria_encontrada] if str(p.get("id")).strip() == str(producto_id).strip()),
            None
        )
        
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{producto_id}' no encontrado en {categoria}"
            )
        
        # Agregar URLs de acceso directo a las imágenes
        producto_detalle = {
            **producto,
            "urls": {
                "imagen_listado": f"/api/producto/listado/{anio}/{mes}/{categoria_encontrada}/{producto_id}",
                "imagen_caracteristicas": f"/api/producto/caracteristicas/{anio}/{mes}/{categoria_encontrada}/{producto_id}",
                "imagen_directa": f"/static/{producto.get('imagen', '')}",
                "caracteristicas_directa": f"/static/{producto.get('imagen_caracteristicas', '')}"
            }
        }
        
        return {
            "año": anio,
            "mes": mes,
            "categoria": categoria_encontrada,
            "producto": producto_detalle
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener producto: {str(e)}"
        )


@app.get("/api/producto/caracteristicas/{anio}/{mes}/{categoria}/{producto_id}")
async def obtener_imagen_caracteristicas(anio: str, mes: str, categoria: str, producto_id: str):
    """Obtiene la imagen de características de un producto específico"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes)
        
        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if cat_nombre.upper() == categoria.upper() or cat_key.upper() == categoria.upper():
                categoria_encontrada = cat_nombre
                break
        
        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404,
                detail=f"Categoría '{categoria}' no encontrada"
            )
        
        # Buscar el producto
        producto = next(
            (p for p in catalogo[categoria_encontrada] if str(p.get("id")).strip() == str(producto_id).strip()),
            None
        )
        
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{producto_id}' no encontrado en {categoria}"
            )
        
        # Obtener ruta de imagen de características
        imagen_caracteristicas = producto.get("imagen_caracteristicas")
        
        if not imagen_caracteristicas:
            raise HTTPException(
                status_code=404,
                detail=f"El producto '{producto_id}' no tiene imagen de características"
            )
        
        # Construir ruta completa
        ruta_imagen = Path(IMAGENES_DIR) / imagen_caracteristicas
        
        if not ruta_imagen.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Imagen de características no encontrada: {imagen_caracteristicas}"
            )
        
        return FileResponse(
            ruta_imagen,
            media_type="image/png"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener imagen de características: {str(e)}"
        )


@app.get("/api/producto/listado/{anio}/{mes}/{categoria}/{producto_id}")
async def obtener_imagen_listado(anio: str, mes: str, categoria: str, producto_id: str):
    """Obtiene la imagen de lista (producto) de un producto específico"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes)
        
        # Buscar la categoría
        categoria_encontrada = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if cat_nombre.upper() == categoria.upper() or cat_key.upper() == categoria.upper():
                categoria_encontrada = cat_nombre
                break
        
        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404,
                detail=f"Categoría '{categoria}' no encontrada"
            )
        
        # Buscar el producto
        producto = next(
            (p for p in catalogo[categoria_encontrada] if str(p.get("id")).strip() == str(producto_id).strip()),
            None
        )
        
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto '{producto_id}' no encontrado en {categoria}"
            )
        
        # Obtener ruta de imagen de lista
        imagen_listado = producto.get("imagen")
        
        if not imagen_listado:
            raise HTTPException(
                status_code=404,
                detail=f"El producto '{producto_id}' no tiene imagen de lista"
            )
        
        # Construir ruta completa
        ruta_imagen = Path(IMAGENES_DIR) / imagen_listado
        
        if not ruta_imagen.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Imagen de lista no encontrada: {imagen_listado}"
            )
        
        return FileResponse(
            ruta_imagen,
            media_type="image/png"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener imagen de lista: {str(e)}"
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
@app.get("/api/pdf/{anio}/{mes}/{categoria}")
async def obtener_pdf_categoria(anio: str, mes: str, categoria: str):
    """Obtiene el PDF de una categoría específica"""
    try:
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(anio, mes, categoria)
        
        if not ruta_pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF no encontrado para {categoria} en {mes}/{anio}"
            )
        
        return InlinePDFResponse(
            ruta_pdf,
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener PDF: {str(e)}"
        )


@app.get("/api/pdfs/{anio}/{mes}")
async def listar_pdfs_mes(anio: str, mes: str):
    """Lista todos los PDFs disponibles en un mes"""
    try:
        pdfs = catalogo_mgr.listar_pdfs_mes(anio, mes)
        
        if not pdfs:
            raise HTTPException(
                status_code=404,
                detail=f"No hay PDFs disponibles para {mes}/{anio}"
            )
        
        return {
            "año": anio,
            "mes": mes,
            "pdfs_disponibles": pdfs,
            "total_pdfs": sum(1 for v in pdfs.values() if v is not None)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar PDFs: {str(e)}"
        )


@app.get("/api/pdf/activo/{categoria}")
async def obtener_pdf_categoria_activa(categoria: str):
    """Obtiene el PDF de una categoría del catálogo activo (mes actual)"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual()
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            catalogo_info["año"],
            catalogo_info["mes"],
            categoria
        )
        
        if not ruta_pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF no encontrado para {categoria}"
            )
        
        return InlinePDFResponse(
            ruta_pdf,
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener PDF: {str(e)}"
        )


@app.get("/api/pdfs/activo")
async def listar_pdfs_mes_activo():
    """Lista todos los PDFs disponibles del catálogo activo (mes actual)"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual()
        pdfs = catalogo_mgr.listar_pdfs_mes(
            catalogo_info["año"],
            catalogo_info["mes"]
        )
        
        if not pdfs:
            raise HTTPException(
                status_code=404,
                detail="No hay PDFs disponibles en el catálogo activo"
            )
        
        return {
            "año": catalogo_info["año"],
            "mes": catalogo_info["mes"],
            "pdfs_disponibles": pdfs,
            "total_pdfs": sum(1 for v in pdfs.values() if v is not None)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar PDFs: {str(e)}"
        )

@app.get("/imagen/{anio}/{mes}/{categoria}/{nombre_imagen}")
async def obtener_imagen_categoria(anio: str, mes: str, categoria: str, nombre_imagen: str):
    """Obtiene una imagen específica de una categoría"""
    try:
        # Mapear nombre de categoría a carpeta
        categoria_upper = categoria.upper()
        nombre_carpeta = None
        for carpeta_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if cat_nombre == categoria_upper or carpeta_key.upper() == categoria_upper:
                nombre_carpeta = carpeta_key
                break
        
        if not nombre_carpeta:
            raise HTTPException(
                status_code=404,
                detail=f"Categoría '{categoria}' no encontrada"
            )
        
        # Construir ruta: imagenes/catalogos/{anio}/fnb/{mes}/{categoria}/listado o caracteristicas
        # Detectar si es producto o característica por el nombre de la carpeta
        rutas_posibles = [
            Path(IMAGENES_DIR) / anio / "fnb" / mes / nombre_carpeta / "listado" / nombre_imagen,
            Path(IMAGENES_DIR) / anio / "fnb" / mes / nombre_carpeta / "caracteristicas" / nombre_imagen,
        ]
        
        for ruta_imagen in rutas_posibles:
            if ruta_imagen.exists():
                return FileResponse(ruta_imagen, media_type="image/png")
        
        raise HTTPException(
            status_code=404, 
            detail=f"Imagen no encontrada: {nombre_imagen}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener imagen: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
