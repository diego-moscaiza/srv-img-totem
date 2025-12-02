"""
Script de creación de la base de datos SQLite para el sistema de catálogos
Este script crea la tabla 'productos' con la estructura completa y actualizada
"""

import sqlite3
import os
from pathlib import Path

# Determinar ruta de BD: usar volumen persistente en Docker, o carpeta local en desarrollo
if os.path.exists("/srv/data"):
    DB_PATH = "/srv/data/catalogos.db"
else:
    DB_PATH = "catalogos.db"

# Crear directorio si no existe
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def create_database():
    """Crea la base de datos y la tabla productos con la estructura completa"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("🔄 Creando base de datos y tabla 'productos'...")

        # Verificar si la tabla ya existe
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='productos'
        """
        )
        table_exists = cursor.fetchone()

        if table_exists:
            print("⚠️  La tabla 'productos' ya existe")
            cursor.execute("SELECT COUNT(*) FROM productos")
            count = cursor.fetchone()[0]
            print(f"📊 Registros actuales: {count}")

            response = input(
                "\n¿Deseas recrear la tabla? Esto eliminará todos los datos (s/N): "
            )
            if response.lower() != "s":
                print("❌ Operación cancelada")
                return

            print("🗑️  Eliminando tabla existente...")
            cursor.execute("DROP TABLE productos")

        # Crear tabla con la estructura completa
        cursor.execute(
            """
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                descripcion VARCHAR(500),
                precio FLOAT NOT NULL,
                categoria VARCHAR(100) NOT NULL,
                imagen_listado VARCHAR(500),
                imagen_caracteristicas VARCHAR(500),
                imagen_caracteristicas_2 VARCHAR(500) DEFAULT NULL,
                cuotas JSON,
                mes VARCHAR(20) NOT NULL,
                ano INTEGER NOT NULL,
                segmento VARCHAR(50) DEFAULT 'fnb' NOT NULL,
                estado VARCHAR(50) DEFAULT 'disponible' NOT NULL,
                stock BOOLEAN DEFAULT 1
            )
        """
        )

        # Crear índices para mejorar el rendimiento
        cursor.execute("CREATE UNIQUE INDEX idx_codigo ON productos(codigo)")
        cursor.execute("CREATE INDEX idx_segmento ON productos(segmento)")
        cursor.execute("CREATE INDEX idx_estado ON productos(estado)")
        cursor.execute("CREATE INDEX idx_categoria ON productos(categoria)")
        cursor.execute("CREATE INDEX idx_mes_ano ON productos(mes, ano)")

        conn.commit()

        print("✓ Tabla 'productos' creada exitosamente")

        # Mostrar estructura final
        cursor.execute("PRAGMA table_info(productos)")
        columns_info = cursor.fetchall()

        print("\n📋 Estructura de la tabla 'productos':")
        for col in columns_info:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            default = f" DEFAULT {col[4]}" if col[4] else ""
            print(f"  {col[0]:2d}. {col[1]:30s} {col[2]:15s} {nullable}{default}")

        # Mostrar índices
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='productos'
        """
        )
        indices = cursor.fetchall()

        print("\n🔑 Índices creados:")
        for idx in indices:
            if not idx[0].startswith("sqlite_"):  # Excluir índices automáticos
                print(f"  - {idx[0]}")

        print(f"\n✓ Base de datos creada en: {os.path.abspath(DB_PATH)}")

    except Exception as e:
        print(f"❌ Error durante la creación: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("SCRIPT DE CREACIÓN DE BASE DE DATOS - Sistema de Catálogos")
    print("=" * 70)
    create_database()
    print("=" * 70)
    print("✓ Proceso completado exitosamente")
