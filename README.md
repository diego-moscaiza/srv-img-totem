📷 Servidor de Imágenes con FastAPI
Un servidor simple y eficiente para servir imágenes locales a través de una API REST construida con FastAPI.

🚀 Características
✅ Servir imágenes desde directorios locales

✅ Soporte para subdirectorios anidados

✅ Múltiples formatos de imagen (PNG, JPG, JPEG, GIF, BMP, WEBP)

✅ Endpoints para ver y descargar imágenes

✅ Búsqueda automática en subcarpetas

✅ Documentación automática interactiva

✅ Diagnóstico integrado del servidor

📁 Estructura del Proyecto

```text
servidor-imagenes/
├── imagenes/                 # Directorio principal de imágenes
│   ├── catalogos/
│   │   └── 2025/
│   │       └── noviembre/
│   │           └── fnb/
│   ├── masivos/
│   │   └── financia-calidda-n-1.jpg
│   └── A.jpg
├── main.py                   # Servidor FastAPI
├── requirements.txt          # Dependencias del proyecto
└── README.md                # Este archivo
```

🛠 Instalación
Clona o descarga el proyecto

Instala las dependencias:

```bash
pip install fastapi uvicorn python-multipart
Ejecuta el servidor:
```

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
📋 Endpoints Disponibles
🔍 Información y Diagnóstico
Método	Endpoint	Descripción
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
