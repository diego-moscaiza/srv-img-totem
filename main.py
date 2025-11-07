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


# Endpoints para servir imágenes (versión mejorada)
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
