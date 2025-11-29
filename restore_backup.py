#!/usr/bin/env python
"""Script para restaurar datos del backup y asignar segmentos"""

import json
from pathlib import Path
from src.database import SessionLocal, Producto, Base, engine

# Crear las tablas con la nueva estructura
Base.metadata.create_all(bind=engine)

# Cargar backup
backup_path = Path("backup_productos.json")
if not backup_path.exists():
    print("❌ No se encontró backup_productos.json")
    exit(1)

with open(backup_path, "r", encoding="utf-8") as f:
    productos_backup = json.load(f)

print(f"📦 Cargados {len(productos_backup)} productos del backup")

# Restaurar con asignación de segmento
db = SessionLocal()

for prod in productos_backup:
    # Determinar segmento basado en código o por defecto fnb
    codigo = prod.get("codigo", "")

    # Puedes agregar lógica aquí para determinar el segmento
    # Por ahora, todos van a fnb por defecto
    segmento = "fnb"

    nuevo_producto = Producto(
        codigo=prod.get("codigo"),
        nombre=prod.get("nombre"),
        descripcion=prod.get("descripcion"),
        precio=prod.get("precio"),
        categoria=prod.get("categoria"),
        imagen_listado=prod.get("imagen_listado"),
        imagen_caracteristicas=prod.get("imagen_caracteristicas"),
        cuotas=prod.get("cuotas"),
        mes=prod.get("mes"),
        ano=prod.get("ano"),
        segmento=segmento,
        estado="disponible",
        stock=prod.get("stock", True),
    )

    try:
        db.add(nuevo_producto)
    except Exception as e:
        print(f"⚠️ Error al agregar {codigo}: {e}")

db.commit()
db.close()

print("✅ Productos restaurados exitosamente")
print(f"Total restaurado: {len(productos_backup)} productos")
