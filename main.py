from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import urllib.parse
from pathlib import Path
from typing import List, Dict
from src.catalogos_manager import catalogo_manager as catalogo_mgr
from src.database import Producto as DBProducto, SessionLocal, engine
from src.database import Base
from src.schemas import Producto, ProductoCreate, ProductoUpdate
from src.config import SERVER_URL, SERVER_URL_EXTERNAL, IMAGENES_DIR

print(f"[DEBUG] SERVER_URL_EXTERNAL={SERVER_URL_EXTERNAL}")

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
    """Endpoint raíz con información del sistema de catálogos"""
    try:
        segmentos = catalogo_mgr.obtener_segmentos_disponibles()
        meses_disponibles = catalogo_mgr.obtener_meses_disponibles()

        # Construir información de catálogos disponibles en el sistema de archivos
        catalogos_disponibles = {}
        for segmento in segmentos:
            ruta_segmento = Path(IMAGENES_DIR) / "catalogos" / segmento / "2025"
            if ruta_segmento.exists():
                meses = [d.name for d in ruta_segmento.iterdir() if d.is_dir()]
                catalogos_disponibles[segmento] = meses

        return {
            "servidor": {
                "nombre": "Servidor de Catálogos Dinámicos",
                "version": "2.1.0",
                "estado": "activo",
            },
            "datos_disponibles": {
                "segmentos": segmentos,
                "catalogos_por_segmento": catalogos_disponibles,
                "productos_en_bd": meses_disponibles,
            },
            "navegacion": {
                "documentacion": "/docs",
                "admin": "/admin",
                "diagnostico": "/diagnostico",
            },
            "endpoints": {
                "catalogos": {
                    "activo": "/api/catalogo/{segmento}/activo",
                    "activo_disponibles": "/api/catalogo/{segmento}/mes-actual/disponibles",
                    "activo_categoria": "/api/catalogo/{segmento}/mes-actual/{categoria}",
                    "activo_categoria_disponibles": "/api/catalogo/{segmento}/mes-actual/{categoria}/disponibles",
                    "por_mes": "/api/catalogo/{segmento}/{año}/{mes}",
                    "por_mes_disponibles": "/api/catalogo/{segmento}/{año}/{mes}/disponibles",
                    "categoria": "/api/catalogo/{segmento}/{año}/{mes}/{categoria}",
                    "categoria_disponibles": "/api/catalogo/{segmento}/{año}/{mes}/{categoria}/disponibles",
                    "producto": "/api/catalogo/{segmento}/{año}/{mes}/{categoria}/{producto_id}",
                },
                "recursos": {
                    "imagen": "/api/catalogos/{ruta_completa}",
                    "pdf": "/api/ver-pdf/{ruta_completa}",
                    "catalogo_pdf": "/api/catalogo-completo/{segmento}/activo",
                },
                "consultas": {
                    "segmentos": "/api/segmentos",
                    "meses": "/api/meses-disponibles",
                },
            },
            "ejemplos": {
                "fnb": {
                    "catalogo": "/api/catalogo/fnb/activo",
                    "celulares": "/api/catalogo/fnb/2025/12-diciembre/celulares",
                    "imagen": "/api/catalogos/fnb/2025/12-diciembre/1-celulares/precios/01.png",
                    "pdf": "/api/catalogo-completo/fnb/activo",
                },
                "gaso": {
                    "catalogo": "/api/catalogo/gaso/activo",
                    "celulares": "/api/catalogo/gaso/2025/12-diciembre/celulares",
                    "imagen": "/api/catalogos/gaso/2025/12-diciembre/1-celulares/precios/01.png",
                    "pdf": "/api/catalogo-completo/gaso/activo",
                },
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al cargar información: {str(e)}"
        )


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


@app.get("/api/imagenes-disponibles")
async def obtener_imagenes_disponibles(
    segmento: str | None = None,
    ano: int | None = None,
    mes: str | None = None,
    categoria: str | None = None,
):
    """Obtiene lista de imágenes disponibles, opcionalmente filtradas por segmento, año, mes y categoría"""
    try:
        imagenes_disponibles = {"listado": {}, "caracteristicas": {}}

        imagenes_dir = Path(IMAGENES_DIR) / "catalogos"

        if not imagenes_dir.exists():
            return imagenes_disponibles

        # Normalizar parámetros de entrada
        segmento_filtro = (
            segmento.strip().lower() if segmento and segmento.strip() else None
        )
        ano_filtro = int(ano) if ano else None
        mes_filtro = mes.strip().lower() if mes and mes.strip() else None
        categoria_filtro = (
            categoria.strip().lower() if categoria and categoria.strip() else None
        )

        # Recorrer estructura: catalogos/segmento/año/mes/categoría/tipo_imagen
        for segmento_dir in imagenes_dir.iterdir():
            if not segmento_dir.is_dir():
                continue

            segmento_actual = segmento_dir.name.lower()

            # Si se especifica segmento, filtrar exactamente
            if segmento_filtro and segmento_actual != segmento_filtro:
                continue

            for ano_dir in segmento_dir.iterdir():
                if not ano_dir.is_dir():
                    continue

                try:
                    ano_actual = int(ano_dir.name)
                except ValueError:
                    continue

                # Si se especifica año, filtrar exactamente
                if ano_filtro and ano_actual != ano_filtro:
                    continue

                for mes_dir in ano_dir.iterdir():
                    if not mes_dir.is_dir():
                        continue

                    mes_actual = mes_dir.name.lower()

                    # Si se especifica mes, verificar que esté en el nombre de la carpeta
                    # Ej: mes="noviembre" debe coincidir con "11-noviembre"
                    if mes_filtro:
                        # Extraer el nombre del mes de la carpeta (ej: "noviembre" de "11-noviembre")
                        mes_nombre = (
                            "-".join(mes_actual.split("-")[1:])
                            if "-" in mes_actual
                            else mes_actual
                        )
                        if mes_nombre != mes_filtro:
                            continue

                    for categoria_dir in mes_dir.iterdir():
                        if not categoria_dir.is_dir():
                            continue

                        categoria_actual = categoria_dir.name.lower()

                        # Si se especifica categoría, filtrar exactamente
                        if categoria_filtro and not categoria_actual.endswith(
                            categoria_filtro
                        ):
                            continue

                        # Buscar carpeta "precios" (listado)
                        precios_dir = categoria_dir / "precios"
                        if precios_dir.exists():
                            # Buscar todas las extensiones de imagen soportadas (case-insensitive)
                            # Usar set() para evitar duplicados en Windows
                            imagenes_listado = set(
                                list(precios_dir.glob("*.png"))
                                + list(precios_dir.glob("*.jpg"))
                                + list(precios_dir.glob("*.jpeg"))
                                + list(precios_dir.glob("*.gif"))
                                + list(precios_dir.glob("*.webp"))
                            )
                            for img in sorted(imagenes_listado):
                                ruta_relativa = img.relative_to(imagenes_dir)
                                ruta_relativa_str = str(ruta_relativa).replace(
                                    "\\", "/"
                                )
                                # Construir URL completa
                                url_completa = f"{SERVER_URL_EXTERNAL}/api/catalogos/{ruta_relativa_str}"
                                key = f"{segmento_dir.name}/{ano_dir.name}/{mes_dir.name}/{categoria_dir.name}"
                                if key not in imagenes_disponibles["listado"]:
                                    imagenes_disponibles["listado"][key] = []
                                imagenes_disponibles["listado"][key].append(
                                    {
                                        "ruta": ruta_relativa_str,
                                        "url": url_completa,
                                        "nombre": img.name,
                                    }
                                )

                        # Buscar carpeta "caracteristicas"
                        caracteristicas_dir = categoria_dir / "caracteristicas"
                        if caracteristicas_dir.exists():
                            # Buscar todas las extensiones de imagen soportadas (case-insensitive)
                            # Usar set() para evitar duplicados en Windows
                            imagenes_caracteristicas = set(
                                list(caracteristicas_dir.glob("*.png"))
                                + list(caracteristicas_dir.glob("*.jpg"))
                                + list(caracteristicas_dir.glob("*.jpeg"))
                                + list(caracteristicas_dir.glob("*.gif"))
                                + list(caracteristicas_dir.glob("*.webp"))
                            )
                            for img in sorted(imagenes_caracteristicas):
                                ruta_relativa = img.relative_to(imagenes_dir)
                                ruta_relativa_str = str(ruta_relativa).replace(
                                    "\\", "/"
                                )
                                # Construir URL completa
                                url_completa = f"{SERVER_URL_EXTERNAL}/api/catalogos/{ruta_relativa_str}"
                                key = f"{segmento_dir.name}/{ano_dir.name}/{mes_dir.name}/{categoria_dir.name}"
                                if key not in imagenes_disponibles["caracteristicas"]:
                                    imagenes_disponibles["caracteristicas"][key] = []
                                imagenes_disponibles["caracteristicas"][key].append(
                                    {
                                        "ruta": ruta_relativa_str,
                                        "url": url_completa,
                                        "nombre": img.name,
                                    }
                                )

        return imagenes_disponibles
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener imágenes: {str(e)}"
        )


@app.get("/api/imagenes-base64")
async def obtener_imagenes_base64(
    segmento: str | None = None,
    ano: int | None = None,
    mes: str | None = None,
    categoria: str | None = None,
    tipo: str = "listado",  # "listado" o "caracteristicas"
):
    """
    Obtiene imágenes en base64, opcionalmente filtradas por segmento, año, mes y categoría.
    Parámetro 'tipo' puede ser 'listado' o 'caracteristicas' para especificar carpeta.
    """
    import base64
    import mimetypes

    try:
        imagenes_base64 = {"imagenes": []}

        imagenes_dir = Path(IMAGENES_DIR) / "catalogos"

        if not imagenes_dir.exists():
            return imagenes_base64

        # Normalizar parámetros de entrada
        segmento_filtro = (
            segmento.strip().lower() if segmento and segmento.strip() else None
        )
        ano_filtro = int(ano) if ano else None
        mes_filtro = mes.strip().lower() if mes and mes.strip() else None
        categoria_filtro = (
            categoria.strip().lower() if categoria and categoria.strip() else None
        )
        tipo_filtro = tipo.strip().lower()

        FORMATOS_PERMITIDOS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

        # Recorrer estructura: catalogos/segmento/año/mes/categoría/tipo_imagen
        for segmento_dir in imagenes_dir.iterdir():
            if not segmento_dir.is_dir():
                continue

            segmento_actual = segmento_dir.name.lower()

            # Si se especifica segmento, filtrar exactamente
            if segmento_filtro and segmento_actual != segmento_filtro:
                continue

            for ano_dir in segmento_dir.iterdir():
                if not ano_dir.is_dir():
                    continue

                try:
                    ano_actual = int(ano_dir.name)
                except ValueError:
                    continue

                # Si se especifica año, filtrar exactamente
                if ano_filtro and ano_actual != ano_filtro:
                    continue

                for mes_dir in ano_dir.iterdir():
                    if not mes_dir.is_dir():
                        continue

                    mes_actual = mes_dir.name.lower()

                    # Si se especifica mes, verificar que esté en el nombre de la carpeta
                    if mes_filtro:
                        mes_nombre = (
                            "-".join(mes_actual.split("-")[1:])
                            if "-" in mes_actual
                            else mes_actual
                        )
                        if mes_nombre != mes_filtro:
                            continue

                    for categoria_dir in mes_dir.iterdir():
                        if not categoria_dir.is_dir():
                            continue

                        categoria_actual = categoria_dir.name.lower()

                        # Si se especifica categoría, filtrar exactamente
                        if categoria_filtro and not categoria_actual.endswith(
                            categoria_filtro
                        ):
                            continue

                        # Buscar carpeta especificada (precios o caracteristicas)
                        tipos_buscar = []
                        if tipo_filtro == "listado":
                            tipos_buscar = ["precios"]
                        elif tipo_filtro == "caracteristicas":
                            tipos_buscar = ["caracteristicas"]
                        else:
                            tipos_buscar = ["precios", "caracteristicas"]

                        for tipo_dir in tipos_buscar:
                            tipo_path = categoria_dir / tipo_dir
                            if not tipo_path.exists():
                                continue

                            # Buscar todas las extensiones de imagen soportadas
                            imagenes_encontradas = set(
                                list(tipo_path.glob("*.png"))
                                + list(tipo_path.glob("*.jpg"))
                                + list(tipo_path.glob("*.jpeg"))
                                + list(tipo_path.glob("*.gif"))
                                + list(tipo_path.glob("*.webp"))
                            )

                            for img in sorted(imagenes_encontradas):
                                try:
                                    ruta_relativa = img.relative_to(imagenes_dir)
                                    ruta_relativa_str = str(ruta_relativa).replace(
                                        "\\", "/"
                                    )

                                    # Leer imagen y convertir a base64
                                    with open(img, "rb") as f:
                                        contenido_base64 = base64.b64encode(
                                            f.read()
                                        ).decode("utf-8")

                                    mime_type = (
                                        mimetypes.guess_type(img)[0] or "image/*"
                                    )
                                    tamaño_bytes = img.stat().st_size
                                    tamaño_kb = round(tamaño_bytes / 1024, 2)

                                    imagenes_base64["imagenes"].append(
                                        {
                                            "nombre": img.name,
                                            "ruta": ruta_relativa_str,
                                            "url": f"{SERVER_URL_EXTERNAL}/api/catalogos/{ruta_relativa_str}",
                                            "url_base64_endpoint": f"/api/imagen-base64/{ruta_relativa_str}",
                                            "segmento": segmento_dir.name,
                                            "año": ano_dir.name,
                                            "mes": mes_dir.name,
                                            "categoria": categoria_dir.name,
                                            "tipo": tipo_dir,
                                            "base64": contenido_base64,
                                            "mime_type": mime_type,
                                            "tamaño_bytes": tamaño_bytes,
                                            "tamaño_kb": tamaño_kb,
                                        }
                                    )
                                except Exception as img_error:
                                    print(
                                        f"[WARN] Error procesando imagen {img.name}: {str(img_error)}"
                                    )
                                    continue

        return {
            "total_imagenes": len(imagenes_base64["imagenes"]),
            "filtros_aplicados": {
                "segmento": segmento_filtro,
                "año": ano_filtro,
                "mes": mes_filtro,
                "categoria": categoria_filtro,
                "tipo": tipo_filtro,
            },
            **imagenes_base64,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener imágenes en base64: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/mes-actual/disponibles")
async def obtener_productos_disponibles_mes_actual(segmento: str):
    """Obtiene SOLO los productos disponibles del mes actual (filtra por estado='disponible')"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        anio = catalogo_info["año"]
        mes = catalogo_info["mes"]
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Construir catálogo FILTRADO con solo productos disponibles
        catalogo_con_pdfs = {}
        for categoria_nombre, productos in catalogo.items():
            # Filtrar solo productos con estado='disponible'
            productos_disponibles = [
                p for p in productos if p.get("estado") == "disponible"
            ]

            if not productos_disponibles:
                continue  # Saltar categoría si no tiene productos disponibles

            # Buscar la carpeta correspondiente a esta categoría
            categoria_carpeta = None
            for cat_key, cat_nom in catalogo_mgr.categoria_map.items():
                if cat_nom == categoria_nombre:
                    categoria_carpeta = cat_key
                    break

            # Obtener PDF de la categoría
            pdf_info = None
            if categoria_carpeta:
                ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
                    anio, mes, categoria_carpeta, segmento
                )
                if ruta_pdf and ruta_pdf.exists():
                    ruta_relativa = ruta_pdf.relative_to(
                        Path(IMAGENES_DIR) / "catalogos"
                    )
                    ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
                    url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
                    url_base64_pdf = f"/api/pdf-base64/{ruta_relativa_str}"
                    pdf_info = {
                        "nombre": ruta_pdf.name,
                        "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                        "url_relativa": url_relativa_pdf,
                        "url_base64": url_base64_pdf,
                        "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
                    }

            catalogo_con_pdfs[categoria_nombre] = {
                "pdf": pdf_info,
                "total_productos": len(productos_disponibles),
                "productos": productos_disponibles,
            }

        # Obtener catálogo completo PDF
        catalogo_completo_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(
            anio, mes, segmento
        )
        catalogo_completo_info = None
        if catalogo_completo_pdf and catalogo_completo_pdf.exists():
            url_relativa_completo = f"/api/catalogo-completo/{segmento}/{anio}/{mes}"
            ruta_rel_completo = catalogo_completo_pdf.relative_to(
                Path(IMAGENES_DIR) / "catalogos"
            )
            url_base64_completo = (
                f"/api/pdf-base64/{str(ruta_rel_completo).replace(chr(92), '/')}"
            )
            catalogo_completo_info = {
                "nombre": catalogo_completo_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_completo}",
                "url_base64": url_base64_completo,
                "tamaño_mb": round(
                    catalogo_completo_pdf.stat().st_size / (1024 * 1024), 2
                ),
            }

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "catalogo_completo_pdf": catalogo_completo_info,
            "categorias": catalogo_con_pdfs,
            "total_categorias": len(catalogo_con_pdfs),
            "total_productos_disponibles": sum(
                len(v.get("productos", [])) for v in catalogo_con_pdfs.values()
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener productos disponibles: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/mes-actual/{categoria}")
async def obtener_categoria_activa(segmento: str, categoria: str):
    """Obtiene productos de una categoría específica del catálogo activo"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        anio = catalogo_info["año"]
        mes = catalogo_info["mes"]
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría usando el mapa específico del segmento
        categoria_encontrada = None
        categoria_carpeta = None
        segmento_obj = catalogo_mgr.obtener_segmento(segmento)
        for cat_key, cat_nombre in segmento_obj.categoria_map.items():
            if (
                cat_nombre.lower() == categoria.lower()
                or cat_key.lower() == categoria.lower()
                or categoria.lower() in cat_key.lower()
            ):
                categoria_encontrada = cat_nombre
                categoria_carpeta = cat_key
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        productos = catalogo[categoria_encontrada]

        # Obtener PDF de la categoría
        pdf_info = None
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            anio, mes, categoria_carpeta or categoria, segmento
        )

        if ruta_pdf and ruta_pdf.exists():
            ruta_relativa = ruta_pdf.relative_to(Path(IMAGENES_DIR) / "catalogos")
            ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
            url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
            url_base64_pdf = f"/api/pdf-base64/{ruta_relativa_str}"
            pdf_info = {
                "nombre": ruta_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                "url_relativa": url_relativa_pdf,
                "url_base64": url_base64_pdf,
                "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
            }
        else:
            pdf_info = {
                "nombre": None,
                "url": None,
                "url_relativa": None,
                "url_base64": None,
                "mensaje": f"No hay PDF disponible para {categoria_encontrada}",
            }

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "categoria": categoria_encontrada,
            "total_productos": len(productos),
            "pdf": pdf_info,
            "productos": productos,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener categoría activa: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/mes-actual/{categoria}/disponibles")
async def obtener_categoria_disponibles_mes_actual(segmento: str, categoria: str):
    """Obtiene SOLO los productos disponibles de una categoría específica del mes actual"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        anio = catalogo_info["año"]
        mes = catalogo_info["mes"]
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría usando el mapa específico del segmento
        categoria_encontrada = None
        categoria_carpeta = None
        segmento_obj = catalogo_mgr.obtener_segmento(segmento)
        for cat_key, cat_nombre in segmento_obj.categoria_map.items():
            if (
                cat_nombre.lower() == categoria.lower()
                or cat_key.lower() == categoria.lower()
                or categoria.lower() in cat_key.lower()
            ):
                categoria_encontrada = cat_nombre
                categoria_carpeta = cat_key
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        # Filtrar solo productos disponibles
        productos = catalogo[categoria_encontrada]
        productos_disponibles = [
            p for p in productos if p.get("estado") == "disponible"
        ]

        # Obtener PDF de la categoría
        pdf_info = None
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            anio, mes, categoria_carpeta or categoria, segmento
        )

        if ruta_pdf and ruta_pdf.exists():
            ruta_relativa = ruta_pdf.relative_to(Path(IMAGENES_DIR) / "catalogos")
            ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
            url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
            url_base64_pdf = f"/api/pdf-base64/{ruta_relativa_str}"
            pdf_info = {
                "nombre": ruta_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                "url_relativa": url_relativa_pdf,
                "url_base64": url_base64_pdf,
                "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
            }
        else:
            pdf_info = {
                "nombre": None,
                "url": None,
                "url_relativa": None,
                "url_base64": None,
                "mensaje": f"No hay PDF disponible para {categoria_encontrada}",
            }

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "categoria": categoria_encontrada,
            "total_productos": len(productos_disponibles),
            "pdf": pdf_info,
            "productos": productos_disponibles,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener categoría disponible: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/mes-actual")
async def obtener_catalogo_activo(segmento: str):
    """Obtiene el catálogo activo de un segmento con productos y PDFs"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        anio = catalogo_info["año"]
        mes = catalogo_info["mes"]
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Construir catálogo con PDFs incluidos por cada categoría
        catalogo_con_pdfs = {}
        for categoria_nombre, productos in catalogo.items():
            # Buscar la carpeta correspondiente a esta categoría
            categoria_carpeta = None
            for cat_key, cat_nom in catalogo_mgr.categoria_map.items():
                if cat_nom == categoria_nombre:
                    categoria_carpeta = cat_key
                    break

            # Obtener PDF de la categoría
            pdf_info = None
            if categoria_carpeta:
                ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
                    anio, mes, categoria_carpeta, segmento
                )
                if ruta_pdf and ruta_pdf.exists():
                    ruta_relativa = ruta_pdf.relative_to(
                        Path(IMAGENES_DIR) / "catalogos"
                    )
                    ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
                    url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
                    url_base64_pdf = f"/api/pdf-base64/{ruta_relativa_str}"
                    pdf_info = {
                        "nombre": ruta_pdf.name,
                        "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                        "url_relativa": url_relativa_pdf,
                        "url_base64": url_base64_pdf,
                        "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
                    }

            catalogo_con_pdfs[categoria_nombre] = {
                "pdf": pdf_info,
                "total_productos": len(productos),
                "productos": productos,
            }

        # Obtener catálogo completo PDF
        catalogo_completo_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(
            anio, mes, segmento
        )
        catalogo_completo_info = None
        if catalogo_completo_pdf and catalogo_completo_pdf.exists():
            url_relativa_completo = f"/api/catalogo-completo/{segmento}/{anio}/{mes}"
            # Para base64 del catálogo completo, usar la ruta del archivo
            ruta_rel_completo = catalogo_completo_pdf.relative_to(
                Path(IMAGENES_DIR) / "catalogos"
            )
            url_base64_completo = (
                f"/api/pdf-base64/{str(ruta_rel_completo).replace(chr(92), '/')}"
            )
            catalogo_completo_info = {
                "nombre": catalogo_completo_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_completo}",
                "url_relativa": url_relativa_completo,
                "url_base64": url_base64_completo,
                "tamaño_mb": round(
                    catalogo_completo_pdf.stat().st_size / (1024 * 1024), 2
                ),
            }

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "catalogo_completo_pdf": catalogo_completo_info,
            "categorias": catalogo_con_pdfs,
            "total_categorias": len(catalogo_con_pdfs),
            "total_productos": sum(len(prods) for prods in catalogo.values()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener catálogo activo: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/mes-actual/productos-disponibles")
async def obtener_productos_disponibles(segmento: str):
    """Obtiene solo los productos disponibles del mes actual (estado='disponible')"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        anio = catalogo_info["año"]
        mes = catalogo_info["mes"]
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Construir catálogo FILTRADO con solo productos disponibles
        catalogo_con_pdfs = {}
        for categoria_nombre, productos in catalogo.items():
            # Filtrar solo productos con estado='disponible'
            productos_disponibles = [
                p for p in productos if p.get("estado") == "disponible"
            ]

            if not productos_disponibles:
                continue  # Saltar categoría si no tiene productos disponibles

            # Buscar la carpeta correspondiente a esta categoría
            categoria_carpeta = None
            for cat_key, cat_nom in catalogo_mgr.categoria_map.items():
                if cat_nom == categoria_nombre:
                    categoria_carpeta = cat_key
                    break

            # Obtener PDF de la categoría
            pdf_info = None
            if categoria_carpeta:
                ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
                    anio, mes, categoria_carpeta, segmento
                )
                if ruta_pdf and ruta_pdf.exists():
                    ruta_relativa = ruta_pdf.relative_to(
                        Path(IMAGENES_DIR) / "catalogos"
                    )
                    ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
                    url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
                    url_base64_pdf = f"/api/pdf-base64/{ruta_relativa_str}"
                    pdf_info = {
                        "nombre": ruta_pdf.name,
                        "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                        "url_relativa": url_relativa_pdf,
                        "url_base64": url_base64_pdf,
                        "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
                    }

            catalogo_con_pdfs[categoria_nombre] = {
                "pdf": pdf_info,
                "total_productos": len(productos_disponibles),
                "productos": productos_disponibles,
            }

        # Obtener catálogo completo PDF
        catalogo_completo_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(
            anio, mes, segmento
        )
        catalogo_completo_info = None
        if catalogo_completo_pdf and catalogo_completo_pdf.exists():
            url_relativa_completo = f"/api/catalogo-completo/{segmento}/{anio}/{mes}"
            ruta_rel_completo = catalogo_completo_pdf.relative_to(
                Path(IMAGENES_DIR) / "catalogos"
            )
            url_base64_completo = (
                f"/api/pdf-base64/{str(ruta_rel_completo).replace(chr(92), '/')}"
            )
            catalogo_completo_info = {
                "nombre": catalogo_completo_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_completo}",
                "url_base64": url_base64_completo,
                "tamaño_mb": round(
                    catalogo_completo_pdf.stat().st_size / (1024 * 1024), 2
                ),
            }

        return {
            "segmento": segmento,
            "catalogo_info": catalogo_info,
            "catalogo_completo_pdf": catalogo_completo_info,
            "categorias": catalogo_con_pdfs,
            "total_categorias": len(catalogo_con_pdfs),
            "total_productos": sum(len(prods) for prods in catalogo.values() if prods),
            "productos_disponibles": sum(
                len(v.get("productos", [])) for v in catalogo_con_pdfs.values()
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener productos disponibles: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/{anio}/{mes}/disponibles")
async def obtener_catalogo_disponibles_mes(segmento: str, anio: str, mes: str):
    """Obtiene catálogo de un mes específico mostrando SOLO los productos disponibles por categoría"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Construir catálogo con PDFs incluidos por cada categoría (solo disponibles)
        catalogo_con_pdfs = {}
        for categoria_nombre, productos in catalogo.items():
            # Filtrar solo productos disponibles
            productos_disponibles = [
                p for p in productos if p.get("estado") == "disponible"
            ]

            if not productos_disponibles:
                continue  # Saltar categoría si no tiene productos disponibles

            # Buscar la carpeta correspondiente a esta categoría
            categoria_carpeta = None
            for cat_key, cat_nom in catalogo_mgr.categoria_map.items():
                if cat_nom == categoria_nombre:
                    categoria_carpeta = cat_key
                    break

            # Obtener PDF de la categoría
            pdf_info = None
            if categoria_carpeta:
                ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
                    anio, mes, categoria_carpeta, segmento
                )
                if ruta_pdf and ruta_pdf.exists():
                    ruta_relativa = ruta_pdf.relative_to(
                        Path(IMAGENES_DIR) / "catalogos"
                    )
                    ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
                    url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
                    pdf_info = {
                        "nombre": ruta_pdf.name,
                        "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                        "url_relativa": url_relativa_pdf,
                        "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
                    }

            catalogo_con_pdfs[categoria_nombre] = {
                "pdf": pdf_info,
                "total_productos": len(productos_disponibles),
                "productos": productos_disponibles,
            }

        return {
            "segmento": segmento,
            "año": anio,
            "mes": mes,
            "categorias": catalogo_con_pdfs,
            "total_categorias": len(catalogo_con_pdfs),
            "total_productos": sum(
                len(prods["productos"]) for prods in catalogo_con_pdfs.values()
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Catálogo no encontrado: {str(e)}")


@app.get("/api/catalogo/{segmento}/{anio}/{mes}")
async def obtener_catalogo_mes(segmento: str, anio: str, mes: str):
    """Obtiene catálogo de un mes específico con productos y PDFs por categoría"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Construir catálogo con PDFs incluidos por cada categoría
        catalogo_con_pdfs = {}
        for categoria_nombre, productos in catalogo.items():
            # Buscar la carpeta correspondiente a esta categoría
            categoria_carpeta = None
            for cat_key, cat_nom in catalogo_mgr.categoria_map.items():
                if cat_nom == categoria_nombre:
                    categoria_carpeta = cat_key
                    break

            # Obtener PDF de la categoría
            pdf_info = None
            if categoria_carpeta:
                ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
                    anio, mes, categoria_carpeta, segmento
                )
                if ruta_pdf and ruta_pdf.exists():
                    ruta_relativa = ruta_pdf.relative_to(
                        Path(IMAGENES_DIR) / "catalogos"
                    )
                    ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
                    url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
                    pdf_info = {
                        "nombre": ruta_pdf.name,
                        "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                        "url_relativa": url_relativa_pdf,
                        "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
                    }

            catalogo_con_pdfs[categoria_nombre] = {
                "pdf": pdf_info,
                "total_productos": len(productos),
                "productos": productos,
            }

        # Obtener catálogo completo PDF
        catalogo_completo_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(
            anio, mes, segmento
        )
        catalogo_completo_info = None
        if catalogo_completo_pdf and catalogo_completo_pdf.exists():
            url_relativa_completo = f"/api/catalogo-completo/{segmento}/{anio}/{mes}"
            catalogo_completo_info = {
                "nombre": catalogo_completo_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_completo}",
                "url_relativa": url_relativa_completo,
                "tamaño_mb": round(
                    catalogo_completo_pdf.stat().st_size / (1024 * 1024), 2
                ),
            }

        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "catalogo_completo_pdf": catalogo_completo_info,
            "categorias": catalogo_con_pdfs,
            "total_categorias": len(catalogo_con_pdfs),
            "total_productos": sum(len(prods) for prods in catalogo.values()),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Catálogo no encontrado: {str(e)}")


@app.get("/api/catalogo/{segmento}/{anio}/{mes}/{categoria}")
async def obtener_categorias_mes(segmento: str, anio: str, mes: str, categoria: str):
    """Obtiene productos de una categoría específica con su PDF correspondiente"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría
        categoria_encontrada = None
        categoria_carpeta = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if (
                cat_nombre.lower() == categoria.lower()
                or cat_key.lower() == categoria.lower()
            ):
                categoria_encontrada = cat_nombre
                categoria_carpeta = cat_key
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        productos = catalogo[categoria_encontrada]

        # Obtener PDF de la categoría
        pdf_info = None
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            anio, mes, categoria_carpeta or categoria, segmento
        )

        if ruta_pdf and ruta_pdf.exists():
            # Construir ruta relativa para la URL
            ruta_relativa = ruta_pdf.relative_to(Path(IMAGENES_DIR) / "catalogos")
            ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
            url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
            pdf_info = {
                "nombre": ruta_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                "url_relativa": url_relativa_pdf,
                "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
            }
        else:
            pdf_info = {
                "nombre": None,
                "url": None,
                "url_relativa": None,
                "mensaje": f"No hay PDF disponible para {categoria_encontrada}",
            }

        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "categoria": categoria_encontrada,
            "total_productos": len(productos),
            "pdf": pdf_info,
            "productos": productos,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Error al obtener categoría: {str(e)}"
        )


@app.get("/api/catalogo/{segmento}/{anio}/{mes}/{categoria}/disponibles")
async def obtener_categorias_disponibles_mes(
    segmento: str, anio: str, mes: str, categoria: str
):
    """Obtiene SOLO los productos disponibles de una categoría específica en un mes dado"""
    try:
        catalogo = catalogo_mgr.cargar_catalogo_mes(anio, mes, segmento)

        # Buscar la categoría
        categoria_encontrada = None
        categoria_carpeta = None
        for cat_key, cat_nombre in catalogo_mgr.categoria_map.items():
            if (
                cat_nombre.lower() == categoria.lower()
                or cat_key.lower() == categoria.lower()
            ):
                categoria_encontrada = cat_nombre
                categoria_carpeta = cat_key
                break

        if not categoria_encontrada or categoria_encontrada not in catalogo:
            raise HTTPException(
                status_code=404, detail=f"Categoría '{categoria}' no encontrada"
            )

        # Filtrar solo productos disponibles
        productos = catalogo[categoria_encontrada]
        productos_disponibles = [
            p for p in productos if p.get("estado") == "disponible"
        ]

        # Obtener PDF de la categoría
        pdf_info = None
        ruta_pdf = catalogo_mgr.obtener_pdf_categoria(
            anio, mes, categoria_carpeta or categoria, segmento
        )

        if ruta_pdf and ruta_pdf.exists():
            # Construir ruta relativa para la URL
            ruta_relativa = ruta_pdf.relative_to(Path(IMAGENES_DIR) / "catalogos")
            ruta_relativa_str = str(ruta_relativa).replace("\\", "/")
            url_relativa_pdf = f"/api/ver-pdf/{ruta_relativa_str}"
            pdf_info = {
                "nombre": ruta_pdf.name,
                "url": f"{SERVER_URL_EXTERNAL}{url_relativa_pdf}",
                "url_relativa": url_relativa_pdf,
                "tamaño_mb": round(ruta_pdf.stat().st_size / (1024 * 1024), 2),
            }
        else:
            pdf_info = {
                "nombre": None,
                "url": None,
                "url_relativa": None,
                "mensaje": f"No hay PDF disponible para {categoria_encontrada}",
            }

        return {
            "segmento": segmento,
            "anio": anio,
            "mes": mes,
            "categoria": categoria_encontrada,
            "total_productos": len(productos_disponibles),
            "pdf": pdf_info,
            "productos": productos_disponibles,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Error al obtener categoría disponible: {str(e)}"
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


@app.get("/api/pdf-base64/{ruta:path}")
async def obtener_pdf_base64(ruta: str, force: bool = False):
    """
    Devuelve un PDF en formato base64 para uso en n8n/WhatsApp.
    Por defecto solo permite archivos menores a 5MB.
    Use ?force=true para forzar la conversión de archivos más grandes (máx 50MB).
    """
    import base64

    MAX_SIZE_DEFAULT = 5 * 1024 * 1024  # 5 MB
    MAX_SIZE_FORCED = 50 * 1024 * 1024  # 50 MB

    try:
        ruta_decodificada = urllib.parse.unquote(ruta)
        ruta_pdf = Path(IMAGENES_DIR) / "catalogos" / ruta_decodificada

        if not ruta_pdf.exists():
            raise HTTPException(
                status_code=404, detail=f"PDF no encontrado: {ruta_decodificada}"
            )

        if not ruta_pdf.is_file() or not ruta_pdf.suffix.lower() == ".pdf":
            raise HTTPException(status_code=400, detail="Ruta inválida o no es un PDF")

        tamaño_bytes = ruta_pdf.stat().st_size
        tamaño_mb = round(tamaño_bytes / (1024 * 1024), 2)

        # Verificar límites de tamaño
        max_size = MAX_SIZE_FORCED if force else MAX_SIZE_DEFAULT
        if tamaño_bytes > max_size:
            return {
                "success": False,
                "error": f"Archivo demasiado grande ({tamaño_mb} MB). Límite: {max_size // (1024*1024)} MB",
                "archivo": {
                    "nombre": ruta_pdf.name,
                    "tamaño_bytes": tamaño_bytes,
                    "tamaño_mb": tamaño_mb,
                    "mime_type": "application/pdf",
                },
                "sugerencia": "Use ?force=true para forzar (máx 50MB) o descargue directamente desde url_relativa",
                "url_descarga_directa": f"/api/ver-pdf/{ruta}",
            }

        # Leer y codificar en base64
        with open(ruta_pdf, "rb") as f:
            contenido_base64 = base64.b64encode(f.read()).decode("utf-8")

        return {
            "success": True,
            "archivo": {
                "nombre": ruta_pdf.name,
                "tamaño_bytes": tamaño_bytes,
                "tamaño_mb": tamaño_mb,
                "mime_type": "application/pdf",
            },
            "base64": contenido_base64,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener PDF: {str(e)}")


@app.get("/api/imagen-base64/{ruta:path}")
async def obtener_imagen_base64(ruta: str, force: bool = False):
    """
    Devuelve una imagen en formato base64 para uso en n8n/WhatsApp.
    Por defecto solo permite archivos menores a 5MB.
    Use ?force=true para forzar la conversión de archivos más grandes (máx 50MB).
    Soporta formatos: PNG, JPG, JPEG, GIF, WEBP
    """
    import base64
    import mimetypes

    MAX_SIZE_DEFAULT = 5 * 1024 * 1024  # 5 MB
    MAX_SIZE_FORCED = 50 * 1024 * 1024  # 50 MB
    FORMATOS_PERMITIDOS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

    try:
        ruta_decodificada = urllib.parse.unquote(ruta)
        ruta_imagen = Path(IMAGENES_DIR) / "catalogos" / ruta_decodificada

        if not ruta_imagen.exists():
            raise HTTPException(
                status_code=404, detail=f"Imagen no encontrada: {ruta_decodificada}"
            )

        if (
            not ruta_imagen.is_file()
            or ruta_imagen.suffix.lower() not in FORMATOS_PERMITIDOS
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Ruta inválida o formato no soportado. Permitidos: {', '.join(FORMATOS_PERMITIDOS)}",
            )

        tamaño_bytes = ruta_imagen.stat().st_size
        tamaño_mb = round(tamaño_bytes / (1024 * 1024), 2)

        # Verificar límites de tamaño
        max_size = MAX_SIZE_FORCED if force else MAX_SIZE_DEFAULT
        if tamaño_bytes > max_size:
            return {
                "success": False,
                "error": f"Archivo demasiado grande ({tamaño_mb} MB). Límite: {max_size // (1024*1024)} MB",
                "archivo": {
                    "nombre": ruta_imagen.name,
                    "tamaño_bytes": tamaño_bytes,
                    "tamaño_mb": tamaño_mb,
                    "formato": ruta_imagen.suffix.lower(),
                    "mime_type": mimetypes.guess_type(ruta_imagen)[0] or "image/*",
                },
                "sugerencia": "Use ?force=true para forzar (máx 50MB) o descargue directamente desde url_relativa",
                "url_descarga_directa": f"/api/catalogos/{ruta}",
            }

        # Obtener mime type
        mime_type = mimetypes.guess_type(ruta_imagen)[0] or "image/*"

        # Leer y codificar en base64
        with open(ruta_imagen, "rb") as f:
            contenido_base64 = base64.b64encode(f.read()).decode("utf-8")

        return {
            "success": True,
            "archivo": {
                "nombre": ruta_imagen.name,
                "tamaño_bytes": tamaño_bytes,
                "tamaño_mb": tamaño_mb,
                "formato": ruta_imagen.suffix.lower(),
                "mime_type": mime_type,
            },
            "base64": contenido_base64,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener imagen: {str(e)}"
        )


@app.get("/api/ver-pdf/{ruta:path}")
async def ver_pdf(ruta: str):
    """Sirve un PDF desde la ruta relativa (dentro de imagenes/catalogos/)"""
    try:
        # Decodificar la URL para manejar caracteres especiales (espacios, tildes, etc.)
        ruta_decodificada = urllib.parse.unquote(ruta)
        ruta_pdf = Path(IMAGENES_DIR) / "catalogos" / ruta_decodificada

        if not ruta_pdf.exists():
            raise HTTPException(
                status_code=404, detail=f"PDF no encontrado: {ruta_decodificada}"
            )

        if not ruta_pdf.is_file() or not ruta_pdf.suffix.lower() == ".pdf":
            raise HTTPException(status_code=400, detail="Ruta inválida o no es un PDF")

        return InlinePDFResponse(ruta_pdf, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al servir PDF: {str(e)}")


@app.get("/api/catalogo-completo/{segmento}/{anio}/{mes}")
async def obtener_catalogo_completo(segmento: str, anio: str, mes: str):
    """Obtiene el PDF del catálogo completo de un mes específico"""
    try:
        ruta_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(anio, mes, segmento)

        if not ruta_pdf or not ruta_pdf.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el catálogo completo para {segmento}/{anio}/{mes}",
            )

        return InlinePDFResponse(ruta_pdf, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener catálogo completo: {str(e)}"
        )


@app.get("/api/catalogo-completo/{segmento}/mes-actual")
async def obtener_catalogo_completo_activo(segmento: str):
    """Obtiene el PDF del catálogo completo del mes activo"""
    try:
        catalogo_info = catalogo_mgr.detectar_catalogo_actual(segmento)
        ruta_pdf = catalogo_mgr.obtener_pdf_catalogo_completo(
            catalogo_info["año"], catalogo_info["mes"], segmento
        )

        if not ruta_pdf or not ruta_pdf.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el catálogo completo activo para {segmento}",
            )

        return InlinePDFResponse(ruta_pdf, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener catálogo completo: {str(e)}"
        )


@app.get("/api/catalogos/{ruta:path}")
async def obtener_imagen_catalogo(ruta: str):
    """Obtiene imágenes de catálogos desde /api/catalogos/..."""
    try:
        # Decodificar la URL para manejar caracteres especiales (espacios, tildes, etc.)
        ruta_decodificada = urllib.parse.unquote(ruta)
        ruta_imagen = Path(IMAGENES_DIR) / "catalogos" / ruta_decodificada

        if not ruta_imagen.exists():
            raise HTTPException(
                status_code=404, detail=f"Imagen no encontrada: {ruta_decodificada}"
            )

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

# Registrar archivos estáticos si la carpeta existe
if Path("templates").exists():
    app.mount("/templates", StaticFiles(directory="templates"), name="templates")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
