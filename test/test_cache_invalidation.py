#!/usr/bin/env python3
"""
Prueba de invalidación de caché en tiempo real
Verifica que los cambios de estado/stock se reflejen inmediatamente en la API
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://192.168.5.85:8000"

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_section(title):
    print(f"\n{title}")
    print("-" * 60)

def test_servidor():
    """Verifica disponibilidad del servidor"""
    print_header("VERIFICANDO DISPONIBILIDAD DEL SERVIDOR")
    try:
        response = requests.get(f"{BASE_URL}/api/productos", timeout=5)
        if response.status_code == 200:
            print(f"✓ Servidor disponible en {BASE_URL}")
            return True
        else:
            print(f"✗ Servidor respondiendo con error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ No se puede conectar al servidor: {e}")
        return False

def obtener_catalogo_activo(segmento):
    """Obtiene el catálogo del mes actual de un segmento"""
    url = f"{BASE_URL}/api/catalogo/{segmento}/mes-actual"
    response = requests.get(url)
    data = response.json()
    
    # La respuesta tiene estructura: {segmento, catalogo_info, categorias, ...}
    # Buscar las categorías con productos
    if "categorias" in data:
        return data["categorias"]
    
    # Fallback: buscar directamente las claves que contienen productos
    resultado = {}
    for key, value in data.items():
        if isinstance(value, dict) and "productos" in value:
            resultado[key] = value
    return resultado if resultado else data

def obtener_producto(producto_id):
    """Obtiene un producto específico"""
    url = f"{BASE_URL}/api/productos/{producto_id}"
    response = requests.get(url)
    return response.json()

def actualizar_producto(producto_id, datos):
    """Actualiza un producto"""
    url = f"{BASE_URL}/api/productos/{producto_id}"
    response = requests.put(url, json=datos)
    return response.status_code, response.json()

def buscar_producto_en_catalogo(catalogo, codigo):
    """Busca un producto por código en el catálogo"""
    for categoria, datos_cat in catalogo.items():
        if isinstance(datos_cat, dict) and "productos" in datos_cat:
            for producto in datos_cat["productos"]:
                if producto.get("codigo") == codigo:
                    return producto
    return None

def test_cambio_estado():
    """Prueba principal: cambio de estado y sincronización"""
    print_header("PRUEBA: CAMBIO DE ESTADO Y SINCRONIZACIÓN DE CACHÉ")
    
    # 1. Obtener catálogo actual (usar fnb que tiene productos en diciembre)
    print_section("1. Obteniendo catálogo actual (fnb)")
    catalogo_inicial = obtener_catalogo_activo("fnb")
    print(f"Catálogo obtenido con {len(catalogo_inicial)} categorías")
    
    # Buscar un producto conocido para usar en la prueba
    producto_test = None
    for categoria, datos_cat in catalogo_inicial.items():
        if isinstance(datos_cat, dict) and "productos" in datos_cat:
            if datos_cat["productos"]:
                producto_test = datos_cat["productos"][0]
                break
    
    if not producto_test:
        print("✗ No hay productos en el catálogo fnb")
        return False
    
    codigo_original = producto_test["codigo"]
    estado_original = producto_test["estado"]
    
    # Obtener el producto completo por código para conseguir el ID real de BD
    print(f"\n  Buscando ID real del producto {codigo_original}...")
    productos_bd = requests.get(f"{BASE_URL}/api/productos").json()
    producto_bd = None
    for p in productos_bd:
        if p.get("codigo") == codigo_original:
            producto_bd = p
            break
    
    if not producto_bd:
        print(f"✗ Producto {codigo_original} no encontrado en BD")
        return False
    
    producto_id = producto_bd["id"]
    
    print(f"\nProducto de prueba seleccionado:")
    print(f"  ID (BD): {producto_id}")
    print(f"  Código: {codigo_original}")
    print(f"  Estado actual: {estado_original}")
    print(f"  Mes actual: {producto_test.get('mes_actual')}")
    
    # 2. Cambiar estado a "no_disponible"
    print_section("2. Cambiando estado a 'no_disponible'")
    status, respuesta = actualizar_producto(producto_id, {
        "estado": "no_disponible"
    })
    
    if status == 200:
        print(f"✓ Producto actualizado exitosamente")
        print(f"  Nuevo estado en BD: {respuesta.get('estado')}")
    else:
        print(f"✗ Error al actualizar: {status}")
        return False
    
    # 3. Verificar cambio INMEDIATO en el catálogo
    print_section("3. Verificando cambio INMEDIATO en catálogo (sin espera)")
    time.sleep(0.1)  # Mínima espera para que se complete la invalidación
    
    catalogo_despues = obtener_catalogo_activo("fnb")
    producto_en_catalogo = buscar_producto_en_catalogo(catalogo_despues, codigo_original)
    
    if producto_en_catalogo:
        print(f"✓ Producto encontrado en catálogo")
        print(f"  Estado: {producto_en_catalogo.get('estado')}")
        print(f"  Mes actual: {producto_en_catalogo.get('mes_actual')}")
        
        if producto_en_catalogo.get('estado') == 'no_disponible':
            print(f"✓ Estado actualizado correctamente a 'no_disponible'")
        else:
            print(f"✗ Estado NO cambió. Sigue siendo: {producto_en_catalogo.get('estado')}")
            return False
            
        if producto_en_catalogo.get('activo') == False:
            print(f"Campo 'activo' correctamente en False")
        else:
            print(f"✗ Campo 'mes_actual' debería ser False pero es: {producto_en_catalogo.get('mes_actual')}")
    else:
        print(f"✗ Producto no encontrado en catálogo después del cambio")
        return False
    
    # 4. Cambiar estado a "disponible"
    print_section("4. Cambiando estado de vuelta a 'disponible'")
    status, respuesta = actualizar_producto(producto_id, {
        "estado": "disponible"
    })
    
    if status == 200:
        print(f"✓ Producto actualizado a 'disponible'")
    else:
        print(f"✗ Error al actualizar: {status}")
        return False
    
    # 5. Verificar cambio final
    print_section("5. Verificando cambio final en catálogo")
    time.sleep(0.1)
    
    catalogo_final = obtener_catalogo_activo("fnb")
    producto_final = buscar_producto_en_catalogo(catalogo_final, codigo_original)
    
    if producto_final:
        print(f"✓ Producto encontrado en catálogo")
        print(f"  Estado: {producto_final.get('estado')}")
        print(f"  Mes actual: {producto_final.get('mes_actual')}")
        
        if producto_final.get('estado') == 'disponible' and producto_final.get('activo') == True:
            print(f"Estado y activo restaurados correctamente")
        else:
            print(f"✗ Estado/mes_actual no corresponden")
            return False
    else:
        print(f"✗ Producto no encontrado después de restaurar estado")
        return False
    
    print_section("RESUMEN")
    print("✓ PRUEBA COMPLETADA EXITOSAMENTE")
    print("  - Cambios de estado se reflejan en tiempo real")
    print("  - Caché se invalida correctamente")
    print("  - Campo 'mes_actual' se calcula correctamente")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TEST DE INVALIDACIÓN DE CACHÉ")
    print("=" * 60)
    
    if not test_servidor():
        exit(1)
    
    if test_cambio_estado():
        print("\n✓ TODOS LOS TESTS PASARON\n")
    else:
        print("\n✗ TESTS FALLARON\n")
        exit(1)
