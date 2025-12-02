#!/usr/bin/env python3
"""
Script para cargar productos desde el sistema de archivos a la base de datos
Lee las imágenes disponibles en imagenes/catalogos/ y crea registros en la BD

Uso:
  cd srv-img-totem
  python test/load_products_from_files.py
"""

import sys
from pathlib import Path
from datetime import datetime

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


def listar_opciones_disponibles():
    """Lista las opciones disponibles en el directorio de imágenes"""
    opciones = {"segmentos": {}, "años": set(), "meses": {}, "categorias": set()}

    for segmento_dir in sorted(IMAGENES_DIR.iterdir()):
        if not segmento_dir.is_dir():
            continue

        segmento = segmento_dir.name
        opciones["segmentos"][segmento] = []

        for ano_dir in sorted(segmento_dir.iterdir()):
            if not ano_dir.is_dir():
                continue

            ano = ano_dir.name
            opciones["años"].add(ano)
            opciones["segmentos"][segmento].append(ano)

            for mes_dir in sorted(ano_dir.iterdir()):
                if not mes_dir.is_dir():
                    continue

                mes_nombre = mes_dir.name
                clave_mes = f"{segmento}_{ano}_{mes_nombre}"
                opciones["meses"][clave_mes] = []

                for cat_dir in sorted(mes_dir.iterdir()):
                    if not cat_dir.is_dir():
                        continue

                    categoria_carpeta = cat_dir.name
                    categoria_nombre = CATEGORIA_MAP.get(
                        categoria_carpeta, categoria_carpeta
                    )
                    opciones["meses"][clave_mes].append(
                        (categoria_carpeta, categoria_nombre)
                    )
                    opciones["categorias"].add(categoria_nombre)

    return opciones


def cargar_productos():
    """Carga productos desde el sistema de archivos a la BD"""

    db = SessionLocal()
    productos_creados = 0

    try:
        print("=" * 80)
        print("CARGADOR INTERACTIVO DE PRODUCTOS")
        print("=" * 80)

        # Listar opciones disponibles
        opciones = listar_opciones_disponibles()

        # Seleccionar segmento
        print("\n📦 SEGMENTOS DISPONIBLES:")
        segmentos_list = list(opciones["segmentos"].keys())
        for i, seg in enumerate(segmentos_list, 1):
            print(f"   {i}. {seg}")

        while True:
            try:
                idx_seg = int(input("\nSelecciona segmento (número): ")) - 1
                if 0 <= idx_seg < len(segmentos_list):
                    segmento = segmentos_list[idx_seg]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Ingresa un número válido")

        # Seleccionar año
        años_disponibles = sorted(opciones["segmentos"][segmento])
        print(f"\n📅 AÑOS DISPONIBLES PARA {segmento}:")
        for i, ano in enumerate(años_disponibles, 1):
            print(f"   {i}. {ano}")

        while True:
            try:
                idx_ano = int(input("\nSelecciona año (número): ")) - 1
                if 0 <= idx_ano < len(años_disponibles):
                    ano = años_disponibles[idx_ano]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Ingresa un número válido")

        # Seleccionar mes
        meses_disponibles = [
            k for k in opciones["meses"].keys() if k.startswith(f"{segmento}_{ano}_")
        ]
        meses_disponibles.sort()

        print(f"\n📆 MESES DISPONIBLES PARA {segmento}/{ano}:")
        for i, mes_key in enumerate(meses_disponibles, 1):
            mes_nombre = mes_key.split("_", 2)[2]
            print(f"   {i}. {mes_nombre}")

        while True:
            try:
                idx_mes = int(input("\nSelecciona mes (número): ")) - 1
                if 0 <= idx_mes < len(meses_disponibles):
                    mes_key = meses_disponibles[idx_mes]
                    mes_nombre = mes_key.split("_", 2)[2]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Ingresa un número válido")

        # Seleccionar categoría(s)
        categorias_disponibles = opciones["meses"][mes_key]
        print(f"\n🏷️  CATEGORÍAS DISPONIBLES PARA {segmento}/{ano}/{mes_nombre}:")
        for i, (cat_carpeta, cat_nombre) in enumerate(categorias_disponibles, 1):
            print(f"   {i}. {cat_nombre}")
        print(f"   {len(categorias_disponibles) + 1}. Todas las categorías")

        while True:
            try:
                opcion = input(
                    "\nSelecciona categoría(s) (números separados por coma o 0 para todas): "
                ).strip()

                if opcion == "0" or opcion == str(len(categorias_disponibles) + 1):
                    categorias_seleccionadas = categorias_disponibles
                    break
                else:
                    indices = [int(x.strip()) - 1 for x in opcion.split(",")]
                    if all(0 <= idx < len(categorias_disponibles) for idx in indices):
                        categorias_seleccionadas = [
                            categorias_disponibles[idx] for idx in indices
                        ]
                        break
                    else:
                        print("❌ Opción inválida")
            except (ValueError, IndexError):
                print("❌ Ingresa números válidos separados por coma")

        # Confirmar selección
        print("\n" + "=" * 80)
        print("RESUMEN DE SELECCIÓN:")
        print(f"  Segmento: {segmento}")
        print(f"  Año: {ano}")
        print(f"  Mes: {mes_nombre}")
        print(
            f"  Categorías: {', '.join([cat[1] for cat in categorias_seleccionadas])}"
        )
        print("=" * 80)

        confirmar = input("\n¿Proceder con la carga? (s/n): ").lower().strip()
        if confirmar != "s":
            print("❌ Operación cancelada")
            return

        # Cargar productos
        print("\n🔄 Cargando productos...")

        ano_dir = IMAGENES_DIR / segmento / ano
        mes_dir = ano_dir / mes_nombre

        mes_texto = mes_nombre.split("-")[1] if "-" in mes_nombre else mes_nombre

        for cat_carpeta, categoria_nombre in categorias_seleccionadas:
            cat_dir = mes_dir / cat_carpeta
            precios_dir = cat_dir / "precios"

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

            for idx, img_precio in enumerate(imagenes_precios, 1):
                codigo = f"{segmento.upper()}-{ano}-{mes_nombre[:2]}-{cat_carpeta[:1]}-{idx:03d}"

                ruta_precio = img_precio.relative_to(IMAGENES_DIR.parent)

                existe = db.query(Producto).filter(Producto.codigo == codigo).first()
                if existe:
                    continue

                producto = Producto(
                    codigo=codigo,
                    nombre=f"{categoria_nombre.capitalize()} {idx}",
                    descripcion=f"{categoria_nombre.capitalize()} disponible en {mes_texto} {ano}",
                    precio=0.0,
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
                print(f"   ✓ {categoria_nombre}: {len(imagenes_precios)} productos")

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
    cargar_productos()
