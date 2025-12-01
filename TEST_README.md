# Prueba de Endpoints - API de Productos

## 📋 Descripción
Este script prueba los endpoints de la API para obtener datos de productos desde la base de datos.

## 🚀 Cómo ejecutar

### Opción 1: Usando PowerShell (Recomendado)
```powershell
# Abre PowerShell y ejecuta:
cd "c:\Users\Diego Moscaiza\Downloads\Servidores Para BOT\srv-img-totem"
.\run_test.ps1
```

### Opción 2: Usando CMD (Batch)
```cmd
# Abre CMD y ejecuta:
cd "c:\Users\Diego Moscaiza\Downloads\Servidores Para BOT\srv-img-totem"
run_test.bat
```

### Opción 3: Manualmente con venv
```powershell
# Abre PowerShell en el directorio del proyecto
cd "c:\Users\Diego Moscaiza\Downloads\Servidores Para BOT\srv-img-totem"

# Activa el virtual environment
.\venv\Scripts\Activate.ps1

# Ejecuta el test
python test_endpoint.py
```

## ⚠️ Requisito Previo
**El servidor debe estar corriendo ANTES de ejecutar el test**

En otra terminal, ejecuta:
```powershell
cd "c:\Users\Diego Moscaiza\Downloads\Servidores Para BOT\srv-img-totem"
.\venv\Scripts\Activate.ps1
python main.py
```

El servidor se iniciará en: `http://192.168.1.65:8000`

## 📊 Qué prueba el script

### TEST 1: Listar todos los productos
- **URL**: `GET /api/productos`
- **Descripción**: Obtiene la lista completa de todos los productos en la BD
- **Respuesta**: Array JSON con:
  - ID
  - Nombre
  - Código
  - Precio
  - Categoría
  - Segmento
  - Estado
  - Imagen listado
  - Imagen características
  - Cuotas
  - Y más campos

### TEST 2: Obtener producto específico
- **URL**: `GET /api/productos/{id}`
- **Descripción**: Obtiene los detalles completos de un producto por su ID
- **Respuesta**: Objeto JSON con todos los datos del producto

### TEST 3: Crear un producto nuevo
- **URL**: `POST /api/productos`
- **Descripción**: Crea un nuevo producto con los datos especificados
- **Respuesta**: El producto creado con su ID asignado

## ✅ Salida esperada

Si todo funciona correctamente, verás:

```
============================================================
TEST 1: Obtener lista de TODOS los productos
============================================================
URL: http://192.168.1.65:8000/api/productos

✅ ÉXITO - 8 productos obtenidos

📋 Primeros 3 productos:

1. SAMSUNG GALAXY A06
   ID: 1
   Código: CELCEL0091
   Precio: S/. 949.00
   Categoría: celulares
   Segmento: fnb
   Estado: disponible
   Imagen: catalogos/fnb/2025/11-noviembre/1-celulares/listado/...
```

## 🐛 Solución de problemas

### "El servidor NO está disponible"
- Verifica que el servidor esté corriendo en otra terminal
- Confirma que esté en: `http://192.168.1.65:8000`
- Si no ves logs del servidor, reinicia con: `python main.py`

### "ModuleNotFoundError: No module named 'requests'"
- El venv no está activado correctamente
- Intenta con los scripts `run_test.ps1` o `run_test.bat`
- O activa manualmente: `.\venv\Scripts\Activate.ps1`

### "Connection refused"
- El servidor no está escuchando en el puerto 8000
- Verifica en Terminal 1 que veas: `Uvicorn running on http://0.0.0.0:8000`

## 📝 Notas
- El servidor DEBE estar ejecutándose antes de correr el test
- Los tests se ejecutan en orden: listar → obtener → crear
- El servidor responde a `http://192.168.1.65:8000`
- Si cambias de red, actualiza `BASE_URL` en `test_endpoint.py`
