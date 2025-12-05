#!/usr/bin/env python3
"""
Script para cargar productos AUTOMÁTICAMENTE desde archivos JSON e imágenes.

Este script:
1. Escanea la estructura imagenes/catalogos/{segmento}/{año}/{mes}/{categoria}/
2. Lee archivos JSON de la carpeta json/ 
3. Relaciona cada JSON con su imagen correspondiente en precios/ (01.json → 01.png/jpg)
4. Opcionalmente vincula con imagen de caracteristicas/ si existe
5. Carga todo a la base de datos SQLite

Uso:
  cd srv-img-totem
  python test/load_from_json.py
  
  # O con opciones:
  python test/load_from_json.py --segmento fnb --limpiar
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
import argparse
from sqlalchemy import cast, String, Integer

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, Producto, Base, engine
from src.config import SERVER_URL

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Configuración
IMAGENES_DIR = Path(__file__).parent.parent / "imagenes" / "catalogos"

def construir_url_imagen(ruta_relativa: str | None) -> str | None:
    """Construye URL absoluta para una imagen desde su ruta relativa"""
    if not ruta_relativa:
        return None
    server_url = SERVER_URL.rstrip("/")
    ruta_limpia = ruta_relativa.lstrip("/")
    return f"{server_url}/api/catalogos/{ruta_limpia}"

# Mapeo de categorías por carpeta
CATEGORIA_MAP = {
    # FNB
    "1-celulares": "celulares",
    "2-laptops": "laptops",
    "3-televisores": "televisores",
    "4-refrigeradoras": "refrigeradoras",
    "5-lavadoras": "lavadoras",
    # GASO
    "2-televisores": "televisores",
    "3-refrigeradores": "refrigeradores",
    "4-lavadoras": "lavadoras",
    "5-fusion": "fusion",
}

# Extensiones de imagen soportadas
EXTENSIONES_IMAGEN = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.PNG', '.JPG', '.JPEG', '.GIF', '.WEBP']


def extraer_precio_numerico(precio_str: str) -> float:
    """
    Extrae el valor numérico de un string de precio como 'S/. 4599' o 'S/. 4599.00'
    
    - Si el precio tiene decimales, los mantiene: 'S/. 4599.99' → 4599.99
    - Si el precio NO tiene decimales: 'S/. 4599' → 4599.0
    
    Args:
        precio_str: String con el precio (ej: "S/. 4999", "S/. 2999.50")
    
    Returns:
        float: Precio como número decimal (ej: 4999.0, 2999.5)
    """
    if not precio_str:
        return 0.0
    
    # Primero eliminar el símbolo de moneda "S/." o "S/" para evitar confusión con el punto
    precio_limpio = precio_str.replace('S/.', '').replace('S/', '').strip()
    
    # Reemplazar comas por nada si son separadores de miles (ej: 4,599 → 4599)
    # O por punto si es separador decimal (ej: 4599,50 → 4599.50)
    if ',' in precio_limpio:
        # Si hay punto Y coma, la coma es separador de miles
        if '.' in precio_limpio:
            precio_limpio = precio_limpio.replace(',', '')
        else:
            # Si solo hay coma, podría ser separador decimal
            # Verificar si hay más de 2 dígitos después de la coma (miles) o no (decimal)
            partes = precio_limpio.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # Es separador decimal
                precio_limpio = precio_limpio.replace(',', '.')
            else:
                # Es separador de miles
                precio_limpio = precio_limpio.replace(',', '')
    
    # Remover cualquier caracter que no sea número o punto decimal
    numeros = re.sub(r'[^\d.]', '', precio_limpio)
    
    # Si hay múltiples puntos (ej: 4.599.00), el último es decimal
    if numeros.count('.') > 1:
        partes = numeros.rsplit('.', 1)
        numeros = partes[0].replace('.', '') + '.' + partes[1]
    
    try:
        precio = float(numeros)
        return round(precio, 2)
    except ValueError:
        return 0.0


def buscar_imagen_por_numero(carpeta: Path, numero: str) -> Path | None:
    """Busca una imagen con el número dado en cualquier extensión soportada"""
    if not carpeta.exists():
        return None
    
    for ext in EXTENSIONES_IMAGEN:
        imagen = carpeta / f"{numero}{ext}"
        if imagen.exists():
            return imagen
    
    return None


def cargar_productos_desde_json(
    segmento_filtro: str | None = None,
    ano_filtro: str | None = None,
    mes_filtro: str | None = None,
    limpiar_antes: bool = False,
    solo_nuevos: bool = True
):
    """
    Carga productos desde archivos JSON relacionándolos con imágenes.
    
    Args:
        segmento_filtro: Filtrar por segmento específico (fnb, gaso)
        ano_filtro: Filtrar por año específico (2025)
        mes_filtro: Filtrar por mes específico (12-diciembre)
        limpiar_antes: Si True, elimina productos existentes antes de cargar
        solo_nuevos: Si True, solo carga productos que no existen (por código)
    """
    db = SessionLocal()
    productos_creados = 0
    productos_actualizados = 0
    productos_omitidos = 0
    errores = []

    try:
        print("=" * 80)
        print("🚀 CARGA AUTOMÁTICA DE PRODUCTOS DESDE JSON")
        print("=" * 80)
        print(f"📂 Directorio base: {IMAGENES_DIR}")
        print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if limpiar_antes:
            print("🗑️  Eliminando productos existentes...")
            db.query(Producto).delete()
            db.commit()
            print("   ✓ Productos eliminados")
            print()

        # Verificar que existe el directorio
        if not IMAGENES_DIR.exists():
            print(f"❌ ERROR: No existe el directorio {IMAGENES_DIR}")
            return

        # Iterar sobre segmentos
        for segmento_dir in sorted(IMAGENES_DIR.iterdir()):
            if not segmento_dir.is_dir():
                continue

            segmento = segmento_dir.name  # fnb, gaso
            
            # Filtrar por segmento si se especificó
            if segmento_filtro and segmento != segmento_filtro:
                continue

            print(f"📦 SEGMENTO: {segmento.upper()}")

            # Iterar sobre años
            for ano_dir in sorted(segmento_dir.iterdir()):
                if not ano_dir.is_dir():
                    continue

                ano = ano_dir.name
                
                # Filtrar por año si se especificó
                if ano_filtro and ano != ano_filtro:
                    continue

                # Iterar sobre meses
                for mes_dir in sorted(ano_dir.iterdir()):
                    if not mes_dir.is_dir():
                        continue

                    mes_carpeta = mes_dir.name  # "12-diciembre"
                    
                    # Filtrar por mes si se especificó
                    if mes_filtro and mes_carpeta != mes_filtro:
                        continue
                    
                    # Extraer nombre del mes
                    mes_texto = mes_carpeta.split("-")[1] if "-" in mes_carpeta else mes_carpeta

                    print(f"\n   📅 {ano}/{mes_carpeta}")

                    # Iterar sobre categorías
                    for cat_dir in sorted(mes_dir.iterdir()):
                        if not cat_dir.is_dir():
                            continue

                        categoria_carpeta = cat_dir.name  # "1-celulares", "2-laptops", etc.
                        categoria_nombre = CATEGORIA_MAP.get(categoria_carpeta, categoria_carpeta.split("-")[-1])

                        # Carpetas de datos
                        json_dir = cat_dir / "json"
                        precios_dir = cat_dir / "precios"
                        caracteristicas_dir = cat_dir / "caracteristicas"

                        # Verificar que existe la carpeta json
                        if not json_dir.exists():
                            continue

                        # Obtener archivos JSON ordenados
                        archivos_json = sorted(json_dir.glob("*.json"))
                        
                        if not archivos_json:
                            continue

                        productos_categoria = 0

                        for json_file in archivos_json:
                            try:
                                # Extraer número del archivo (01, 02, etc.)
                                numero = json_file.stem  # "01", "02", etc.

                                # Leer datos del JSON
                                with open(json_file, 'r', encoding='utf-8') as f:
                                    datos = json.load(f)

                                # Extraer campos del JSON
                                codigo = datos.get('codigo', f"{segmento.upper()}-{categoria_carpeta}-{numero}")
                                nombre = datos.get('producto', datos.get('nombre', f"Producto {numero}"))
                                descripcion = datos.get('descripcion', '')
                                precio_str = datos.get('precio', '0')
                                precio = extraer_precio_numerico(precio_str)
                                cuotas = datos.get('cuotas', {})
                                marca = datos.get('marca', '')
                                beneficios = datos.get('beneficios', [])
                                
                                # Si hay marca, agregarla a la descripción
                                if marca and marca not in descripcion:
                                    descripcion = f"{marca} - {descripcion}" if descripcion else marca

                                # Buscar imagen de precios (se asigna automáticamente)
                                imagen_precio = buscar_imagen_por_numero(precios_dir, numero)
                                
                                # Las imágenes de características NO se asignan automáticamente
                                # El usuario las selecciona manualmente desde el panel admin
                                # Solo construimos la ruta de precios

                                # Construir URLs absolutas para las imágenes
                                # El frontend espera URLs completas como http://192.168.5.85:8000/api/catalogos/fnb/2025/...
                                url_precio = None

                                if imagen_precio:
                                    ruta_relativa = str(imagen_precio.relative_to(IMAGENES_DIR)).replace("\\", "/")
                                    url_precio = construir_url_imagen(ruta_relativa)

                                # Verificar si el producto ya existe
                                producto_existente = db.query(Producto).filter(
                                    Producto.codigo == codigo
                                ).first()

                                if producto_existente:
                                    if solo_nuevos:
                                        productos_omitidos += 1
                                        continue
                                    else:
                                        # Actualizar producto existente (NO actualiza imagen_caracteristicas)
                                        producto_existente.nombre = nombre
                                        producto_existente.descripcion = descripcion
                                        producto_existente.precio = precio
                                        producto_existente.categoria = categoria_nombre
                                        producto_existente.imagen_listado = url_precio
                                        # imagen_caracteristicas NO se actualiza automáticamente
                                        producto_existente.cuotas = cuotas
                                        producto_existente.mes = mes_texto
                                        producto_existente.ano = int(ano)
                                        producto_existente.segmento = segmento
                                        productos_actualizados += 1
                                        productos_categoria += 1
                                        continue

                                # Crear nuevo producto (imagen_caracteristicas queda vacía)
                                producto = Producto(
                                    codigo=codigo,
                                    nombre=nombre,
                                    descripcion=descripcion,
                                    precio=precio,
                                    categoria=categoria_nombre,
                                    imagen_listado=url_precio,
                                    imagen_caracteristicas=None,  # Se asigna manualmente desde admin
                                    cuotas=cuotas,
                                    mes=mes_texto,
                                    ano=int(ano),
                                    segmento=segmento,
                                    estado="disponible",
                                    stock=True,
                                )

                                db.add(producto)
                                productos_creados += 1
                                productos_categoria += 1

                            except json.JSONDecodeError as e:
                                errores.append(f"Error JSON en {json_file}: {e}")
                            except Exception as e:
                                errores.append(f"Error procesando {json_file}: {e}")

                        if productos_categoria > 0:
                            print(f"      ✓ {categoria_nombre}: {productos_categoria} productos")

        # Guardar cambios
        db.commit()

        # Resumen final
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE CARGA")
        print("=" * 80)
        print(f"   ✅ Productos creados:     {productos_creados}")
        print(f"   🔄 Productos actualizados: {productos_actualizados}")
        print(f"   ⏭️  Productos omitidos:    {productos_omitidos}")
        
        if errores:
            print(f"\n   ⚠️  Errores encontrados: {len(errores)}")
            for error in errores[:5]:  # Mostrar máximo 5 errores
                print(f"      - {error}")
            if len(errores) > 5:
                print(f"      ... y {len(errores) - 5} más")

        print("=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Carga automática de productos desde archivos JSON"
    )
    parser.add_argument(
        "--segmento", "-s",
        type=str,
        help="Filtrar por segmento (fnb, gaso)"
    )
    parser.add_argument(
        "--ano", "-a",
        type=str,
        help="Filtrar por año (2025)"
    )
    parser.add_argument(
        "--mes", "-m",
        type=str,
        help="Filtrar por mes (12-diciembre)"
    )
    parser.add_argument(
        "--limpiar", "-l",
        action="store_true",
        help="Eliminar todos los productos antes de cargar"
    )
    parser.add_argument(
        "--actualizar", "-u",
        action="store_true",
        help="Actualizar productos existentes (por defecto solo crea nuevos)"
    )

    args = parser.parse_args()

    cargar_productos_desde_json(
        segmento_filtro=args.segmento,
        ano_filtro=args.ano,
        mes_filtro=args.mes,
        limpiar_antes=args.limpiar,
        solo_nuevos=not args.actualizar
    )


if __name__ == "__main__":
    main()
