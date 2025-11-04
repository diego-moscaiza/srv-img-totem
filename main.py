from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from typing import List

app = FastAPI(
    title="Servidor de Imágenes",
    description="API para servir imágenes locales",
    version="1.0.0"
)

# Directorio donde se almacenan las imágenes
IMAGENES_DIR = "imagenes"

# Crear el directorio si no existe
Path(IMAGENES_DIR).mkdir(exist_ok=True)

# Montar directorio estático para servir archivos (esto SÍ funciona con subdirectorios)
app.mount("/static", StaticFiles(directory=IMAGENES_DIR), name="static")

# Extensiones permitidas
EXTENSIONES_PERMITIDAS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

def es_imagen_valida(nombre_archivo: str) -> bool:
    """Verifica si el archivo es una imagen válida"""
    return Path(nombre_archivo).suffix.lower() in EXTENSIONES_PERMITIDAS

def buscar_imagen_en_subdirectorios(nombre_archivo: str) -> Path:
    """Busca la imagen en todos los subdirectorios"""
    for root, dirs, files in os.walk(IMAGENES_DIR):
        for file in files:
            if file == nombre_archivo and es_imagen_valida(file):
                return Path(root) / file
    return Path(root)

@app.get("/")
async def root():
    return {
        "message": "Servidor de imágenes funcionando",
        "endpoints": {
            "listar_imagenes": "/imagenes",
            "obtener_imagen": "/imagen/{nombre_archivo}",
            "ver_imagen_en_navegador": "/ver/{nombre_archivo}",
            "acceso_directo_con_ruta": "/static/{ruta_completa}",
            "listar_todas": "/todas-las-imagenes"
        }
    }

@app.get("/imagenes", response_model=List[str])
async def listar_imagenes():
    """Lista todas las imágenes disponibles en la raíz"""
    try:
        archivos = []
        for archivo in os.listdir(IMAGENES_DIR):
            ruta_completa = Path(IMAGENES_DIR) / archivo
            if ruta_completa.is_file() and es_imagen_valida(archivo):
                archivos.append(archivo)
        return archivos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {str(e)}")

@app.get("/todas-las-imagenes")
async def listar_todas_las_imagenes():
    """Lista TODAS las imágenes incluyendo subdirectorios"""
    try:
        archivos = []
        for root, dirs, files in os.walk(IMAGENES_DIR):
            for file in files:
                if es_imagen_valida(file):
                    ruta_relativa = Path(root) / file
                    # Hacer la ruta relativa al directorio IMAGENES_DIR
                    ruta_relativa = ruta_relativa.relative_to(IMAGENES_DIR)
                    archivos.append(str(ruta_relativa))
        return archivos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {str(e)}")

@app.get("/imagen/{nombre_archivo}")
async def obtener_imagen(nombre_archivo: str):
    """Devuelve la imagen como archivo para descargar (busca en subdirectorios)"""
    # Primero buscar en raíz
    ruta_raiz = Path(IMAGENES_DIR) / nombre_archivo
    
    if ruta_raiz.exists() and ruta_raiz.is_file() and es_imagen_valida(nombre_archivo):
        return FileResponse(path=ruta_raiz, filename=nombre_archivo)
    
    # Si no está en raíz, buscar en subdirectorios
    ruta_encontrada = buscar_imagen_en_subdirectorios(nombre_archivo)
    
    if ruta_encontrada and ruta_encontrada.exists():
        return FileResponse(path=ruta_encontrada, filename=nombre_archivo)
    
    raise HTTPException(
        status_code=404, 
        detail=f"Imagen no encontrada: {nombre_archivo}. Usa /todas-las-imagenes para ver las disponibles"
    )

@app.get("/ver/{nombre_archivo}")
async def ver_imagen(nombre_archivo: str):
    """Muestra la imagen directamente en el navegador (busca en subdirectorios)"""
    # Primero buscar en raíz
    ruta_raiz = Path(IMAGENES_DIR) / nombre_archivo
    
    if ruta_raiz.exists() and ruta_raiz.is_file() and es_imagen_valida(nombre_archivo):
        return FileResponse(ruta_raiz)
    
    # Si no está en raíz, buscar en subdirectorios
    ruta_encontrada = buscar_imagen_en_subdirectorios(nombre_archivo)
    
    if ruta_encontrada and ruta_encontrada.exists():
        return FileResponse(ruta_encontrada)
    
    raise HTTPException(
        status_code=404, 
        detail=f"Imagen no encontrada: {nombre_archivo}"
    )

# NUEVO ENDPOINT para acceder con ruta completa
@app.get("/ver-ruta/{ruta:path}")
async def ver_imagen_con_ruta(ruta: str):
    """Muestra la imagen usando la ruta completa desde imágenes/"""
    ruta_imagen = Path(IMAGENES_DIR) / ruta
    
    if not ruta_imagen.exists():
        raise HTTPException(status_code=404, detail=f"Imagen no encontrada: {ruta}")
    
    if not ruta_imagen.is_file():
        raise HTTPException(status_code=400, detail="Ruta inválida")
    
    if not es_imagen_valida(ruta_imagen.name):
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")
    
    return FileResponse(ruta_imagen)

@app.get("/diagnostico")
async def diagnostico():
    """Endpoint para diagnosticar problemas"""
    diagnostico_info = {
        "directorio_actual": os.getcwd(),
        "directorio_imagenes": IMAGENES_DIR,
        "existe_directorio": Path(IMAGENES_DIR).exists(),
        "estructura_completa": []
    }
    
    if Path(IMAGENES_DIR).exists():
        for root, dirs, files in os.walk(IMAGENES_DIR):
            for file in files:
                if es_imagen_valida(file):
                    ruta_completa = Path(root) / file
                    ruta_relativa = ruta_completa.relative_to(IMAGENES_DIR)
                    diagnostico_info["estructura_completa"].append({
                        "ruta_relativa": str(ruta_relativa),
                        "ruta_completa": str(ruta_completa),
                        "existe": ruta_completa.exists()
                    })
    
    return diagnostico_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
