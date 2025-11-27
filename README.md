# 🎯 Servidor de Catálogos Dinámicos con FastAPI + PostgreSQL

Un servidor completo para gestionar catálogos de productos con imágenes, PDFs y panel administrativo web.

## ✨ Características Principales

✅ **Gestión de Catálogos** - Organización por año, mes y categoría
✅ **Servicio de Imágenes** - Listado y características de productos
✅ **Generación de PDFs** - Catálogos en PDF con formato automático
✅ **Base de Datos PostgreSQL** - Almacenamiento persistente de productos
✅ **Panel Admin Web** - Interfaz intuitiva para CRUD completo
✅ **API REST** - Endpoints para integración con otras aplicaciones
✅ **Búsqueda Flexible** - Soporta JSON estático o base de datos

## 📦 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar PostgreSQL

Lee [POSTGRES_SETUP.md](./POSTGRES_SETUP.md) para:
- Crear la base de datos
- Crear el usuario
- Actualizar las credenciales en `database.py`

### 3. Ejecutar el Servidor

```bash
python main.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Acceder a la Interfaz

- **Panel Admin**: http://localhost:8000/admin
- **Documentación API**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/redoc

## 📂 Estructura del Proyecto

```
srv-img-totem/
├── api/
│   └── catalogos/               # Catálogos en JSON
│       └── 2025/
│           └── fnb/
│               └── noviembre/   # Catálogos por mes
│                   ├── 1-celulares.json
│                   ├── 2-laptops.json
│                   └── ...
├── imagenes/
│   └── catalogos/               # Imágenes de productos
│       └── 2025/
│           └── fnb/
│               └── noviembre/
│                   └── {categoría}/
│                       ├── listado/         # Fotos para listado
│                       └── caracteristicas/ # Fotos detalladas
│
├── main.py                      # Servidor FastAPI (principal)
├── database.py                  # Modelos SQLAlchemy para PostgreSQL
├── schemas.py                   # Esquemas Pydantic para validación
├── crud_routes.py               # Endpoints CRUD y panel admin
├── catalogos_manager.py         # Cargador de catálogos JSON
├── migrate_data.py              # Script para migrar JSON → PostgreSQL
├── requirements.txt             # Dependencias Python
├── .env.example                 # Variables de entorno (ejemplo)
└── README.md                    # Este archivo
```

## 📡 Endpoints Disponibles

### 🎛️ Panel Administrativo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/admin` | Panel web para gestionar productos |

### 🗄️ API CRUD de Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos` | Listar todos los productos |
| GET | `/api/productos/{id}` | Obtener producto por ID |
| POST | `/api/productos` | Crear nuevo producto |
| PUT | `/api/productos/{id}` | Actualizar producto |
| DELETE | `/api/productos/{id}` | Eliminar producto |

### 📚 Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/catalogo/{anio}/{mes}/{categoria}` | Obtener catálogo completo |
| GET | `/catalogo/listado/{anio}/{mes}/{categoria}` | Obtener solo productos |

### 🖼️ Imágenes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/imagen/{anio}/{mes}/{categoria}/{nombre}` | Obtener imagen de producto |
| GET | `/ver/{nombre_archivo}` | Ver imagen por nombre |
| GET | `/ver-ruta/{ruta:path}` | Ver imagen por ruta |
| GET | `/static/{ruta:path}` | Acceso directo a archivos estáticos |

### 📄 PDFs

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/pdf/{anio}/{mes}/{categoria}` | Descargar catálogo PDF |
| GET | `/ver-pdf/{anio}/{mes}/{categoria}` | Ver PDF en navegador |

### 🔧 Sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información general del servidor |
| GET | `/diagnostico` | Diagnóstico del servidor |

## 💾 Modelos de Base de Datos

### Producto

```python
class Producto(Base):
    __tablename__ = "productos"
    
    id: Integer          # ID único
    codigo: String       # Código del producto (único)
    nombre: String       # Nombre del producto
    descripcion: String  # Descripción adicional
    precio: Float        # Precio base
    categoria: String    # Categoría (celulares, laptops, etc.)
    imagen_listado: String        # Ruta de imagen para listado
    imagen_caracteristicas: String # Ruta de imagen detallada
    cuotas: JSON         # {"3": 338.85, "6": 178.87, "12": 99.24}
    mes: String          # Mes del catálogo
    ano: Integer         # Año del catálogo
    stock: Boolean       # Disponibilidad
```

## 🔄 Flujo de Datos

```
JSON Files (legacy)      →  catalogos_manager.py  →  FastAPI Endpoints
                             ↓
PostgreSQL Database      ←  crud_routes.py        ←  Panel Admin Web
                             ↓
                         API REST Endpoints
```

## 📊 Casos de Uso

### 1. Servir Catálogos Existentes (JSON)
```bash
GET /catalogo/2025/noviembre/celulares
# Retorna: Lista de productos desde JSON
```

### 2. Gestionar Productos en BD
```bash
POST /api/productos
# Body: {"codigo": "...", "nombre": "...", ...}
# Crea nuevo producto en PostgreSQL
```

### 3. Ver Panel Admin
```
Abre http://localhost:8000/admin
- Crear, editar, eliminar productos
- Ver tabla completa
- Buscar por nombre/código
```

## 🔐 Seguridad

⚠️ **En Desarrollo:**
- Base de datos sin autenticación
- CORS abierto para desarrollo

✅ **Para Producción:**
- Implementar autenticación JWT
- Validar permisos RBAC
- Usar variables de entorno para credenciales
- Certificados HTTPS
- Rate limiting

## 🐛 Solución de Problemas

### Error: "Role does not exist"
```bash
# En PSQL:
CREATE USER usuario WITH PASSWORD 'contraseña';
```

### Error: "Database does not exist"
```bash
# En PSQL:
CREATE DATABASE catalogos_db OWNER usuario;
```

### Las imágenes no se muestran
- Verifica que la ruta en base de datos sea correcta
- Comprueba que la carpeta `imagenes/` exista
- Las rutas deben ser relativas a la carpeta `imagenes/`

### Migrando datos existentes
```bash
python migrate_data.py
```

## 📝 Ejemplo de Uso Completo

### 1. Crear un Producto

```bash
curl -X POST "http://localhost:8000/api/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "CELCEL0091",
    "nombre": "SAMSUNG GALAXY A06",
    "descripcion": "128 GB - 4 GB RAM",
    "precio": 949.00,
    "categoria": "celulares",
    "imagen_listado": "catalogos/2025/fnb/noviembre/1-celulares/listado/01.png",
    "imagen_caracteristicas": "catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png",
    "cuotas": {"3": 338.85, "6": 178.87, "9": 125.7, "12": 99.24},
    "mes": "noviembre",
    "ano": 2025,
    "stock": true
  }'
```

### 2. Obtener Todos los Productos

```bash
curl "http://localhost:8000/api/productos"
```

### 3. Actualizar Producto

```bash
curl -X PUT "http://localhost:8000/api/productos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 899.00,
    "stock": false
  }'
```

### 4. Eliminar Producto

```bash
curl -X DELETE "http://localhost:8000/api/productos/1"
```

## 🎨 Personalización

### Agregar Nuevas Categorías

En `database.py`, modifica la categoría:
```python
categoria = Column(String(100))  # Ya soporta cualquier string
```

En el formulario del admin (`crud_routes.py`), agrega opciones:
```html
<select name="categoria" required>
    <option>celulares</option>
    <option>laptops</option>
    <option>mi_nueva_categoria</option>
</select>
```

### Cambiar Puerto

En `main.py`, última línea:
```python
uvicorn.run(app, host="0.0.0.0", port=9000)  # Cambiar a 9000
```

## 🤝 Contribuciones

Este proyecto forma parte de BOT Server infrastructure.

## 📞 Soporte

Para problemas o preguntas, consulta:
- `POSTGRES_SETUP.md` - Configuración de base de datos
- `ENDPOINTS_IMAGENES.md` - Documentación de endpoints de imágenes
- Logs de la consola del servidor

## 📄 Licencia

Uso interno BOT. Todos los derechos reservados.

---

**Última actualización:** 2025
**Versión:** 2.0.0 (PostgreSQL + Panel Admin)
GET	/	Información general del servidor
GET	/diagnostico	Diagnóstico completo del sistema de archivos
GET	/imagenes	Lista imágenes en el directorio raíz
GET	/todas-las-imagenes	Lista TODAS las imágenes incluyendo subdirectorios
🖼 Servir Imágenes
Método	Endpoint	Descripción
GET	/ver/{nombre_archivo}	Muestra imagen en el navegador (busca en subdirectorios)
GET	/ver-ruta/{ruta_completa}	Muestra imagen usando ruta completa desde imagenes/
GET	/imagen/{nombre_archivo}	Descarga la imagen como archivo
GET	/static/{ruta}	Acceso directo estático a archivos
🎯 Uso de la API
```

1. Acceso Básico por Nombre de Archivo
   
```text
http://localhost:8000/ver/financia-calidda-n-1.jpg
Busca automáticamente en todos los subdirectorios
```

1. Acceso por Ruta Completa

```text
http://localhost:8000/ver-ruta/masivos/financia-calidda-n-1.jpg
http://localhost:8000/ver-ruta/catalogos/2025/noviembre/fnb/imagen.jpg
```

1. Descargar Imágenes

```text
http://localhost:8000/imagen/financia-calidda-n-1.jpg
```

1. Acceso Directo Estático
```text
http://localhost:8000/static/masivos/financia-calidda-n-1.jpg
```

🔧 Configuración
Directorio de Imágenes
El servidor busca imágenes en el directorio imagenes/ por defecto. Puedes modificarlo cambiando la variable IMAGENES_DIR en main.py.

Formatos Soportados
.png, .jpg, .jpeg, .gif, .bmp, .webp

Puertos y Host
Puerto por defecto: 8000

Host: 0.0.0.0 (accesible desde cualquier IP)

Documentación: http://localhost:8000/docs

🚦 Ejemplos Prácticos
Verificar que el servidor funciona:

```bash
curl http://localhost:8000/
```

Ver diagnóstico del sistema de archivos:

```bash
curl http://localhost:8000/diagnostico
```

Listar todas las imágenes disponibles:

```bash
curl http://localhost:8000/todas-las-imagenes
```

Acceder a una imagen específica:

```bash
# Si la imagen está en: imagenes/masivos/financia-calidda-n-1.jpg
curl http://localhost:8000/ver/financia-calidda-n-1.jpg
```

# o

```bash
curl http://localhost:8000/ver-ruta/masivos/financia-calidda-n-1.jpg
```

🐛 Solución de Problemas
Error "Not Found"
Verifica que la imagen exista en el directorio imagenes/

Usa el endpoint /diagnostico para ver la estructura de archivos

Confirma el nombre exacto del archivo (incluyendo extensión)

La imagen no se muestra
Verifica que el formato esté soportado

Confirma que la imagen no esté corrupta

Revisa los permisos del archivo

El servidor no inicia
Verifica que FastAPI esté instalado: pip list | grep fastapi

Confirma que el puerto 8000 esté disponible

Revisa que no haya errores de sintaxis en main.py

📚 Documentación Interactiva
Una vez ejecutado el servidor, puedes acceder a:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🎨 Personalización
Puedes modificar el servidor editando main.py:

Cambiar el directorio de imágenes

Agregar más formatos de archivo

Modificar los endpoints

Agregar autenticación

Implementar cache

📄 Licencia
Este proyecto es de código abierto y está disponible bajo la licencia MIT.
