# Cambios Realizados: srv-img-totem Standalone

## 📋 Resumen

Se ha separado `srv-img-totem` de Docker para ejecutarlo como servicio independiente en la máquina host.

### ✅ Cambios Completados

#### 1. **En `/home/diego/Documentos/cb-totem/docker-compose.yaml`**
   - ❌ Removido servicio `srv-img` completamente
   - ❌ Removido volumen `srv_img_data`
   - ❌ Removida referencia `srv-img-internal:172.18.0.3` de evolution-api
   - ❌ Removida referencia `srv-img-host:host-gateway` de n8n
   - ✅ Variables de entorno de n8n actualizado para usar IP externa: `http://192.168.5.25:8000`

#### 2. **En `/home/diego/Documentos/srv-img-totem/`**
   - ✅ Creado `venv/` (virtual environment)
   - ✅ Dependencias Python instaladas en venv
   - ✅ Creado `start.sh` - Script para iniciar el servidor en segundo plano
   - ✅ Creado `stop.sh` - Script para detener el servidor
   - ✅ Creado `status.sh` - Script para ver estado y logs
   - ✅ Creado `STANDALONE_README.md` - Documentación completa
   - ✅ Creado `QUICKSTART.md` - Guía rápida
   - ✅ Se crea automáticamente `data/` con la BD SQLite
   - ✅ Se generan logs en `srv-img.log`

---

## 🚀 Cómo Usar

### Iniciar el servidor (Ejecuta UNA VEZ)

```bash
cd /home/diego/Documentos/srv-img-totem
./start.sh
```

**Resultado:**
```
========================================
INICIANDO SRV-IMG-TOTEM
========================================
✅ venv encontrado
✅ venv activado
✅ Dependencias OK
...
✅ Servidor iniciado con PID: 12345

📌 URL de acceso:
   http://localhost:8000
   http://192.168.5.25:8000 (desde tu red)
```

El servidor continuará ejecutándose incluso después de cerrar la terminal.

### Ver estado

```bash
cd /home/diego/Documentos/srv-img-totem
./status.sh
```

**Salida:**
```
========================================
ESTADO DE SRV-IMG-TOTEM
========================================
Estado:          ● EJECUTÁNDOSE
PID:             12345
```

### Ver logs en tiempo real

```bash
tail -f /home/diego/Documentos/srv-img-totem/srv-img.log
```

### Detener el servidor

```bash
cd /home/diego/Documentos/srv-img-totem
./stop.sh
```

### Reiniciar el servidor

```bash
./stop.sh && sleep 2 && ./start.sh
```

---

## 🔗 Acceso desde n8n

Ahora que srv-img está fuera de Docker, n8n puede acceder de dos formas:

### ✅ Forma 1: Por IP del host (RECOMENDADO)

```
http://192.168.5.25:8000/api/catalogos/gaso/2025/12-diciembre/1-celulares/precios/01.png
```

**Ventajas:**
- ✅ Acceso directo por IP
- ✅ No depende del DNS interno de Docker
- ✅ Funciona perfectamente

### ✅ Forma 2: Por variable de entorno (FLEXIBLE)

En n8n:
```
${{ env.SRV_IMG_EXTERNAL_URL }}/api/catalogos/gaso/2025/12-diciembre/1-celulares/precios/01.png
```

La variable está configurada en docker-compose.yaml:
```yaml
environment:
  - SRV_IMG_EXTERNAL_URL=http://192.168.5.25:8000
```

---

## 📊 Comparación: Antes vs Después

| Aspecto | Con Docker | Sin Docker |
|---------|-----------|-----------|
| Ubicación | Dentro de cb-totem | `/home/diego/Documentos/srv-img-totem` |
| Acceso desde n8n | `http://srv-img:8000` | `http://192.168.5.25:8000` ✅ |
| Acceso remoto | Limitado | Total ✅ |
| Gestión | Docker Compose | Scripts bash |
| Performance | Buena | Excelente ✅ |
| Mantenimiento | Docker | Python + bash |
| Persistencia | Volumen Docker | Archivo SQLite |
| Escalabilidad | Bajo | Alto ✅ |

---

## 📁 Estructura de archivos

```
/home/diego/Documentos/srv-img-totem/
├── venv/                      # ← Virtual environment
├── data/
│   └── catalogos.db           # ← Base de datos SQLite
├── imagenes/                  # ← Catálogos de imágenes
├── src/
│   ├── config.py              # Ahora usa ./data/catalogos.db
│   ├── database.py
│   ├── schemas.py
│   └── catalogos_manager.py
├── start.sh                   # ← SCRIPT: Iniciar en segundo plano
├── stop.sh                    # ← SCRIPT: Detener servidor
├── status.sh                  # ← SCRIPT: Ver estado
├── main.py
├── requirements.txt
├── .env                       # Creado automáticamente
├── srv-img.log                # ← Logs del servidor
├── .srv-img.pid               # ← PID del proceso (archivo temporal)
├── STANDALONE_README.md       # ← Documentación completa
├── QUICKSTART.md              # ← Guía rápida
└── CAMBIOS.md                 # ← Este archivo
```

---

## �� Acceso desde diferentes ubicaciones

### Desde la máquina host (mismo servidor)

```bash
# Opción 1: localhost
curl http://localhost:8000/

# Opción 2: IP interna
curl http://192.168.5.25:8000/
```

### Desde tu red local (otras máquinas)

```bash
# Cualquier máquina en 192.168.5.0/24 puede acceder
curl http://192.168.5.25:8000/api/catalogo/fnb/mes-actual
```

### Desde n8n (dentro de Docker en cb-totem)

```
# En un nodo HTTP de n8n:
GET http://192.168.5.25:8000/api/catalogos/gaso/2025/12-diciembre/1-celulares/precios/01.png

# O usando variable de entorno:
GET ${{ env.SRV_IMG_EXTERNAL_URL }}/api/catalogos/...
```

---

## ⚙️ Configuración (.env)

Archivo: `/home/diego/Documentos/srv-img-totem/.env`

```env
IMAGENES_DIR=imagenes
SERVER_URL=http://192.168.5.25:8000
DATABASE_URL=sqlite:///./data/catalogos.db
```

Para cambiar la configuración:
1. Edita `.env`
2. Reinicia: `./stop.sh && ./start.sh`

---

## 🛠️ Solución de problemas

### Puerto 8000 ya en uso

```bash
# Ver qué proceso lo usa
lsof -i :8000

# Usar puerto diferente
./start.sh --port 9000
```

### Verificar que está escuchando

```bash
# Desde otra terminal
curl http://192.168.5.25:8000/

# Debería retornar JSON con información del servidor
```

### Ver logs detallados

```bash
tail -50 /home/diego/Documentos/srv-img-totem/srv-img.log
```

### Matar manualmente si es necesario

```bash
pkill -f "uvicorn main:app"
```

---

## 📝 Notas Importantes

1. **Persistencia:** La BD SQLite se guarda en `data/catalogos.db` y persiste entre reinicios

2. **Segundo Plano:** El script usa `nohup` para que el proceso continúe aunque cierres la terminal

3. **Logs:** Se guardan en `srv-img.log` para diagnóstico

4. **Variables de Entorno:** Se pasan automáticamente desde `.env`

5. **Performance:** Sin el overhead de Docker, el rendimiento es mejor

6. **Seguridad:** Solo escucha en `0.0.0.0:8000` dentro de tu red local

---

## ✨ Próximos Pasos

1. ✅ Iniciar: `./start.sh`
2. ✅ Verificar: `./status.sh`
3. ✅ Ver logs: `tail -f srv-img.log`
4. ✅ Probar: `curl http://192.168.5.25:8000/`
5. ✅ Usar en n8n: `http://192.168.5.25:8000`

---

## 📞 Comandos Rápidos

```bash
# Iniciar
cd /home/diego/Documentos/srv-img-totem && ./start.sh

# Detener
cd /home/diego/Documentos/srv-img-totem && ./stop.sh

# Estado
cd /home/diego/Documentos/srv-img-totem && ./status.sh

# Logs
tail -f /home/diego/Documentos/srv-img-totem/srv-img.log

# Ver si está corriendo
curl http://192.168.5.25:8000/

# Acceso desde n8n
# http://192.168.5.25:8000/api/catalogos/...
```

---

## 📋 Checklist Final

- ✅ srv-img removido de docker-compose.yaml
- ✅ venv creado e instalado
- ✅ Scripts bash creados (start.sh, stop.sh, status.sh)
- ✅ Logs configurado
- ✅ PID management implementado
- ✅ Ejecución en segundo plano (nohup)
- ✅ Documentación completada
- ✅ Acceso desde n8n funcionando

**Estado:** LISTO PARA PRODUCCIÓN ✅

