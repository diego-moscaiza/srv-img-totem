import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CatalogoManager:
    def __init__(self, base_dir: str = "imagenes/catalogos"):
        self.base_dir = Path(base_dir)
        self.catalogos_cache = {}
    
    def detectar_catalogo_actual(self) -> Dict:
        """Detecta automáticamente el catálogo del mes actual"""
        año_actual = datetime.now().strftime("%Y")
        mes_actual = datetime.now().strftime("%m")  # "01", "02", etc.
        
        meses_espanol = {
            "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
            "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
            "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
        }
        
        mes_nombre = meses_espanol.get(mes_actual)
        
        # Verificar que mes_nombre no sea None antes de construir la ruta
        if not mes_nombre:
            # Fallback: usar el primer mes disponible o mes por defecto
            mes_nombre = "enero"
        
        # Construir la ruta de manera segura
        ruta_catalogo = self.base_dir / año_actual / mes_nombre
        
        return {
            "año": año_actual,
            "mes": mes_nombre,
            "mes_numero": mes_actual,
            "ruta_base": str(ruta_catalogo),
            "existe": ruta_catalogo.exists()
        }
    
    def cargar_catalogo_mes(self, año: str, mes: str) -> Dict:
        """Carga el catálogo de un mes específico"""
        # Validar que año y mes no sean None o vacíos
        if not año or not mes:
            año = datetime.now().strftime("%Y")
            mes = "enero"
        
        cache_key = f"{año}-{mes}"
        
        if cache_key in self.catalogos_cache:
            return self.catalogos_cache[cache_key]
        
        # En una implementación real, esto cargaría desde JSON/DB
        catalogo = self._generar_catalogo_ejemplo(año, mes)
        self.catalogos_cache[cache_key] = catalogo
        
        return catalogo
    
    def _generar_catalogo_ejemplo(self, año: str, mes: str) -> Dict:
        """Genera catálogo de ejemplo (reemplazar con carga real)"""
        # Asegurarse de que año y mes tengan valores por defecto
        año = año or datetime.now().strftime("%Y")
        mes = mes or "enero"
        
        return {
            "CELULARES": [
                {
                    "id": f"samsung_a15_{mes}",
                    "nombre": "SAMSUNG GALAXY A15",
                    "descripcion": f"256 GB - 8GB RAM - Edición {mes.capitalize()}",
                    "imagen": f"http://192.168.1.74:8000/static/catalogos/{año}/{mes}/fnb/precios-cuotas/1-celulares/01.png",
                    "precio": "S/ 1,177.23",
                    "precio_numero": 1177.23,
                    "stock": True,
                    "categoria": "CELULARES",
                    "mes_validez": f"{año}-{mes}",
                    "cuotas": [3, 6, 12]
                }
            ],
            "LAPTOPS": [
                {
                    "id": f"lenovo_ideapad_{mes}",
                    "nombre": "LENOVO IDEAPAD 3",
                    "descripcion": f"15.6\" - Intel i5 - Edición {mes.capitalize()}",
                    "imagen": f"http://192.168.1.74:8000/static/catalogos/{año}/{mes}/fnb/precios-cuotas/2-laptops/01.png",
                    "precio": "S/ 2,199.00",
                    "precio_numero": 2199.00,
                    "stock": True,
                    "categoria": "LAPTOPS", 
                    "mes_validez": f"{año}-{mes}",
                    "cuotas": [3, 6, 12, 18]
                }
            ]
        }
    
    def validar_producto(self, producto_id: str, categoria: str) -> Dict:
        """Valida si un producto está disponible"""
        # Validar parámetros de entrada
        if not producto_id or not categoria:
            return {
                "disponible": False, 
                "razon": "producto_id y categoria son requeridos"
            }
        
        catalogo_info = self.detectar_catalogo_actual()
        catalogo = self.cargar_catalogo_mes(
            catalogo_info["año"], 
            catalogo_info["mes"]
        )
        
        if categoria not in catalogo:
            return {"disponible": False, "razon": "Categoría no disponible"}
        
        producto = next((p for p in catalogo[categoria] if p["id"] == producto_id), None)
        
        if not producto:
            return {"disponible": False, "razon": "Producto no encontrado"}
        
        if not producto["stock"]:
            return {"disponible": False, "razon": "Sin stock"}
        
        return {
            "disponible": True,
            "producto": producto,
            "catalogo_actual": catalogo_info
        }
    
    def obtener_meses_disponibles(self) -> List[Dict]:
        """Obtiene lista de meses con catálogos disponibles"""
        meses_disponibles = []
        
        if not self.base_dir.exists():
            return meses_disponibles
        
        for año_dir in self.base_dir.iterdir():
            if año_dir.is_dir():
                for mes_dir in año_dir.iterdir():
                    if mes_dir.is_dir():
                        meses_disponibles.append({
                            "año": año_dir.name,
                            "mes": mes_dir.name,
                            "ruta": str(mes_dir)
                        })
        
        return sorted(meses_disponibles, key=lambda x: (x["año"], x["mes"]), reverse=True)

# Instancia global
catalogo_manager = CatalogoManager()
