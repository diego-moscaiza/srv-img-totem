# Configuración de URLs - Servidor de Catálogos

## Cambiar la URL del Servidor

Para cambiar la URL del servidor (hostname o IP), simplemente edita el archivo `.env` en la raíz del proyecto:

### Opciones de configuración:

```env
# Opción 1: Usar IP local (RECOMENDADO) ✓
SERVER_URL=http://192.168.1.65:8000

# Opción 2: Usar localhost (desarrollo local)
SERVER_URL=http://localhost:8000

# Opción 3: Usar nombre de host (requiere configuración DNS/hosts)
SERVER_URL=http://srv-catalogos:8000
```

## Configuración actual

```
✓ SERVER_URL=http://192.168.1.65:8000
```

## Cómo funciona

1. El archivo `.env` contiene la variable `SERVER_URL`
2. El archivo `src/config.py` lee esta variable
3. El script `fix_imagenes.py` actualiza todas las URLs en la base de datos
4. Ejecuta: `python fix_imagenes.py`

## Flujo completo

### 1. Editar `.env`
```bash
# Cambiar SERVER_URL a lo que necesites
SERVER_URL=http://192.168.1.65:8000
```

### 2. Ejecutar el script de actualización
```bash
python fix_imagenes.py
```

### 3. Reiniciar el servidor
```bash
# El servidor se reinicia automáticamente
python main.py
```

## Ejemplo de URLs en la base de datos después de ejecutar:

```
http://192.168.1.65:8000/api/catalogos/fnb/2025/11-noviembre/1-celulares/caracteristicas/01.png
http://192.168.1.65:8000/api/catalogos/fnb/2025/11-noviembre/1-celulares/precios/01.png
```

## Nota importante

- **No requiere modificar el sistema operativo** (no necesitas editar `/etc/hosts` o archivo hosts de Windows)
- La configuración está **completamente dentro del proyecto**
- Solo necesitas cambiar `SERVER_URL` en `.env` y ejecutar `fix_imagenes.py`

## Opción de nombre de host (avanzado)

Si quieres usar `http://srv-catalogos:8000` en lugar de la IP, necesitarás:

### En Windows:
1. Abre `C:\Windows\System32\drivers\etc\hosts` como Administrador
2. Agrega esta línea:
   ```
   192.168.1.65 srv-catalogos
   ```
3. Guarda y cierra
4. Cambia `.env`:
   ```
   SERVER_URL=http://srv-catalogos:8000
   ```
5. Ejecuta: `python fix_imagenes.py`
