# Endpoints de Imágenes - Documentación

## Resumen de endpoints para recuperar imágenes de productos y características

### 1. **Endpoint Principal de Producto (JSON con URLs)**
```
GET /api/producto/{año}/{mes}/{categoria}/{producto_id}
```
Retorna los detalles completos del producto incluyendo:
- Datos del producto (precio, nombre, descripción, etc.)
- Objeto `urls` con 4 URLs de imagen:
  - `imagen_lista`: Endpoint para obtener imagen del producto
  - `imagen_caracteristicas`: Endpoint para obtener imagen de características
  - `imagen_directa`: Ruta directa vía `/static`
  - `caracteristicas_directa`: Ruta directa vía `/static`

**Ejemplo:**
```bash
curl http://localhost:8000/api/producto/2025/noviembre/CELULARES/1
```

---

### 2. **Endpoint de Imagen de Producto (PNG)**
```
GET /api/producto/lista/{año}/{mes}/{categoria}/{producto_id}
```
Descarga directamente la imagen PNG del producto.

**Ejemplo:**
```bash
curl http://localhost:8000/api/producto/lista/2025/noviembre/CELULARES/1 -o producto.png
```

---

### 3. **Endpoint de Imagen de Características (PNG)**
```
GET /api/producto/caracteristicas/{año}/{mes}/{categoria}/{producto_id}
```
Descarga directamente la imagen PNG de características del producto.

**Ejemplo:**
```bash
curl http://localhost:8000/api/producto/caracteristicas/2025/noviembre/CELULARES/1 -o caracteristicas.png
```

---

### 4. **Endpoint Directo de Imagen por Categoría**
```
GET /imagen/{año}/{mes}/{categoria}/{nombre_imagen}
```
Obtiene una imagen específica de una categoría. Busca automáticamente en las subcarpetas `productos/` y `caracteristicas/`.

**Ejemplo:**
```bash
curl http://localhost:8000/imagen/2025/noviembre/CELULARES/01.png -o imagen.png
curl http://localhost:8000/imagen/2025/noviembre/CELULARES/02.png -o imagen.png
```

---

### 5. **Acceso Directo vía /static (sin procesar)**
```
GET /static/catalogos/{año}/fnb/{mes}/{categoria}/{subcarpeta}/{nombre_imagen}
```
Acceso directo al archivo usando el servidor de archivos estáticos de FastAPI.

**Subcarpetas disponibles:**
- `productos/` - Imágenes de productos
- `caracteristicas/` - Imágenes de características

**Ejemplo:**
```bash
http://localhost:8000/static/catalogos/2025/fnb/noviembre/1-celulares/productos/01.png
http://localhost:8000/static/catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/01.png
```

---

### 6. **Búsqueda por nombre de archivo (en subdirectorios)**
```
GET /ver/{nombre_archivo}
```
Busca recursivamente en todo el árbol de directorios de `imagenes/`.

**Ejemplo:**
```bash
curl http://localhost:8000/ver/01.png
```

---

### 7. **Acceso por ruta completa**
```
GET /ver-ruta/{ruta:path}
```
Accede a una imagen usando la ruta relativa desde `imagenes/`.

**Ejemplo:**
```bash
curl http://localhost:8000/ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/productos/01.png
```

---

## Estructura de carpetas de imágenes
```
imagenes/
└── catalogos/
    └── 2025/
        └── fnb/
            └── noviembre/
                ├── 1-celulares/
                │   ├── productos/
                │   │   ├── 01.png
                │   │   └── 02.png
                │   └── caracteristicas/
                │       ├── 01.png
                │       └── 02.png
                ├── 2-laptops/
                │   ├── productos/
                │   │   ├── 01.png
                │   │   └── 02.png
                │   └── caracteristicas/
                │       ├── 01.png
                │       └── 02.png
                ├── 3-televisores/
                ├── 4-refrigeradoras/
                └── 5-lavadoras/
```

---

## Rutas en JSON (productos)
Las imágenes se referencian en los JSON de la siguiente forma:
```json
{
  "id": "1",
  "nombre": "SAMSUNG GALAXY A06",
  "imagen": "catalogos/2025/fnb/noviembre/1-celulares/productos/01.png",
  "imagen_caracteristicas": "catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/01.png"
}
```

---

## Pruebas recomendadas

### 1. Obtener detalles del producto
```bash
curl http://localhost:8000/api/producto/2025/noviembre/CELULARES/1
```

### 2. Descargar imagen de producto
```bash
curl http://localhost:8000/api/producto/lista/2025/noviembre/CELULARES/1 -o producto.png
```

### 3. Descargar imagen de características
```bash
curl http://localhost:8000/api/producto/caracteristicas/2025/noviembre/CELULARES/1 -o caracteristicas.png
```

### 4. Acceso directo vía static
```bash
curl http://localhost:8000/static/catalogos/2025/fnb/noviembre/1-celulares/productos/01.png -o producto.png
```

---

## Categorías disponibles
- `CELULARES` (2 productos)
- `LAPTOPS` (2 productos)
- `TELEVISORES` (1 producto)
- `REFRIGERADORAS` (1 producto)
- `LAVADORAS` (1 producto)

---

## Estado actual
✅ Todos los endpoints funcionando correctamente
✅ Imágenes se sirven desde múltiples rutas
✅ JSON contiene referencias a imágenes correctas
✅ Servidor FastAPI ejecutándose en puerto 8000
