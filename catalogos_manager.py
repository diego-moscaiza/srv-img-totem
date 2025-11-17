import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class CatalogoManager:
    def __init__(
        self, base_dir: str = "api/catalogos", imagenes_base: str = "imagenes/catalogos"
    ):
        self.base_dir = Path(base_dir)
        self.imagenes_base = Path(imagenes_base)
        self.catalogos_cache = {}

        # Mapeo de carpetas a nombres de categoría legibles
        self.categoria_map = {
            "1-celulares": "CELULARES",
            "2-laptops": "LAPTOPS",
            "3-televisores": "TELEVISORES",
            "4-refrigeradoras": "REFRIGERADORAS",
            "5-lavadoras": "LAVADORAS",
        }

    def detectar_catalogo_actual(self) -> Dict:
        """Detecta automáticamente el catálogo del mes actual"""
        año_actual = datetime.now().strftime("%Y")
        mes_actual = datetime.now().strftime("%m")  # "01", "02", etc.

        meses_espanol = {
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

        mes_nombre = meses_espanol.get(mes_actual)

        # Verificar que mes_nombre no sea None antes de construir la ruta
        if not mes_nombre:
            # Fallback: usar el primer mes disponible o mes por defecto
            mes_nombre = "enero"

        # Construir la ruta de manera segura (usando la ruta de productos JSON)
        ruta_catalogo = self.base_dir / año_actual / "fnb" / mes_nombre

        return {
            "año": año_actual,
            "mes": mes_nombre,
            "mes_numero": mes_actual,
            "ruta_base": str(ruta_catalogo),
            "existe": ruta_catalogo.exists(),
        }

    def cargar_catalogo_mes(self, año: str, mes: str) -> Dict:
        """Carga el catálogo de un mes específico desde los archivos JSON"""
        # Validar que año y mes no sean None o vacíos
        if not año or not mes:
            año = datetime.now().strftime("%Y")
            mes = "enero"

        cache_key = f"{año}-{mes}"

        if cache_key in self.catalogos_cache:
            return self.catalogos_cache[cache_key]

        # Cargar catálogo desde archivos JSON reales
        catalogo = self._cargar_catalogo_desde_json(año, mes)
        self.catalogos_cache[cache_key] = catalogo

        return catalogo

    def _cargar_catalogo_desde_json(self, año: str, mes: str) -> Dict:
        """Carga productos reales desde los archivos JSON en la estructura de carpetas"""
        catalogo = {}

        # Ruta base donde están los productos.json
        ruta_mes = self.base_dir / año / "fnb" / mes

        if not ruta_mes.exists():
            print(f"⚠️ Advertencia: No existe la ruta {ruta_mes}")
            return catalogo

        # Recorrer cada carpeta de categoría (1-celulares, 2-laptops, etc.)
        for carpeta in sorted(ruta_mes.iterdir()):
            if not carpeta.is_dir():
                continue

            nombre_carpeta = carpeta.name

            # Obtener el nombre de categoría desde el mapeo
            categoria_nombre = self.categoria_map.get(nombre_carpeta)

            if not categoria_nombre:
                print(f"⚠️ Carpeta no reconocida: {nombre_carpeta}")
                continue

            # Buscar productos.json en esta carpeta
            archivo_productos = carpeta / "productos.json"

            if not archivo_productos.exists():
                print(f"⚠️ No existe productos.json en {carpeta}")
                catalogo[categoria_nombre] = []
                continue

            # Cargar y procesar el JSON
            try:
                with open(archivo_productos, "r", encoding="utf-8") as f:
                    productos = json.load(f)

                # Procesar cada producto para agregar información de rutas
                productos_procesados = []
                for producto in productos:
                    # Obtener solo el nombre del archivo de imagen (sin ruta)
                    imagen_original = producto.get('imagen', '')
                    # Si la imagen ya tiene ruta, extraer solo el nombre del archivo
                    nombre_imagen = Path(imagen_original).name if imagen_original else ''
                    
                    # Enriquecer producto con información adicional
                    producto_enriquecido = {
                        **producto,
                        "categoria": categoria_nombre,
                        "mes_validez": f"{año}-{mes}",
                        "stock": True,  # Por defecto asumimos que tiene stock
                        # Construir rutas dinámicamente usando solo el nombre del archivo
                        "ruta_imagen_relativa": f"catalogos/{año}/fnb/{mes}/{nombre_carpeta}/{nombre_imagen}",
                        "ruta_imagen_absoluta": f"/static/catalogos/{año}/fnb/{mes}/{nombre_carpeta}/{nombre_imagen}",
                    }
                    productos_procesados.append(producto_enriquecido)

                catalogo[categoria_nombre] = productos_procesados

            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON en {archivo_productos}: {e}")
                catalogo[categoria_nombre] = []
            except Exception as e:
                print(f"❌ Error al cargar {archivo_productos}: {e}")
                catalogo[categoria_nombre] = []

        return catalogo

    def validar_producto(self, producto_id: str, categoria: str) -> Dict:
        """Valida si un producto está disponible"""
        # Validar parámetros de entrada
        if not producto_id or not categoria:
            return {
                "disponible": False,
                "razon": "producto_id y categoria son requeridos",
            }

        catalogo_info = self.detectar_catalogo_actual()
        catalogo = self.cargar_catalogo_mes(catalogo_info["año"], catalogo_info["mes"])

        if categoria not in catalogo:
            return {"disponible": False, "razon": "Categoría no disponible"}

        producto = next(
            (p for p in catalogo[categoria] if p["id"] == producto_id), None
        )

        if not producto:
            return {"disponible": False, "razon": "Producto no encontrado"}

        if not producto["stock"]:
            return {"disponible": False, "razon": "Sin stock"}

        return {
            "disponible": True,
            "producto": producto,
            "catalogo_actual": catalogo_info,
        }

    def obtener_meses_disponibles(self) -> List[Dict]:
        """Obtiene lista de meses con catálogos disponibles desde los JSON"""
        meses_disponibles = []

        if not self.base_dir.exists():
            print(f"⚠️ No existe el directorio base: {self.base_dir}")
            return meses_disponibles

        try:
            for año_dir in sorted(self.base_dir.iterdir()):
                if not año_dir.is_dir():
                    continue

                # Buscar dentro de "fnb"
                fnb_dir = año_dir / "fnb"
                if not fnb_dir.exists():
                    continue

                for mes_dir in sorted(fnb_dir.iterdir()):
                    if mes_dir.is_dir():
                        meses_disponibles.append(
                            {
                                "año": año_dir.name,
                                "mes": mes_dir.name,
                                "ruta": str(mes_dir),
                                "tiene_productos": self._contar_productos(mes_dir),
                            }
                        )
        except Exception as e:
            print(f"❌ Error al obtener meses disponibles: {e}")

        return sorted(
            meses_disponibles, key=lambda x: (x["año"], x["mes"]), reverse=True
        )

    def _contar_productos(self, ruta_mes: Path) -> int:
        """Cuenta el total de productos en un mes"""
        total = 0
        for carpeta in ruta_mes.iterdir():
            if carpeta.is_dir():
                archivo_productos = carpeta / "productos.json"
                if archivo_productos.exists():
                    try:
                        with open(archivo_productos, "r", encoding="utf-8") as f:
                            productos = json.load(f)
                            total += (
                                len(productos) if isinstance(productos, list) else 0
                            )
                    except:
                        pass
        return total


# Instancia global
catalogo_manager = CatalogoManager()
