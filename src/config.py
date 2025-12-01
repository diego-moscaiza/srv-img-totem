import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del servidor
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
IMAGENES_DIR = os.getenv("IMAGENES_DIR", "imagenes")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalogos.db")

# Información de configuración
CONFIG_INFO = {
    "server_url": SERVER_URL,
    "imagenes_dir": IMAGENES_DIR,
    "database_url": DATABASE_URL,
}

print(f"✓ Configuración cargada desde .env")
print(f"  - SERVER_URL: {SERVER_URL}")
print(f"  - IMAGENES_DIR: {IMAGENES_DIR}")
