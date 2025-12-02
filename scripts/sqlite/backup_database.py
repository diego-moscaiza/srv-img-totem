#!/usr/bin/env python3
"""
Script para hacer backup de la base de datos SQLite
Crea una copia de la BD con timestamp

Uso:
  cd srv-img-totem
  python scripts/sqlite/backup_database.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def hacer_backup():
    """Hace un backup de la base de datos"""

    # Rutas
    proyecto_root = Path(__file__).parent.parent.parent
    db_path = proyecto_root / "catalogos.db"
    backup_dir = proyecto_root / "backups"

    try:
        print("=" * 80)
        print("BACKUP DE BASE DE DATOS")
        print("=" * 80)

        # Verificar que la BD existe
        if not db_path.exists():
            print(f"\n❌ Error: No se encontró la base de datos en {db_path}")
            return

        # Crear carpeta de backups si no existe
        backup_dir.mkdir(exist_ok=True)

        # Crear nombre del backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"catalogos_backup_{timestamp}.db"
        backup_path = backup_dir / backup_filename

        print(f"\n📁 Directorio de backups: {backup_dir}")
        print(f"📦 Base de datos actual: {db_path}")
        print(f"💾 Archivo de backup: {backup_filename}")

        # Obtener tamaño de la BD
        db_size = db_path.stat().st_size
        size_mb = db_size / (1024 * 1024)
        print(f"📊 Tamaño de BD: {size_mb:.2f} MB")

        # Crear backup
        print("\n🔄 Creando backup...")
        shutil.copy2(db_path, backup_path)

        # Verificar que el backup se creó
        if backup_path.exists():
            backup_size = backup_path.stat().st_size
            backup_size_mb = backup_size / (1024 * 1024)
            print(f"✅ Backup creado exitosamente")
            print(f"   Ruta: {backup_path}")
            print(f"   Tamaño: {backup_size_mb:.2f} MB")

            print("\n" + "=" * 80)
            print("✅ BACKUP COMPLETADO")
            print("=" * 80)
        else:
            print(f"❌ Error: No se pudo crear el backup")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


def listar_backups():
    """Lista todos los backups disponibles"""

    proyecto_root = Path(__file__).parent.parent.parent
    backup_dir = proyecto_root / "backups"

    if not backup_dir.exists():
        print("📁 No hay carpeta de backups aún")
        return

    backups = sorted(backup_dir.glob("catalogos_backup_*.db"), reverse=True)

    if not backups:
        print("📁 No hay backups disponibles")
        return

    print("\n" + "=" * 80)
    print("BACKUPS DISPONIBLES")
    print("=" * 80)

    for i, backup_file in enumerate(backups, 1):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        fecha_mod = datetime.fromtimestamp(backup_file.stat().st_mtime)
        print(f"\n{i}. {backup_file.name}")
        print(f"   Tamaño: {size_mb:.2f} MB")
        print(f"   Fecha: {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    hacer_backup()
    listar_backups()
