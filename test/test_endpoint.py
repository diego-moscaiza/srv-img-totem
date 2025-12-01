#!/usr/bin/env python3
r"""
Script para probar los endpoints de productos
Uso: python test_endpoint.py

NOTA: Ejecutar desde la terminal con venv activado:

  EN WINDOWS:
    cd srv-img-totem
    .\venv\Scripts\activate
    python test_endpoint.py

  EN LINUX/MAC:
    cd srv-img-totem
    source venv/bin/activate
    python test_endpoint.py
"""

import requests
import json
import os
from typing import Dict, List, Any

# Configuración
BASE_URL = os.environ.get("SERVER_URL", "http://192.168.1.65:8000")


def verificar_servidor_disponible(url: str, timeout: int = 5) -> bool:
    """Verifica si el servidor está disponible"""
    try:
        response = requests.get(url, timeout=timeout)
        return True
    except:
        return False


class TestadorEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def test_listar_productos(self) -> Dict[str, Any]:
        """Obtiene lista de todos los productos"""
        print("\n" + "=" * 60)
        print("TEST 1: Obtener lista de TODOS los productos")
        print("=" * 60)

        url = f"{self.base_url}/api/productos"
        print(f"URL: {url}\n")

        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                productos = response.json()
                print(f"✅ ÉXITO - {len(productos)} productos obtenidos")
                print(f"\n📋 Primeros 3 productos:")
                for idx, producto in enumerate(productos[:3], 1):
                    print(f"\n{idx}. {producto.get('nombre', 'N/A')}")
                    print(f"   ID: {producto.get('id')}")
                    print(f"   Código: {producto.get('codigo')}")
                    print(f"   Precio: S/. {producto.get('precio')}")
                    print(f"   Categoría: {producto.get('categoria')}")
                    print(f"   Segmento: {producto.get('segmento')}")
                    print(f"   Estado: {producto.get('estado')}")
                    print(f"   Imagen: {producto.get('imagen_listado', 'N/A')[:50]}...")

                print(f"\n📊 Total de productos: {len(productos)}")
                return {"status": "success", "count": len(productos), "data": productos}
            else:
                print(f"❌ ERROR - Status {response.status_code}")
                print(f"Respuesta: {response.text}")
                return {"status": "error", "code": response.status_code}

        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR - No se pudo conectar a {self.base_url}")
            print("   Asegúrate de que el servidor esté corriendo en esa dirección")
            return {"status": "connection_error"}
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {"status": "error", "message": str(e)}

    def test_obtener_producto(self, producto_id: int = 1) -> Dict[str, Any]:
        """Obtiene un producto específico por ID"""
        print("\n" + "=" * 60)
        print(f"TEST 2: Obtener producto específico (ID: {producto_id})")
        print("=" * 60)

        url = f"{self.base_url}/api/productos/{producto_id}"
        print(f"URL: {url}\n")

        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                producto = response.json()
                print(f"✅ ÉXITO - Producto encontrado")
                print(f"\n📦 Detalles del producto:")
                print(f"   Nombre: {producto.get('nombre')}")
                print(f"   Código: {producto.get('codigo')}")
                print(f"   Descripción: {producto.get('descripcion', 'N/A')}")
                print(f"   Precio: S/. {producto.get('precio')}")
                print(f"   Categoría: {producto.get('categoria')}")
                print(f"   Segmento: {producto.get('segmento')}")
                print(f"   Estado: {producto.get('estado')}")
                print(f"   Mes: {producto.get('mes')}")
                print(f"   Año: {producto.get('ano')}")
                print(f"   Stock: {producto.get('stock')}")
                print(f"   Cuotas: {json.dumps(producto.get('cuotas', {}), indent=2)}")
                print(f"   Imagen listado: {producto.get('imagen_listado', 'N/A')}")
                print(
                    f"   Imagen características: {producto.get('imagen_caracteristicas', 'N/A')}"
                )

                return {"status": "success", "data": producto}
            elif response.status_code == 404:
                print(f"❌ Producto no encontrado (ID: {producto_id})")
                return {"status": "not_found"}
            else:
                print(f"❌ ERROR - Status {response.status_code}")
                print(f"Respuesta: {response.text}")
                return {"status": "error", "code": response.status_code}

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {"status": "error", "message": str(e)}

    def test_crear_producto(self) -> Dict[str, Any]:
        """Crea un nuevo producto de prueba"""
        print("\n" + "=" * 60)
        print("TEST 3: Crear un nuevo producto")
        print("=" * 60)

        url = f"{self.base_url}/api/productos"
        print(f"URL: {url}\n")

        nuevo_producto = {
            "codigo": "TEST0001",
            "nombre": "Producto de Prueba",
            "descripcion": "Este es un producto de prueba",
            "precio": 99.99,
            "categoria": "celulares",
            "segmento": "fnb",
            "estado": "disponible",
            "stock": True,
            "imagen_listado": "catalogos/fnb/2025/11-noviembre/1-celulares/listado/01.png",
            "imagen_caracteristicas": "catalogos/fnb/2025/11-noviembre/1-celulares/caracteristicas/01.png",
            "mes": "noviembre",
            "ano": 2025,
            "cuotas": {"3": 33.33, "6": 16.67, "12": 8.33},
        }

        print(f"📤 Enviando datos:")
        print(json.dumps(nuevo_producto, indent=2, ensure_ascii=False))

        try:
            response = self.session.post(url, json=nuevo_producto, timeout=10)

            if response.status_code == 200:
                producto_creado = response.json()
                print(f"\n✅ ÉXITO - Producto creado")
                print(f"   ID: {producto_creado.get('id')}")
                print(f"   Nombre: {producto_creado.get('nombre')}")
                return {"status": "success", "data": producto_creado}
            else:
                print(f"\n❌ ERROR - Status {response.status_code}")
                print(f"Respuesta: {response.text}")
                return {"status": "error", "code": response.status_code}

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {"status": "error", "message": str(e)}

    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("\n" + "🚀 INICIANDO PRUEBAS DE ENDPOINTS".center(60, "="))
        print(f"Base URL: {self.base_url}\n")

        resultados = {
            "listar": self.test_listar_productos(),
            "obtener": self.test_obtener_producto(),
            "crear": self.test_crear_producto(),
        }

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)

        for test_name, resultado in resultados.items():
            status = resultado.get("status", "desconocido")
            emoji = "✅" if status == "success" else "❌"
            print(f"{emoji} {test_name}: {status}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🔍 Verificando disponibilidad del servidor...")
    print(f"URL: {BASE_URL}")

    if not verificar_servidor_disponible(BASE_URL):
        print("⚠️  El servidor NO está disponible en http://192.168.1.65:8000")
        print("\n📝 Para iniciar el servidor, abre otra terminal y ejecuta:")
        print("\n  EN WINDOWS:")
        print("   cd srv-img-totem")
        print("   .\\venv\\Scripts\\activate")
        print("   python main.py")
        print("\n  EN LINUX/MAC:")
        print("   cd srv-img-totem")
        print("   source venv/bin/activate")
        print("   python main.py")
        print("\nLuego vuelve a ejecutar este script.")
        exit(1)

    print("✅ Servidor disponible!\n")

    testador = TestadorEndpoints(BASE_URL)
    testador.run_all_tests()
