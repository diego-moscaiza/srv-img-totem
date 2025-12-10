from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from src.database import SessionLocal, Producto
import os

# Cargar .env si existe (para desarrollo local)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # En Docker no necesita dotenv


def get_imagenes_base():
    """
    Determina la ruta base de imágenes según el entorno:
    - Docker (producción): /srv/imagenes/catalogos
    - Local (desarrollo): imagenes/catalogos
    """
    # Primero verificar variable de entorno
    imagenes_dir = os.getenv("IMAGENES_DIR")
    if imagenes_dir:
        return Path(imagenes_dir) / "catalogos"

    # Detectar si estamos en Docker
    if Path("/srv/imagenes/catalogos").exists():
        return Path("/srv/imagenes/catalogos")

    # Local: usar ruta relativa
    return Path("imagenes/catalogos")


class SegmentoCatalogo:
    """Abstracción para manejar un segmento específico (fnb, gaso, etc.)"""

    def __init__(
        self, nombre_segmento: str, categoria_map: Dict[str, str], imagenes_base: Path
    ):
        self.nombre = nombre_segmento
        self.categoria_map = categoria_map
        self.imagenes_base = imagenes_base
        self.cache = {}

    def invalidar_cache(self):
        """Invalida todo el caché del segmento"""
        self.cache.clear()
        print(f"[CACHE] Invalidado para segmento: {self.nombre}")

    def cargar_catalogo_mes(self, año: str, mes: str) -> Dict:
        """Carga el catálogo de un mes específico desde la BD"""
        cache_key = f"{año}-{mes}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        catalogo = self._cargar_desde_db(año, mes)
        self.cache[cache_key] = catalogo
        return catalogo

    def _cargar_desde_db(self, año: str, mes: str) -> Dict:
        """Carga productos desde la BD para este segmento"""
        catalogo = {}

        try:
            db = SessionLocal()

            # Convertir número de mes a nombre si es necesario
            meses_map = {
                "01": "enero",
                "02": "febrero",
                "03": "marzo",
                "04": "abril",
                "05": "mayo",
                "06": "junio",
                "07": "julio",
                "08": "agosto",
                "09": "septiembre",
                "10": "octubre",
                "11": "noviembre",
                "12": "diciembre",
            }

            # Extraer el nombre del mes si viene en formato "12-diciembre"
            if "-" in mes:
                mes_nombre = mes.split("-", 1)[
                    1
                ]  # Obtiene "diciembre" de "12-diciembre"
            else:
                mes_nombre = meses_map.get(mes, mes)

            # Forzar lectura fresca de la BD (sin caché de SQLAlchemy)
            db.expire_all()

            # Normalizar nombre de segmento para consistency
            nombre_segmento_normalizado = self.nombre.strip().lower()

            # Consultar productos del mes y año
            productos = (
                db.query(Producto)
                .filter(
                    Producto.ano == int(año),
                    Producto.mes == mes_nombre,
                    Producto.segmento == nombre_segmento_normalizado,
                )
                .all()
            )

            # Convertir a diccionarios ANTES de cerrar la sesión para evitar lazy loading
            catalogo_temp = {}
            for producto in productos:
                categoria = producto.categoria

                if categoria not in catalogo_temp:
                    catalogo_temp[categoria] = []

                # Determinar si el producto está activo basado en estado y stock
                es_disponible = producto.estado == "disponible" and producto.stock
                es_mes_actual = (
                    año == datetime.now().strftime("%Y")
                    and mes_nombre == self._convertir_mes_actual()
                )

                producto_dict = {
                    "id": producto.codigo,
                    "codigo": producto.codigo,
                    "nombre": producto.nombre,
                    "descripcion": producto.descripcion,
                    "precio": producto.precio,
                    "categoria": categoria,
                    "imagen": producto.imagen_listado,
                    "imagen_caracteristicas": producto.imagen_caracteristicas,
                    "cuotas": producto.cuotas,
                    "estado": producto.estado,  # disponible, no_disponible, agotado
                    "stock": producto.stock,
                    "mes_validez": f"{año}-{mes_nombre}",
                    "segmento": self.nombre,
                    "activo": es_disponible and es_mes_actual,
                }

                catalogo_temp[categoria].append(producto_dict)

            catalogo = catalogo_temp
            db.close()

            return catalogo

        except Exception as e:
            print(f"[ERROR] No se pudo cargar catálogo {self.nombre}: {e}")
            return {}

    def validar_producto(self, producto_id: str, categoria: str) -> Dict:
        """Valida disponibilidad de un producto en este segmento"""
        catalogo_actual = self.detectar_mes_actual()
        catalogo = self.cargar_catalogo_mes(
            catalogo_actual["año"], catalogo_actual["mes"]
        )

        if categoria not in catalogo:
            return {"disponible": False, "razon": "Categoría no disponible"}

        producto = next(
            (p for p in catalogo[categoria] if p["id"] == producto_id), None
        )

        if not producto:
            return {"disponible": False, "razon": "Producto no encontrado"}

        if not producto["stock"]:
            return {"disponible": False, "razon": "Sin stock"}

        return {"disponible": True, "producto": producto}

    def detectar_mes_actual(self) -> Dict:
        """Detecta el mes actual"""
        año = datetime.now().strftime("%Y")
        mes_num = datetime.now().strftime("%m")

        meses_map = {
            "01": "enero",
            "02": "febrero",
            "03": "marzo",
            "04": "abril",
            "05": "mayo",
            "06": "junio",
            "07": "julio",
            "08": "agosto",
            "09": "septiembre",
            "10": "octubre",
            "11": "noviembre",
            "12": "diciembre",
        }

        mes_nombre = meses_map.get(mes_num, "noviembre")

        return {
            "año": año,
            "mes": mes_nombre,
            "mes_numero": mes_num,
            "segmento": self.nombre,
        }

    def _convertir_mes_actual(self) -> str:
        """Convierte el mes actual a nombre"""
        mes_num = datetime.now().strftime("%m")
        meses_map = {
            "01": "enero",
            "02": "febrero",
            "03": "marzo",
            "04": "abril",
            "05": "mayo",
            "06": "junio",
            "07": "julio",
            "08": "agosto",
            "09": "septiembre",
            "10": "octubre",
            "11": "noviembre",
            "12": "diciembre",
        }
        return meses_map.get(mes_num, "noviembre")

    def obtener_pdf_categoria(
        self, año: str, mes: str, categoria: str
    ) -> Optional[Path]:
        """Obtiene la ruta del PDF de una categoría
        Busca en la raíz de la carpeta de la categoría
        """
        categoria_lower = categoria.lower()

        nombre_carpeta = None
        for carpeta_key, cat_nombre in self.categoria_map.items():
            if (
                cat_nombre == categoria_lower
                or carpeta_key == categoria
                or carpeta_key.lower() == categoria_lower
            ):
                nombre_carpeta = carpeta_key
                break

        if not nombre_carpeta:
            return None

        # Buscar la carpeta del mes con formato XX-mes
        ruta_año = self.imagenes_base / self.nombre / año
        if not ruta_año.exists():
            return None

        # Buscar carpeta que contenga el nombre del mes
        mes_limpio = mes.split("-")[-1] if "-" in mes else mes
        carpeta_mes = None
        for carpeta in ruta_año.iterdir():
            if carpeta.is_dir() and mes_limpio in carpeta.name.lower():
                carpeta_mes = carpeta.name
                break

        if not carpeta_mes:
            return None

        ruta_categoria = ruta_año / carpeta_mes / nombre_carpeta

        if not ruta_categoria.exists():
            return None

        # Buscar PDFs en la raíz de la carpeta de categoría (no en subcarpetas)
        pdfs = list(ruta_categoria.glob("*.pdf"))
        return pdfs[0] if pdfs else None

    def _buscar_carpeta_mes(self, año: str, mes: str) -> Optional[Path]:
        """Busca la carpeta del mes con formato XX-mes"""
        ruta_año = self.imagenes_base / self.nombre / año
        if not ruta_año.exists():
            return None

        mes_limpio = mes.split("-")[-1] if "-" in mes else mes
        for carpeta in ruta_año.iterdir():
            if carpeta.is_dir() and mes_limpio in carpeta.name.lower():
                return carpeta
        return None

    def listar_pdfs_mes(self, año: str, mes: str) -> Dict[str, Optional[str]]:
        """Lista PDFs disponibles en un mes para este segmento
        Busca PDFs en la raíz de cada carpeta de categoría
        Ej: fnb/2025/12-diciembre/1-celulares/*.pdf
        """
        pdfs_disponibles = {}

        ruta_mes = self._buscar_carpeta_mes(año, mes)
        if not ruta_mes:
            return pdfs_disponibles

        # Buscar PDFs en cada carpeta de categoría
        for nombre_carpeta, categoria_nombre in sorted(self.categoria_map.items()):
            ruta_categoria = ruta_mes / nombre_carpeta

            if ruta_categoria.exists():
                # Buscar PDFs en la raíz de la carpeta (no subcarpetas)
                pdfs = list(ruta_categoria.glob("*.pdf"))
                if pdfs:
                    ruta_relativa = pdfs[0].relative_to(self.imagenes_base)
                    pdfs_disponibles[categoria_nombre] = str(ruta_relativa).replace(
                        "\\", "/"
                    )
                else:
                    pdfs_disponibles[categoria_nombre] = None
            else:
                pdfs_disponibles[categoria_nombre] = None

        return pdfs_disponibles

    def obtener_pdf_catalogo_completo(self, año: str, mes: str) -> Optional[Path]:
        """Obtiene la ruta del PDF del catálogo completo del mes (ubicado en la raíz del mes)"""
        ruta_mes = self._buscar_carpeta_mes(año, mes)
        if not ruta_mes:
            return None

        # Buscar PDFs en la raíz de la carpeta del mes
        pdfs = list(ruta_mes.glob("*.pdf"))
        return pdfs[0] if pdfs else None


class CatalogoManager:
    """Gestor central de catálogos por segmento"""

    def __init__(
        self,
        imagenes_base: str | None = None,
        segmentos: Optional[List[str]] = None,
    ):
        # Usar la función que detecta el entorno automáticamente
        self.imagenes_base = (
            Path(imagenes_base) if imagenes_base else get_imagenes_base()
        )
        self.segmentos: Dict[str, SegmentoCatalogo] = {}

        # Mapeo de categorías ESPECÍFICO POR SEGMENTO
        # FNB: 1-celulares, 2-laptops, 3-televisores, 4-refrigeradoras, 5-lavadoras
        categoria_map_fnb = {
            "1-celulares": "celulares",
            "2-laptops": "laptops",
            "3-televisores": "televisores",
            "4-refrigeradoras": "refrigeradoras",
            "5-lavadoras": "lavadoras",
        }

        # GASO: 1-celulares, 2-televisores, 3-refrigeradores, 4-lavadoras, 5-fusion
        categoria_map_gaso = {
            "1-celulares": "celulares",
            "2-televisores": "televisores",
            "3-refrigeradores": "refrigeradores",
            "4-lavadoras": "lavadoras",
            "5-fusion": "fusion",
        }

        # Crear instancias de cada segmento con su mapeo específico
        segmentos_default = segmentos or ["fnb", "gaso"]
        for segmento_nombre in segmentos_default:
            # Seleccionar mapa según segmento
            categoria_map = (
                categoria_map_fnb if segmento_nombre == "fnb" else categoria_map_gaso
            )
            self.segmentos[segmento_nombre] = SegmentoCatalogo(
                segmento_nombre, categoria_map, self.imagenes_base
            )

        # Guardar un mapa genérico para compatibilidad (usado ocasionalmente)
        self.categoria_map = {**categoria_map_fnb, **categoria_map_gaso}

    def obtener_segmento(self, nombre_segmento: str = "fnb") -> SegmentoCatalogo:
        """Obtiene la instancia de un segmento específico"""
        # Normalizar segmento a minúsculas
        nombre_segmento_normalizado = nombre_segmento.strip().lower()
        if nombre_segmento_normalizado not in self.segmentos:
            raise ValueError(
                f"Segmento '{nombre_segmento_normalizado}' no existe. Disponibles: {list(self.segmentos.keys())}"
            )
        return self.segmentos[nombre_segmento_normalizado]

    def invalidar_cache(self, segmento: str | None = None):
        """Invalida el caché de un segmento o todos si no se especifica"""
        if segmento:
            # Normalizar segmento a minúsculas
            segmento_normalizado = segmento.strip().lower()
            if segmento_normalizado in self.segmentos:
                print(
                    f"[CACHE] Invalidando caché para segmento: {segmento_normalizado}"
                )
                self.segmentos[segmento_normalizado].invalidar_cache()
            else:
                print(
                    f"[CACHE] Advertencia: segmento '{segmento_normalizado}' no encontrado. Segmentos disponibles: {list(self.segmentos.keys())}"
                )
        else:
            for seg in self.segmentos.values():
                seg.invalidar_cache()
            print("[CACHE] Invalidado para TODOS los segmentos")

    def detectar_catalogo_actual(self, segmento: str = "fnb") -> Dict:
        """Detecta automáticamente el catálogo del mes actual para un segmento"""
        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.detectar_mes_actual()

    def cargar_catalogo_mes(self, año: str, mes: str, segmento: str = "fnb") -> Dict:
        """Carga el catálogo de un mes específico desde la BD para un segmento"""
        if not año or not mes:
            año = datetime.now().strftime("%Y")
            mes = "noviembre"

        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.cargar_catalogo_mes(año, mes)

    def validar_producto(
        self, producto_id: str, categoria: str, segmento: str = "fnb"
    ) -> Dict:
        """Valida si un producto está disponible en un segmento"""
        if not producto_id or not categoria:
            return {
                "disponible": False,
                "razon": "producto_id y categoria son requeridos",
            }

        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.validar_producto(producto_id, categoria)

    def obtener_meses_disponibles(self) -> List[Dict]:
        """Obtiene lista de meses disponibles con productos en la BD"""
        meses_disponibles = []

        try:
            db = SessionLocal()
            registros = db.query(Producto.ano, Producto.mes).distinct().all()
            db.close()

            meses_dict = {}
            for ano, mes in registros:
                key = f"{ano}-{mes}"
                if key not in meses_dict:
                    meses_dict[key] = {"año": str(ano), "mes": mes}

            for key, mes_info in meses_dict.items():
                db = SessionLocal()
                cantidad = (
                    db.query(Producto)
                    .filter(
                        Producto.ano == int(mes_info["año"]),
                        Producto.mes == mes_info["mes"],
                    )
                    .count()
                )
                db.close()

                meses_info_completa = {**mes_info, "tiene_productos": cantidad}
                meses_disponibles.append(meses_info_completa)

            return sorted(
                meses_disponibles, key=lambda x: (x["año"], x["mes"]), reverse=True
            )

        except Exception as e:
            print(f"[ERROR] No se pudo obtener meses disponibles: {e}")
            return []

    def obtener_segmentos_disponibles(self) -> List[str]:
        """Obtiene lista de segmentos configurados"""
        return list(self.segmentos.keys())

    def obtener_pdf_categoria(
        self, año: str, mes: str, categoria: str, segmento: str = "fnb"
    ) -> Optional[Path]:
        """Obtiene la ruta del PDF de una categoría para un segmento"""
        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.obtener_pdf_categoria(año, mes, categoria)

    def listar_pdfs_mes(
        self, año: str, mes: str, segmento: str = "fnb"
    ) -> Dict[str, Optional[str]]:
        """Lista PDFs disponibles en un mes para un segmento"""
        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.listar_pdfs_mes(año, mes)

    def obtener_pdf_catalogo_completo(
        self, año: str, mes: str, segmento: str = "fnb"
    ) -> Optional[Path]:
        """Obtiene la ruta del PDF del catálogo completo del mes para un segmento"""
        segmento_obj = self.obtener_segmento(segmento)
        return segmento_obj.obtener_pdf_catalogo_completo(año, mes)


# Instancia global
catalogo_manager = CatalogoManager()
