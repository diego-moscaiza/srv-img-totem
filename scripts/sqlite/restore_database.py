#!/usr/bin/env python3
"""
Script para restaurar la base de datos desde un backup
Permite seleccionar el backup a restaurar

Uso:
  cd srv-img-totem
  python scripts/sqlite/restore_database.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def listar_backups():
    """Lista todos los backups disponibles"""

    proyecto_root = Path(__file__).parent.parent.parent
    backup_dir = proyecto_root / "backups"

    if not backup_dir.exists():
        return []

    backups = sorted(backup_dir.glob("catalogos_backup_*.db"), reverse=True)
    return backups


def restaurar_backup():
    """Restaura la base de datos desde un backup"""

    proyecto_root = Path(__file__).parent.parent.parent
    db_path = proyecto_root / "catalogos.db"

    try:
        print("=" * 80)
        print("RESTAURAR BASE DE DATOS DESDE BACKUP")
        print("=" * 80)

        # Listar backups disponibles
        backups = listar_backups()

        if not backups:
            print("\n❌ No hay backups disponibles")
            return

        print("\n📁 BACKUPS DISPONIBLES:")
        for i, backup_file in enumerate(backups, 1):
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            fecha_mod = datetime.fromtimestamp(backup_file.stat().st_mtime)
            print(f"\n   {i}. {backup_file.name}")
            print(f"      Tamaño: {size_mb:.2f} MB")
            print(f"      Fecha: {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')}")

        # Seleccionar backup
        while True:
            try:
                idx = int(input("\nSelecciona el backup a restaurar (número): ")) - 1
                if 0 <= idx < len(backups):
                    backup_seleccionado = backups[idx]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Ingresa un número válido")

        print("\n" + "=" * 80)
        print("CONFIRMACIÓN DE RESTAURACIÓN")
        print("=" * 80)
        print(f"\n⚠️  ADVERTENCIA: Esta operación REEMPLAZARÁ la base de datos actual")
        print(f"\nBackup a restaurar: {backup_seleccionado.name}")
        print(f"BD actual: {db_path}")
        print("\nEsta acción NO SE PUEDE DESHACER (a menos que tengas otro backup)")

        confirmacion = (
            input(
                "\n¿Estás seguro de que deseas restaurar este backup? (escribe 'sí' para confirmar): "
            )
            .strip()
            .lower()
        )

        if confirmacion != "sí":
            print("\n❌ Operación cancelada")
            return

        # Crear backup de la BD actual antes de restaurar (si existe)
        if db_path.exists():
            print("\n🔄 Creando backup de seguridad de la BD actual...")
            backup_dir = proyecto_root / "backups"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_seguridad = (
                backup_dir / f"catalogos_backup_antes_restaurar_{timestamp}.db"
            )
            shutil.copy2(db_path, backup_seguridad)
            print(f"✅ Backup de seguridad creado: {backup_seguridad.name}")

        # Restaurar el backup
        print(f"\n🔄 Restaurando {backup_seleccionado.name}...")
        shutil.copy2(backup_seleccionado, db_path)

        # Verificar que la restauración fue exitosa
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Base de datos restaurada exitosamente")
            print(f"   Ruta: {db_path}")
            print(f"   Tamaño: {size_mb:.2f} MB")

            print("\n" + "=" * 80)
            print("✅ RESTAURACIÓN COMPLETADA")
            print("=" * 80)
        else:
            print(f"❌ Error: No se pudo restaurar la base de datos")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    restaurar_backup()
