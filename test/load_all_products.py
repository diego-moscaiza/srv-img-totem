#!/usr/bin/env python3
"""
Script para cargar TODOS los productos desde el sistema de archivos a la BD
Lee las imágenes disponibles en imagenes/catalogos/ y crea registros en la BD

Uso:
  cd srv-img-totem
  python test/load_all_products.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, Producto, Base, engine

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Configuración
IMAGENES_DIR = Path(__file__).parent.parent / "imagenes" / "catalogos"

# Mapeo de categorías
CATEGORIA_MAP = {
    "1-celulares": "celulares",
    "2-laptops": "laptops",
    "3-televisores": "televisores",
    "4-refrigeradoras": "refrigeradoras",
    "5-lavadoras": "lavadoras",
    "3-refrigeradores": "refrigeradores",  # Para GASO
    "5-fusion": "fusion",  # Para GASO
}


def cargar_todos_productos():
    """Carga TODOS los productos desde el sistema de archivos a la BD"""

    db = SessionLocal()
    productos_creados = 0

    try:
        print("=" * 80)
        print("CARGANDO TODOS LOS PRODUCTOS DESDE ARCHIVOS A LA BASE DE DATOS")
        print("=" * 80)

        # Iterar sobre segmentos
        for segmento_dir in sorted(IMAGENES_DIR.iterdir()):
            if not segmento_dir.is_dir():
                continue

            segmento = segmento_dir.name  # fnb, gaso
            print(f"\n📦 SEGMENTO: {segmento}")

            # Iterar sobre años
            for ano_dir in sorted(segmento_dir.iterdir()):
                if not ano_dir.is_dir():
                    continue

                ano = ano_dir.name

                # Iterar sobre meses
                for mes_dir in sorted(ano_dir.iterdir()):
                    if not mes_dir.is_dir():
                        continue

                    mes_nombre = mes_dir.name  # "11-noviembre", "12-diciembre"
                    mes_texto = (
                        mes_nombre.split("-")[1] if "-" in mes_nombre else mes_nombre
                    )

                    print(f"\n   📅 {mes_nombre}")

                    # Iterar sobre categorías
                    for cat_dir in sorted(mes_dir.iterdir()):
                        if not cat_dir.is_dir():
                            continue

                        categoria_carpeta = (
                            cat_dir.name
                        )  # "1-celulares", "2-laptops", etc.
                        categoria_nombre = CATEGORIA_MAP.get(
                            categoria_carpeta, categoria_carpeta
                        )

                        # Buscar imágenes SOLO en carpeta precios/
                        precios_dir = cat_dir / "precios"

                        # Obtener imágenes de precios (cualquier formato)
                        imagenes_precios = []
                        if precios_dir.exists():
                            imagenes_precios = sorted(
                                list(precios_dir.glob("*.png")) + 
                                list(precios_dir.glob("*.jpg")) + 
                                list(precios_dir.glob("*.jpeg")) + 
                                list(precios_dir.glob("*.JPG")) + 
                                list(precios_dir.glob("*.JPEG")) +
                                list(precios_dir.glob("*.gif")) +
                                list(precios_dir.glob("*.webp"))
                            )

                        # Crear un producto por cada imagen de precios
                        for idx, img_precio in enumerate(imagenes_precios, 1):
                            codigo = f"{segmento.upper()}-{ano}-{mes_nombre[:2]}-{categoria_carpeta[:1]}-{idx:03d}"

                            # Obtener ruta relativa desde imagenes/
                            ruta_precio = img_precio.relative_to(IMAGENES_DIR.parent)

                            # Verificar si el producto ya existe
                            existe = (
                                db.query(Producto)
                                .filter(Producto.codigo == codigo)
                                .first()
                            )
                            if existe:
                                continue

                            # Crear producto
                            producto = Producto(
                                codigo=codigo,
                                nombre=f"{categoria_nombre.capitalize()} {idx}",
                                descripcion=f"{categoria_nombre.capitalize()} disponible en {mes_texto} {ano}",
                                precio=0.0,  # Sin precio por defecto
                                categoria=categoria_nombre,
                                imagen_listado=str(ruta_precio),
                                imagen_caracteristicas=str(ruta_precio),
                                cuotas=None,
                                mes=mes_texto,
                                ano=ano,
                                segmento=segmento,
                                estado="disponible",
                                stock=True,
                            )

                            db.add(producto)
                            productos_creados += 1

                        if imagenes_precios:
                            print(
                                f"      ✓ {categoria_nombre}: {len(imagenes_precios)} productos"
                            )

        db.commit()

        print("\n" + "=" * 80)
        print(f"✅ PROCESO COMPLETADO: {productos_creados} productos cargados")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    cargar_todos_productos()
