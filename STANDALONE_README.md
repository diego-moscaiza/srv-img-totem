# srv-img-totem - Servidor Independiente

Este directorio contiene **srv-img-totem ejecutándose fuera de Docker**, como un servicio independiente en la máquina host.

## Estructura

```
srv-img-totem/
├── venv/                    # Virtual environment (creado automáticamente)
├── start.sh                 # Script para iniciar el servicio
├── stop.sh                  # Script para detener el servicio
├── main.py                  # Aplicación FastAPI
├── requirements.txt         # Dependencias Python
├── .env                     # Configuración (creado automáticamente)
├── imagenes/                # Catálogos de imágenes
├── src/                     # Código fuente
│   ├── config.py           # Configuración
│   ├── database.py         # BD SQLite
│   ├── schemas.py          # Modelos Pydantic
│   └── catalogos_manager.py # Gestión de catálogos
└── data/                    # Base de datos SQLite (se crea automáticamente)
    └── catalogos.db
```

## Instalación Inicial

### Opción 1: Automática (Recomendado)

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh
```

El script automáticamente:
- ✅ Crea el venv si no existe
- ✅ Instala dependencias
- ✅ Crea el directorio `data/`
- ✅ Copia `.env` de `.env.example` si no existe
- ✅ Inicia el servidor

### Opción 2: Manual

```bash
cd /home/diego/Documentos/srv-img-totem

# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Uso

### Iniciar el servidor (Desarrollo)

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh
```

**Salida esperada:**
```
========================================
INICIANDO SRV-IMG-TOTEM
========================================
✅ venv encontrado
ℹ️  Activando venv...
✅ venv activado
...
========================================
INFORMACIÓN DE EJECUCIÓN
========================================
Directorio:     /home/diego/Documentos/srv-img-totem
Python:         Python 3.12.x
Host:           0.0.0.0
Puerto:         8000
Reload:         Habilitado (Desarrollo)
...
📌 URL de acceso:
   http://0.0.0.0:8000
   http://192.168.5.25:8000 (desde tu red)

INFO:     Started server process [PID]
```

### Iniciar en modo producción

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh --prod
```

**Características del modo producción:**
- ❌ Sin reloading automático
- ✅ 4 workers Uvicorn
- ✅ Log level reducido

### Iniciar con puerto personalizado

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh --port 9000
```

### Detener el servidor

```bash
cd /home/diego/Documentos/srv-img-totem
./stop.sh
```

O presiona `Ctrl+C` si está corriendo en la terminal.

## Configuración

El archivo `.env` controla:

```env
IMAGENES_DIR=imagenes              # Directorio de imágenes
SERVER_URL=http://192.168.5.25:8000 # URL pública del servidor
DATABASE_URL=sqlite:///./data/catalogos.db  # Base de datos SQLite
```

## Acceso desde diferentes lugares

### Desde la máquina host

```bash
# Desde el mismo servidor
curl http://localhost:8000/

# Desde tu red local (recomendado)
curl http://192.168.5.25:8000/
```

### Desde n8n (Docker)

```
# ✅ FUNCIONA: Por nombre del servicio (DNS interno Docker)
http://srv-img:8000

# ✅ FUNCIONA: Por IP host
http://192.168.5.25:8000

# ✅ FUNCIONA: Por variable de entorno en n8n
${{ env.SRV_IMG_EXTERNAL_URL }}  → http://192.168.5.25:8000
```

### Desde otras máquinas en tu red

```bash
# Accede desde cualquier máquina en 192.168.5.0/24
curl http://192.168.5.25:8000/
```

## Ejemplos de uso

### Obtener catálogo de FNB

```bash
curl http://192.168.5.25:8000/api/catalogo/fnb/mes-actual | python3 -m json.tool
```

### Descargar imagen

```bash
curl -O http://192.168.5.25:8000/api/catalogos/gaso/2025/12-diciembre/1-celulares/precios/01.png
```

### Obtener información del servidor

```bash
curl http://192.168.5.25:8000/ | python3 -m json.tool
```

## Base de datos

### Ubicación

```
./data/catalogos.db    # Archivo SQLite persistente
```

### Respaldar base de datos

```bash
cp data/catalogos.db data/catalogos.db.backup
```

### Restaurar desde respaldo

```bash
cp data/catalogos.db.backup data/catalogos.db
```

## Logs

Los logs se muestran en la terminal donde ejecutas `start.sh`. Para guardar en archivo:

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh 2>&1 | tee srv-img.log
```

## Solución de problemas

### Puerto 8000 ya en uso

```bash
# Opción 1: Usar puerto diferente
./start.sh --port 9000

# Opción 2: Ver qué proceso usa el puerto
lsof -i :8000

# Opción 3: Matar proceso anterior
./stop.sh
```

### Módulos no encontrados

```bash
# Reinstalar dependencias
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Base de datos corrupta

```bash
# Respaldar antigua
mv data/catalogos.db data/catalogos.db.corrupted

# Se creará nueva base de datos vacía al iniciar
./start.sh
```

## Comparación: Docker vs Sin Docker

| Aspecto | Con Docker | Sin Docker |
|---------|-----------|-----------|
| Aislamiento | Completo | Ninguno |
| Acceso desde n8n | Por nombre (srv-img:8000) | Por IP (192.168.5.25:8000) ✅ |
| Complejidad | Media | Baja |
| Performance | Buena | Excelente |
| Recursos | Compartidos | Dedicados |
| Mantenimiento | Docker | Python/Bash |
| Acceso remoto | Limitado | Total ✅ |

## Configurar autostart con systemd (Opcional)

Si deseas que srv-img-totem se inicie automáticamente:

### 1. Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/srv-img-totem.service
```

### 2. Agregar contenido

```ini
[Unit]
Description=SRV-IMG-TOTEM Server
After=network.target

[Service]
Type=simple
User=diego
WorkingDirectory=/home/diego/Documentos/srv-img-totem
ExecStart=/home/diego/Documentos/srv-img-totem/start.sh --prod
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Habilitar y iniciar

```bash
sudo systemctl daemon-reload
sudo systemctl enable srv-img-totem
sudo systemctl start srv-img-totem

# Ver estado
sudo systemctl status srv-img-totem

# Ver logs
sudo journalctl -u srv-img-totem -f
```

## Versión

- **Versión:** 2.1.0
- **Python:** 3.11+
- **FastAPI:** 0.121.0
- **SQLAlchemy:** 2.0.23

## Contacto

Para reportar problemas o sugerencias, edita `.env` y reinicia el servicio.
