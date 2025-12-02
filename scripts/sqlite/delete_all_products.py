#!/usr/bin/env python3
"""
Script para borrar TODOS los productos de la base de datos
ADVERTENCIA: Esta acción no se puede deshacer

Uso:
  cd srv-img-totem
  python scripts/sqlite/delete_all_products.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import SessionLocal, Producto


def borrar_todos_productos():
    """Borra TODOS los productos de la base de datos"""

    db = SessionLocal()

    try:
        print("=" * 80)
        print("BORRADOR DE PRODUCTOS - BASE DE DATOS")
        print("=" * 80)

        # Contar productos existentes
        total_productos = db.query(Producto).count()

        if total_productos == 0:
            print("\n⚠️  No hay productos en la base de datos")
            print("=" * 80)
            return

        print(f"\n⚠️  ADVERTENCIA: Hay {total_productos} productos en la base de datos")
        print("\nEsta acción BORRARÁ PERMANENTEMENTE todos los productos.")
        print("Esta acción NO SE PUEDE DESHACER.")

        # Pedir confirmación
        confirmacion = (
            input(
                "\n¿Estás seguro de que deseas borrar TODOS los productos? (escribe 'sí' para confirmar): "
            )
            .strip()
            .lower()
        )

        if confirmacion != "sí":
            print("\n❌ Operación cancelada")
            return

        # Segunda confirmación
        confirmacion2 = input("Confirma nuevamente escribiendo 'BORRAR TODO': ").strip()

        if confirmacion2 != "BORRAR TODO":
            print("\n❌ Operación cancelada")
            return

        print("\n🔄 Borrando todos los productos...")

        # Borrar todos los productos
        db.query(Producto).delete()
        db.commit()

        print("\n" + "=" * 80)
        print(f"✅ PROCESO COMPLETADO: {total_productos} productos borrados")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    borrar_todos_productos()
