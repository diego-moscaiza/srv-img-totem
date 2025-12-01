# Configuración de Base de Datos SQLite

## ¿Por qué SQLite?

- ✅ **Sin servidor externo** - No necesitas instalar PostgreSQL
- ✅ **Cero configuración** - Todo funciona automáticamente
- ✅ **Portátil** - Base de datos es un simple archivo `catalogos.db`
- ✅ **Desarrollo rápido** - Perfecto para prototipado y desarrollo
- ✅ **Perfecto para este proyecto** - Catálogos con datos relativamente estáticos

## Instalación (Super Fácil)

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- sqlalchemy==2.0.23
- fastapi y sus dependencias
- uvicorn para servir la aplicación

**Nota:** No necesitas psycopg2 ni PostgreSQL instalado

### 2. Ejecutar el Servidor

```bash
python main.py
```

¡Eso es todo! Deberías ver:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

La base de datos SQLite (`catalogos.db`) se creará automáticamente en el mismo directorio.

### 3. Acceder al Panel Admin

Una vez que el servidor esté ejecutándose, accede a:

```
http://localhost:8000/admin
```

Aquí puedes:
- ✅ Crear nuevos productos
- ✅ Ver todos los productos
- ✅ Editar productos existentes
- ✅ Eliminar productos

## Estructura de la Base de Datos

SQLite crea automáticamente una tabla `productos` con estos campos:

| Campo                    | Tipo    | Descripción                          |
| ------------------------ | ------- | ------------------------------------ |
| `id`                     | Integer | ID único                             |
| `codigo`                 | String  | Código del producto (único)          |
| `nombre`                 | String  | Nombre del producto                  |
| `descripcion`            | String  | Descripción adicional                |
| `precio`                 | Float   | Precio base                          |
| `categoria`              | String  | Categoría (celulares, laptops, etc.) |
| `imagen_listado`         | String  | Ruta de imagen para listado          |
| `imagen_caracteristicas` | String  | Ruta de imagen detallada             |
| `cuotas`                 | JSON    | Cuotas disponibles                   |
| `mes`                    | String  | Mes del catálogo                     |
| `ano`                    | Integer | Año del catálogo                     |
| `stock`                  | Boolean | Disponibilidad                       |

## Migración de Datos (Opcional)

Si tienes datos existentes en los archivos JSON y quieres importarlos a la base de datos, ejecuta:

```bash
python src/migrate_data.py
```

Este script leerá los archivos JSON y creará los registros en SQLite.

## Solución de Problemas

### El servidor no inicia

**Posible causa:** Ruta incorrecta al iniciar

**Solución:**
```bash
cd c:\ruta\a\srv-img-totem
python main.py
```

### Error al acceder a /admin

**Posible causa:** El servidor no está ejecutándose o URL incorrecta

**Solución:**
1. Verifica que veas `Application startup complete` en la consola
2. Usa la URL: `http://localhost:8000/admin`
3. Intenta: `http://127.0.0.1:8000/admin`

### Cambiar el archivo de base de datos

Por defecto la base de datos está en `catalogos.db`. Para cambiar la ubicación, edita `src/database.py`:

```python
# Cambiar esta línea:
DATABASE_URL = "sqlite:///./catalogos.db"

# A:
DATABASE_URL = "sqlite:///C:/ruta/completa/catalogo.db"
```

### Resetear la base de datos

Si necesitas empezar de cero:

```bash
# Windows
del catalogos.db

# Linux/Mac
rm catalogos.db
```

Luego reinicia el servidor y se creará una base de datos nueva.

## Endpoints Disponibles

### Panel Admin
- `GET /admin` - Panel de administración completo
- `GET /api/admin` - Panel directo (sin redirección)

### API CRUD de Productos
- `GET /api/productos` - Listar todos
- `GET /api/productos/{id}` - Obtener uno
- `POST /api/productos` - Crear nuevo
- `PUT /api/productos/{id}` - Actualizar
- `DELETE /api/productos/{id}` - Eliminar

### Endpoints de Catálogos (JSON)
- `GET /api/catalogo/activo` - Catálogo del mes actual
- `GET /api/catalogos/{año}/{mes}` - Catálogo específico
- `GET /api/categorias/{año}/{mes}` - Categorías disponibles
- `GET /api/meses-disponibles` - Listado de meses

### Endpoints de Imágenes
- `GET /imagen/{año}/{mes}/{categoría}/{nombre}` - Ver imagen específica
- `GET /ver/{nombre_archivo}` - Buscar imagen por nombre
- `GET /ver-ruta/{ruta}` - Ver imagen por ruta completa

## Migrar a PostgreSQL en el Futuro

Si en el futuro necesitas PostgreSQL (producción con múltiples usuarios):

1. **Exporta los datos:**
   ```bash
   python -c "from src.database import SessionLocal; ..."
   ```

2. **Instala PostgreSQL** y crea la base de datos

3. **Actualiza `src/database.py`:**
   ```python
   DATABASE_URL = "postgresql://usuario:password@localhost:5432/catalogos_db"
   ```

4. **Reinstala dependencias:**
   ```bash
   pip install psycopg2-binary
   ```

5. **Reinicia el servidor** - SQLAlchemy migrará automáticamente

## Notas Importantes

- Las imágenes se sirven desde `/static/` que mapea a la carpeta `imagenes/`
- Los PDFs están en `api/catalogos/`
- Los productos en SQLite son independientes de los JSON existentes
- Puedes usar ambos sistemas en paralelo (JSON + SQLite)
- SQLite es suficiente para catálogos con cientos de productos
- Para millones de registros, considera PostgreSQL
