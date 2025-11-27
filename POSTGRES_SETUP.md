# Configuración de PostgreSQL

## Requisitos
- PostgreSQL instalado y ejecutándose en tu sistema
- Acceso a línea de comandos (psql)

## Pasos de Instalación

### 1. Crear la Base de Datos y Usuario

Abre una terminal/PowerShell con permisos de administrador y conectate a PostgreSQL:

```bash
psql -U postgres
```

Luego ejecuta los siguientes comandos SQL:

```sql
-- Crear usuario (reemplaza 'tucontraseña' con una contraseña segura)
CREATE USER usuario WITH PASSWORD 'tucontraseña';

-- Crear base de datos
CREATE DATABASE catalogos_db OWNER usuario;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE catalogos_db TO usuario;

-- Salir
\q
```

### 2. Actualizar las Credenciales en database.py

Abre `database.py` y actualiza la línea:

```python
DATABASE_URL = "postgresql://usuario:tucontraseña@localhost:5432/catalogos_db"
```

Reemplaza:
- `usuario` - el nombre de usuario que creaste
- `tucontraseña` - la contraseña que asignaste
- `localhost` - si es en otra máquina, cambia por el host
- `5432` - puerto PostgreSQL (por defecto es 5432)
- `catalogos_db` - nombre de la base de datos

### 3. Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

Esto instalará:
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- fastapi y sus dependencias

### 4. Verificar la Conexión

Ejecuta el servidor:

```bash
python main.py
```

Deberías ver:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Si hay un error de conexión, verifica:
1. PostgreSQL está ejecutándose: `psql -U usuario -d catalogos_db -c "SELECT 1;"`
2. Las credenciales en `database.py` son correctas
3. El usuario tiene permisos en la base de datos

### 5. Acceder al Panel Admin

Una vez que el servidor esté ejecutándose, accede a:

```
http://localhost:8000/admin
```

Aquí puedes:
- ✅ Crear nuevos productos
- ✅ Ver todos los productos
- ✅ Editar productos existentes
- ✅ Eliminar productos

## Migración de Datos (Opcional)

Si tienes datos existentes en los archivos JSON y quieres importarlos a la base de datos, ejecuta:

```bash
python migrate_data.py
```

Este script leerá los archivos JSON y creará los registros en PostgreSQL.

## Solución de Problemas

### Error: "psycopg2.OperationalError: FATAL: role 'usuario' does not exist"

Asegúrate de haber creado el usuario en PostgreSQL:

```sql
CREATE USER usuario WITH PASSWORD 'contraseña';
```

### Error: "psycopg2.OperationalError: FATAL: database 'catalogos_db' does not exist"

Asegúrate de haber creado la base de datos:

```sql
CREATE DATABASE catalogos_db OWNER usuario;
```

### Error: "permission denied for schema public"

Otorga los permisos correctamente:

```sql
GRANT ALL ON SCHEMA public TO usuario;
GRANT ALL ON ALL TABLES IN SCHEMA public TO usuario;
```

### El servidor inicia pero no puedo acceder a /admin

Verifica que:
1. El servidor esté ejecutándose en `http://0.0.0.0:8000`
2. Accedes con la URL correcta: `http://localhost:8000/admin`
3. No hay errores en la consola del servidor

## Endpoints Disponibles

### Panel Admin
- `GET /admin` - Panel de administración completo

### API CRUD de Productos
- `GET /api/productos` - Listar todos
- `GET /api/productos/{id}` - Obtener uno
- `POST /api/productos` - Crear nuevo
- `PUT /api/productos/{id}` - Actualizar
- `DELETE /api/productos/{id}` - Eliminar

### Endpoints Originales (siguen funcionando)
- `GET /catalogo/{anio}/{mes}/{categoria}` - Obtener catálogo
- `GET /imagen/{anio}/{mes}/{categoria}/{nombre}` - Ver imagen
- `GET /pdf/{anio}/{mes}/{categoria}` - Descargar PDF

## Notas Importantes

- Las imágenes se sirven desde `/static/` que mapea a la carpeta `imagenes/`
- Los PDFs están en `api/catalogos/` y se generan automáticamente del catálogo
- Los productos en PostgreSQL son independientes de los JSON existentes
- Puedes usar ambos sistemas en paralelo o migrar completamente
