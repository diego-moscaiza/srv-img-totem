#!/usr/bin/env python3
"""
Script de prueba para verificar que el CatalogoManager carga correctamente
los productos desde los archivos JSON y no devuelve datos hardcodeados
"""

import json
from catalogos_manager import catalogo_manager

print("=" * 80)
print("PRUEBA DE CARGA DE CATÁLOGOS DESDE JSON")
print("=" * 80)

# Prueba 1: Detectar catálogo actual
print("\n📅 PRUEBA 1: Detectar catálogo actual")
print("-" * 80)
catalogo_actual = catalogo_manager.detectar_catalogo_actual()
print(f"Año: {catalogo_actual['año']}")
print(f"Mes: {catalogo_actual['mes']}")
print(f"Ruta: {catalogo_actual['ruta_base']}")
print(f"Existe: {catalogo_actual['existe']}")

# Prueba 2: Obtener meses disponibles
print("\n📅 PRUEBA 2: Meses disponibles")
print("-" * 80)
meses = catalogo_manager.obtener_meses_disponibles()
print(f"Total de meses disponibles: {len(meses)}")
for mes_info in meses:
    print(
        f"  • {mes_info['año']}/{mes_info['mes']} - {mes_info['tiene_productos']} productos"
    )

# Prueba 3: Cargar catálogo del mes actual
print("\n📦 PRUEBA 3: Cargar catálogo actual (REAL desde JSON)")
print("-" * 80)
catalogo = catalogo_manager.cargar_catalogo_mes(
    catalogo_actual["año"], catalogo_actual["mes"]
)

print(f"\nCategorías encontradas: {list(catalogo.keys())}")

for categoria, productos in catalogo.items():
    print(f"\n🏷️ CATEGORÍA: {categoria}")
    print(f"   Total de productos: {len(productos)}")
    if productos:
        for i, producto in enumerate(productos[:2], 1):  # Mostrar solo los primeros 2
            print(f"\n   Producto {i}:")
            print(f"     ID: {producto.get('id', 'N/A')}")
            print(f"     Nombre: {producto.get('nombre', 'N/A')}")
            print(f"     Precio: {producto.get('precio', 'N/A')}")
            print(f"     Imagen: {producto.get('imagen', 'N/A')}")
            print(
                f"     Ruta imagen (relativa): {producto.get('ruta_imagen_relativa', 'N/A')}"
            )
            print(
                f"     Ruta imagen (absoluta): {producto.get('ruta_imagen_absoluta', 'N/A')}"
            )
            print(f"     Stock: {producto.get('stock', 'N/A')}")
            print(f"     Categoría: {producto.get('categoria', 'N/A')}")
        if len(productos) > 2:
            print(f"\n   ... y {len(productos) - 2} productos más")

# Prueba 4: Validar un producto específico
print("\n✅ PRUEBA 4: Validación de productos específicos")
print("-" * 80)

# Obtener el primer producto disponible para validar
producto_para_validar = None
categoria_para_validar = None

for categoria, productos in catalogo.items():
    if productos:
        producto_para_validar = productos[0]
        categoria_para_validar = categoria
        break

if producto_para_validar:
    producto_id = producto_para_validar.get("id")
    resultado = catalogo_manager.validar_producto(producto_id, categoria_para_validar)
    print(f"Validando: {producto_id} en categoría {categoria_para_validar}")
    print(f"Disponible: {resultado['disponible']}")
    if resultado["disponible"]:
        print(f"Producto encontrado: {resultado['producto']['nombre']}")
else:
    print("No hay productos disponibles para validar")

print("\n" + "=" * 80)
print("✨ PRUEBA COMPLETADA")
print("=" * 80)
