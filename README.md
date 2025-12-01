# 🎯 Servidor de Catálogos Dinámicos con FastAPI + SQLite

Un servidor completo para gestionar catálogos de productos con imágenes, panel administrativo moderno, segmentación de productos (FNB/GASO) y galería interactiva.

## ✨ Características Principales

✅ **Gestión de Catálogos** - Organización por año, mes y categoría
✅ **Panel Admin Moderno** - Interfaz web responsiva con galería de productos
✅ **Servicio de Imágenes** - Listado (180px) y características (300px) de productos
✅ **Base de Datos SQLite** - Almacenamiento persistente sin servidor externo
✅ **Segmentación** - FNB (Financiamiento No Bancario) y GASO (Gaso doméstico)
✅ **Estados de Producto** - Disponible / Agotado
✅ **API REST** - Endpoints CRUD para integración con otras aplicaciones
✅ **Galería Interactiva** - Vista de cards con modal de detalle

## 📦 Requisitos Previos

- Python 3.8+
- pip

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Servidor

```bash
python main.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

La base de datos SQLite se crea automáticamente en `catalogos.db`

### 3. Acceder a la Interfaz

- **Panel Admin**: http://localhost:8000/api/admin
- **API Docs**: http://localhost:8000/docs

## 📂 Estructura del Proyecto ACTUAL

```
srv-img-totem/
├── main.py                      # Servidor FastAPI principal
├── catalogos.db                 # Base de datos SQLite (se crea automáticamente)
├── requirements.txt             # Dependencias Python
├── .env                         # Configuración
├── .env.example                 # Ejemplo de configuración
│
├── src/
│   ├── main.py                  # ⚠️ NOTA: main.py está EN RAÍZ, no en src/
│   ├── database.py              # Modelos SQLAlchemy (productos)
│   ├── schemas.py               # Validación Pydantic
│   ├── crud_routes.py           # Endpoints CRUD + Panel Admin HTML/CSS/JS
│   └── catalogos_manager.py     # Cargador JSON (legacy, opcional)
│
├── imagenes/
│   └── catalogos/               # Carpeta base para imágenes
│       ├── fnb/                 # Segmento FNB
│       │   └── 2025/
│       │       └── 11-noviembre/
│       │           ├── 1-celulares/
│       │           │   ├── caracteristicas/  # Imágenes grandes
│       │           │   └── precios/           # Miniaturas
│       │           ├── 2-laptops/
│       │           └── ... más categorías
│       │
│       └── gaso/                # Segmento GASO
│           └── 2025/
│               └── 11-noviembre/
│                   └── ... estructura similar
│
├── docs/
│   ├── CAMBIOS_ACTUALES.md     # Resumen de cambios SQLite + Galería
│   ├── RESUMEN_RAPIDO.md       # Guía rápida (LEER ESTO)
│   ├── SQLITE_SETUP.md         # Configuración SQLite
│   └── ENDPOINTS_IMAGENES.md   # Documentación de endpoints
│
└── README.md                    # Este archivo
```

## 📡 Endpoints Principales

### 🎛️ Panel Administrativo

| Método | Endpoint     | Descripción                           |
| ------ | ------------ | ------------------------------------- |
| GET    | `/api/admin` | Panel web HTML (galería + formulario) |

### 🗄️ API CRUD de Productos

| Método | Endpoint              | Descripción                |
| ------ | --------------------- | -------------------------- |
| GET    | `/api/productos`      | Listar todos los productos |
| GET    | `/api/productos/{id}` | Obtener producto por ID    |
| POST   | `/api/productos`      | Crear nuevo producto       |
| PUT    | `/api/productos/{id}` | Actualizar producto        |
| DELETE | `/api/productos/{id}` | Eliminar producto          |

### 🖼️ Imágenes

| Método | Endpoint                | Descripción                          |
| ------ | ----------------------- | ------------------------------------ |
| GET    | `/ver-ruta/{ruta:path}` | Servir imagen desde ruta (PRINCIPAL) |

**Ejemplo:**
```
GET /ver-ruta/catalogos/fnb/2025/11-noviembre/1-celulares/precios/01.png
```

## 💾 Modelo de Base de Datos ACTUAL

### Tabla: `productos`

```python
{
    "id": 1,
    "codigo": "CELCEL0091",              # Único
    "nombre": "Samsung Galaxy A06",
    "descripcion": "128 GB - 4 GB RAM",
    "precio": 949.00,
    "categoria": "celulares",
    "segmento": "fnb",                   # ✅ NUEVO: fnb/gaso
    "estado": "disponible",              # ✅ NUEVO: disponible/agotado
    "stock": 50,
    "imagen_listado": "catalogos/fnb/2025/11-noviembre/1-celulares/precios/01.png",
    "imagen_caracteristicas": "catalogos/fnb/2025/11-noviembre/1-celulares/caracteristicas/00.png",
    "cuotas": {"3": 338.85, "6": 178.87, "12": 99.24},
    "mes": "noviembre",
    "ano": 2025
}
```

## 🎨 Panel Admin - Características

### Galería de Productos
- ✅ Vista de cards en CSS Grid responsivo
- ✅ Imagen miniatura (180px height)
- ✅ Código, nombre, precio
- ✅ Badges de segmento (FNB azul / GASO amarillo)
- ✅ Badge de estado (disponible verde / agotado rojo)
- ✅ Botones: Ver, Editar, Eliminar
- ✅ Borde punteado en "Sin imagen" (fallback)

### Modal de Detalle
- ✅ Dos columnas de imágenes (300px height)
- ✅ Imagen Listado (izquierda)
- ✅ Imagen Características (derecha)
- ✅ Tabla con información del producto
- ✅ "Sin imagen" limpio cuando falta imagen

### Formulario de Crear/Editar
- ✅ Todos los campos del producto
- ✅ Validación en frontend
- ✅ Selección de segmento (FNB/GASO)
- ✅ Selección de estado (disponible/agotado)
- ✅ Mensajes de alerta tipo toast

## 🔐 Seguridad

⚠️ **En Desarrollo:**
- Base de datos SQLite sin autenticación
- CORS abierto para desarrollo

✅ **Para Producción:**
- Implementar autenticación JWT
- Validar permisos RBAC
- Certificados HTTPS
- Rate limiting

## 🐛 Solución de Problemas

### Las imágenes no se muestran
- Verifica que la ruta en base de datos sea correcta
- Comprueba que la carpeta `imagenes/catalogos/` exista
- Las rutas deben ser relativas a la carpeta `imagenes/`
- Ejemplo correcto: `catalogos/fnb/2025/11-noviembre/1-celulares/precios/01.png`

### Imágenes con "Sin imagen" pero existe el archivo
- Limpia caché del navegador (Ctrl+F5)
- Verifica que el archivo realmente existe en la ruta
- Comprueba permisos del archivo

### Panel Admin no carga
- Verifica que el servidor esté corriendo: `python main.py`
- Accede a http://localhost:8000/api/admin (no /admin)
- Abre consola del navegador (F12) para ver errores

### Base de datos corrupta
```bash
# Eliminar BD y recrear
rm catalogos.db
python main.py
```

### Base de datos bloqueada
```
Cierra el servidor, espera 5 segundos, reinicia.
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
- **RESUMEN_RAPIDO.md** - Guía rápida (LEER PRIMERO)
- **SQLITE_SETUP.md** - Configuración de SQLite
- **ENDPOINTS_IMAGENES.md** - Documentación de endpoints de imágenes
- Logs de la consola del servidor

## 📄 Licencia

Uso interno BOT. Todos los derechos reservados.

---

**Última actualización:** Diciembre 2025
**Versión:** 2.1.0 (SQLite + Galería + FNB/GASO)
**Estado**: 🟢 Listo para usar
