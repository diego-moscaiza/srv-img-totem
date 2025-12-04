# 📊 Análisis Completo del Proyecto `srv-img-totem`

> **Fecha:** 4 de diciembre de 2025  
> **Versión:** 2.1.0

---

## 🎯 **Propósito**

Es un **servidor de catálogos de productos** construido con **FastAPI + SQLite** para gestionar productos con imágenes, diseñado para integrarse con bots (probablemente WhatsApp vía n8n).

---

## 🏗️ **Arquitectura General**

| Capa | Tecnología | Descripción |
|------|------------|-------------|
| **API** | FastAPI | Servidor REST con endpoints para catálogos, productos e imágenes |
| **BD** | SQLite + SQLAlchemy | Almacenamiento persistente sin servidor externo |
| **Frontend** | HTML/CSS/JS (admin.html) | Panel administrativo con galería interactiva |
| **Imágenes** | Sistema de archivos | Estructura organizada por segmento/año/mes/categoría |

---

## 📁 **Estructura de Archivos Clave**

```
srv-img-totem/
├── main.py                    ← Aplicación FastAPI principal (~940 líneas)
├── catalogos.db               ← Base de datos SQLite (se crea sola)
├── requirements.txt           ← Dependencias Python
│
├── src/
│   ├── config.py              ← Configuración (.env, SERVER_URL, IMAGENES_DIR)
│   ├── database.py            ← Modelo SQLAlchemy (Producto) + conexión
│   ├── schemas.py             ← Validación Pydantic (ProductoCreate/Update)
│   ├── catalogos_manager.py   ← Lógica de negocio (CatalogoManager, SegmentoCatalogo)
│   └── crud_routes.py         ← Endpoints CRUD para productos
│
├── imagenes/
│   └── catalogos/
│       └── {segmento}/        ← fnb, gaso
│           └── {año}/
│               └── {mes-nombre}/
│                   └── {num-categoria}/
│                       ├── precios/         ← Imágenes de listado
│                       ├── caracteristicas/ ← Imágenes detalladas
│                       └── json/            ← Datos de productos (.json)
│
├── templates/
│   └── admin.html             ← Panel administrativo web (2200+ líneas)
│
├── scripts/sqlite/
│   ├── create_database.py     ← Crear BD
│   ├── backup_database.py     ← Respaldo
│   ├── restore_database.py    ← Restaurar
│   └── delete_all_products.py ← Limpiar productos
│
├── test/
│   ├── load_products_from_files.py  ← Carga interactiva
│   ├── load_all_products.py         ← Carga masiva automática
│   └── ...
│
└── docs/                      ← Documentación
```

---

## 🔌 **Endpoints Principales**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/catalogo/{segmento}/activo` | GET | Catálogo del mes actual |
| `/api/catalogo/{segmento}/{año}/{mes}` | GET | Catálogo de un mes específico |
| `/api/catalogo/{segmento}/{año}/{mes}/{categoria}` | GET | Productos de una categoría |
| `/api/catalogos/{ruta:path}` | GET | Servir imágenes estáticas |
| `/api/ver-pdf/{ruta:path}` | GET | Visualizar PDF en línea |
| `/api/pdf-base64/{ruta:path}` | GET | PDF en Base64 para WhatsApp/n8n |
| `/api/productos` | CRUD | Gestión de productos |
| `/admin` | GET | Panel administrativo web |
| `/diagnostico` | GET | Información de diagnóstico |

---

## 🏷️ **Segmentación de Productos**

| Segmento | Categorías |
|----------|------------|
| **FNB** (Financiamiento No Bancario) | celulares, laptops, televisores, refrigeradoras, lavadoras |
| **GASO** (Gaso doméstico) | celulares, televisores, refrigeradores, lavadoras, fusion |

---

## 📦 **Modelo de Datos (Producto)**

```python
{
    "id": int,                          # Auto-incremento
    "codigo": str,                      # Único (ej: "COMLAP0050")
    "nombre": str,                      # Nombre del producto
    "descripcion": str,                 # Descripción
    "precio": float,                    # Precio en soles
    "categoria": str,                   # celulares, laptops, etc.
    "segmento": str,                    # "fnb" | "gaso"
    "estado": str,                      # "disponible" | "agotado"
    "stock": bool,                      # true/false
    "imagen_listado": str,              # Ruta imagen pequeña
    "imagen_caracteristicas": str,      # Ruta imagen detalle
    "imagen_caracteristicas_2": str,    # Segunda imagen (opcional)
    "cuotas": JSON,                     # {"3": 338.85, "6": 178.87, ...}
    "mes": str,                         # "diciembre"
    "ano": int                          # 2025
}
```

---

## 🖼️ **Sistema de Imágenes y JSON**

### Estructura de carpetas:
```
imagenes/catalogos/{segmento}/{año}/{mes}/
└── {num-categoria}/
    ├── precios/
    │   ├── 01.png
    │   ├── 02.png
    │   └── ...
    ├── caracteristicas/
    │   ├── 01.png
    │   ├── 02.png
    │   └── ...
    └── json/
        ├── 01.json
        ├── 02.json
        └── ...
```

### Relación imagen ↔ JSON:
- `precios/01.png` → `json/01.json`
- `precios/02.jpg` → `json/02.json`
- El número del archivo vincula la imagen con sus datos

### Formato de archivo JSON:
```json
{
    "codigo": "COMLAP0050",
    "producto": "Lenovo Laptop i7 IDEAPAD SLIM 5i",
    "descripcion": "Procesador Intel i7, pantalla 15.6 pulgadas",
    "precio": "S/. 4599",
    "marca": "Lenovo",
    "nota_adicional": "* IMÁGENES Y COLORES REFERENCIALES *",
    "cuotas": {
        "3": 1651.94,
        "6": 875.92,
        "9": 618.14,
        "12": 489.93,
        "18": 363.07,
        "24": 301.00,
        "36": 241.69,
        "48": 214.77,
        "60": 200.76
    },
    "beneficios": [
        "01 año de garantía",
        "Delivery gratuito",
        "Accede al pronto pago",
        "Cero cuota inicial"
    ]
}
```

---

## ⚙️ **Configuración (.env)**

```env
SERVER_URL=http://localhost:8000
IMAGENES_DIR=imagenes
DATABASE_URL=sqlite:///catalogos.db
```

---

## 🚀 **Instalación y Ejecución**

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar (Windows PowerShell)
venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar servidor
python main.py

# 5. Acceder
http://localhost:8000/admin
http://localhost:8000/docs
```

---

## 🔍 **Observaciones y Posibles Mejoras**

### ⚠️ **Problemas Detectados**

1. **Duplicación en `database.py`**: La columna `stock` está definida dos veces (líneas 64-65)

2. **`main.py` muy extenso** (~940 líneas): Podría dividirse en múltiples routers/módulos

3. **Inconsistencia en categorías**: FNB usa "refrigeradoras", GASO usa "refrigeradores"

4. **Caché sin invalidación**: `SegmentoCatalogo.cache` no tiene TTL ni mecanismo de limpieza

5. **Sin autenticación**: El panel admin está expuesto sin protección

### 💡 **Sugerencias de Mejora**

1. **Separar endpoints** en routers por funcionalidad:
   - `routers/catalogos.py`
   - `routers/imagenes.py`
   - `routers/admin.py`

2. **Agregar autenticación** básica al panel admin

3. **Implementar paginación** en listados de productos

4. **Agregar logging** estructurado

5. **Tests automatizados** (actualmente solo hay scripts de prueba manuales)

---

## 📝 **Flujo de Uso Típico**

1. **Preparar estructura**: Colocar imágenes en `precios/` y datos en `json/`
2. **Cargar productos**: Ejecutar script de carga automática
3. **Iniciar servidor**: `python main.py`
4. **Gestionar productos**: Acceder a `/admin`
5. **Consumir API**: Otros sistemas (bots) consultan `/api/catalogo/{segmento}/activo`

---

## 🔗 **Dependencias Principales**

| Paquete | Versión | Uso |
|---------|---------|-----|
| `fastapi` | 0.121.0 | Framework web |
| `uvicorn` | 0.38.0 | Servidor ASGI |
| `sqlalchemy` | 2.0.23 | ORM |
| `pydantic` | 2.12.3 | Validación |
| `python-dotenv` | 1.1.1 | Variables de entorno |
| `aiofiles` | 25.1.0 | Archivos async |

---

## 📌 **Notas Adicionales**

- La BD se crea automáticamente al iniciar el servidor
- Las rutas de imágenes son relativas a `imagenes/`
- El sistema soporta múltiples formatos: PNG, JPG, JPEG, GIF, WEBP
- Los PDFs se pueden servir inline o en Base64 para WhatsApp
