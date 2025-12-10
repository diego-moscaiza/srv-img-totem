import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del servidor
# SERVER_URL: Para acceso interno dentro de Docker
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

IMAGENES_DIR = os.getenv("IMAGENES_DIR", "imagenes")

# Configuración de Base de Datos
# Prioridad:
# 1. DATABASE_URL del .env (desarrollo local)
# 2. /srv/data/catalogos.db (Docker detectado automáticamente)
# 3. ./catalogos.db en la raíz del proyecto (fallback)
def get_database_url():
    """
    Determina la URL de la base de datos según el entorno:
    - Docker (producción): /srv/data/catalogos.db
    - Local (desarrollo): DATABASE_URL del .env o ./catalogos.db
    """
    # Si hay variable de entorno definida, usarla (desarrollo local con .env)
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Detectar si estamos en Docker (el directorio /srv existe)
    if Path("/srv/data").exists():
        return "sqlite:////srv/data/catalogos.db"

    # Local: usar ruta relativa al proyecto
    project_root = Path(__file__).parent.parent
    db_path = project_root / "catalogos.db"
    return f"sqlite:///{db_path}"


DATABASE_URL = get_database_url()

# Información de configuración
CONFIG_INFO = {
    "server_url": SERVER_URL,
    "imagenes_dir": IMAGENES_DIR,
    "database_url": DATABASE_URL,
}

print(f"[OK] Configuracion cargada desde .env")
print(f"  - SERVER_URL: {SERVER_URL}")


def get_image_url(ruta_relativa: str, use_external: bool = True) -> str:
    """
    Construye URL completa para imagen.
    
    Args:
        ruta_relativa: Ruta relativa de la imagen (ej: /api/catalogos/fnb/...)
        use_external: Si True, usa SERVER_URL (para URLs que van a externos)
                     Si False, usa SERVER_URL (para URLs internas)
    
    Returns:
        URL completa de la imagen
    """
    base_url = SERVER_URL if use_external else SERVER_URL
    # Asegurar que no hay doble slash
    if ruta_relativa.startswith('/'):
        return f"{base_url}{ruta_relativa}"
    else:
        return f"{base_url}/{ruta_relativa}"
print(f"  - IMAGENES_DIR: {IMAGENES_DIR}")
