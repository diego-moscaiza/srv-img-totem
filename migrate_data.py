import json
import sys
from pathlib import Path
from database import SessionLocal, Producto

try:
    from sqlalchemy.exc import IntegrityError
except ImportError:
    # Fallback si sqlalchemy no está instalado
    class IntegrityError(Exception):
        pass

def migrate_json_to_db():
    """
    Migra datos de archivos JSON a la base de datos PostgreSQL
    """
    db = SessionLocal()
    
    try:
        # Directorio base de catálogos
        catalogs_dir = Path("api/catalogos")
        
        if not catalogs_dir.exists():
            print(f"❌ Directorio {catalogs_dir} no encontrado")
            return
        
        # Buscar todos los archivos JSON
        json_files = list(catalogs_dir.rglob("*.json"))
        
        if not json_files:
            print("❌ No se encontraron archivos JSON")
            return
        
        print(f"✅ Se encontraron {len(json_files)} archivos JSON")
        
        products_added = 0
        products_skipped = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Procesar cada producto en el JSON
                productos = data if isinstance(data, list) else data.get('productos', [])
                
                for prod in productos:
                    try:
                        # Crear objeto Producto
                        nuevo_producto = Producto(
                            codigo=prod.get('codigo'),
                            nombre=prod.get('nombre'),
                            descripcion=prod.get('descripcion', ''),
                            precio=float(prod.get('precio', 0)),
                            categoria=prod.get('categoria', ''),
                            imagen_listado=prod.get('imagen_listado', ''),
                            imagen_caracteristicas=prod.get('imagen_caracteristicas', ''),
                            cuotas=prod.get('cuotas', {}),
                            mes=prod.get('mes', ''),
                            ano=int(prod.get('ano', 2025)),
                            stock=prod.get('stock', True)
                        )
                        
                        db.add(nuevo_producto)
                        db.commit()
                        db.refresh(nuevo_producto)
                        
                        print(f"✅ Agregado: {prod.get('codigo')} - {prod.get('nombre')}")
                        products_added += 1
                        
                    except (IntegrityError, Exception) as e:
                        db.rollback()
                        if isinstance(e, IntegrityError) or "unique" in str(e).lower():
                            print(f"⚠️  Duplicado (omitido): {prod.get('codigo')} - {prod.get('nombre')}")
                        else:
                            print(f"❌ Error en {prod.get('codigo')}: {str(e)}")
                        products_skipped += 1
                        
            except json.JSONDecodeError:
                print(f"❌ Error al leer JSON: {json_file}")
            except Exception as e:
                print(f"❌ Error procesando {json_file}: {str(e)}")
        
        print("\n" + "="*50)
        print(f"📊 Migración completada:")
        print(f"   ✅ Productos agregados: {products_added}")
        print(f"   ⚠️  Productos omitidos: {products_skipped}")
        print(f"   📁 Total procesado: {products_added + products_skipped}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Iniciando migración de JSON a PostgreSQL...")
    print()
    migrate_json_to_db()
