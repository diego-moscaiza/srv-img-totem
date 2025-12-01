# 🖼️ Endpoints de Imágenes - Documentación Actualizada

## Resumen Rápido

La aplicación sirve imágenes desde la carpeta `imagenes/catalogos/` usando el endpoint principal:

```
GET /ver-ruta/{ruta:path}
```

## Endpoint Principal

### `/ver-ruta/{ruta:path}`

**Descripción**: Sirve cualquier imagen desde la ruta relativa a `imagenes/`

**Método**: GET

**Parámetro**: `{ruta:path}` - Ruta relativa a carpeta `imagenes/`

**Ejemplo de uso:**

```
GET /ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/listado/01.png
GET /ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png
```

**URL Completa:**

```
http://localhost:8000/ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/listado/01.png
```

**Respuesta:**
- ✅ 200 OK - Imagen PNG/JPG servida
- ❌ 500 Error - Archivo no existe

**Fallback**: Cuando la imagen no existe, se muestra placeholder "Sin imagen" en el frontend

## Estructura de Directorios

```
imagenes/
└── catalogos/
    └── 2025/
        └── fnb/
            └── noviembre/
                └── 1-celulares/
                    ├── listado/
                    │   ├── 01.png
                    │   ├── 02.png
                    │   └── ...
                    └── caracteristicas/
                        ├── 00.png
                        ├── 01.png
                        └── ...
```

## Uso en Base de Datos

En la tabla `productos`, los campos de imagen almacenan rutas relativas:

```sql
imagen_listado: "catalogos/2025/fnb/noviembre/1-celulares/listado/01.png"
imagen_caracteristicas: "catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png"
```

Al servir, se construye la URL:
```
/ver-ruta/{valor_imagen}
```

## Ejemplo Completo

### 1. Crear producto con imágenes

```bash
curl -X POST http://localhost:8000/api/productos \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "CELCEL0091",
    "nombre": "Samsung Galaxy A06",
    "descripcion": "128 GB - 4 GB RAM",
    "precio": 949.00,
    "categoria": "celulares",
    "segmento": "fnb",
    "estado": "disponible",
    "stock": 50,
    "imagen_listado": "catalogos/2025/fnb/noviembre/1-celulares/listado/01.png",
    "imagen_caracteristicas": "catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png",
    "cuotas": {"3": 338.85, "6": 178.87, "12": 99.24},
    "mes": "noviembre",
    "ano": 2025
  }'
```

### 2. Obtener producto

```bash
curl http://localhost:8000/api/productos/1
```

**Respuesta:**
```json
{
  "id": 1,
  "codigo": "CELCEL0091",
  "nombre": "Samsung Galaxy A06",
  ...
  "imagen_listado": "catalogos/2025/fnb/noviembre/1-celulares/listado/01.png",
  "imagen_caracteristicas": "catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png"
}
```

### 3. Servir imagen en HTML

```html
<!-- Galería (miniatura 180px) -->
<img src="/ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/listado/01.png" 
     alt="Samsung Galaxy A06"
     style="width: 100%; height: 180px; object-fit: contain;">

<!-- Detalle (grande 300px) -->
<img src="/ver-ruta/catalogos/2025/fnb/noviembre/1-celulares/caracteristicas/00.png"
     alt="Características"
     style="width: 100%; height: 300px; object-fit: contain;">
```

### 4. Manejo de errores

```javascript
// Cuando imagen no carga
img.onerror = function() {
  this.parentElement.innerHTML = 
    '<div style="width: 100%; height: 300px; ' +
    'display: flex; align-items: center; ' +
    'justify-content: center; border: 2px dashed #d0d0d0;">'+
    'Sin imagen</div>';
};
```

## Requerimientos

✅ Archivo debe existir en la ruta especificada
✅ Formato soportado: PNG, JPG, JPEG, GIF, BMP, WEBP
✅ La ruta es relativa a carpeta `imagenes/`

## Formatos Soportados

- `.png`
- `.jpg` / `.jpeg`
- `.gif`
- `.bmp`
- `.webp`

## Solución de Problemas

**Error 500 - Imagen no encontrada**
```
Solución: Verifica que el archivo exista en:
  imagenes/{ruta_especificada}
```

**Ruta incorrecta**
```
Incorrecto: /ver-ruta/imagenes/catalogos/...
Correcto:   /ver-ruta/catalogos/...
(No incluir "imagenes/" al inicio)
```

**Imagen corrupta**
```
- Verifica integridad del archivo
- Reinicia servidor
- Limpia caché del navegador (Ctrl+F5)
```

---

**Versión**: 2.1.0
**Última actualización**: Diciembre 2025
**Estado**: 🟢 Funcional

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
