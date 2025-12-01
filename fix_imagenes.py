import os
from dotenv import load_dotenv
from src.database import SessionLocal, Producto

# Cargar variables de entorno
load_dotenv()
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

db = SessionLocal()
productos = db.query(Producto).all()

print("Actualizando rutas de imágenes...")
actualizados = 0

for p in productos:
    actualizado = False

    # Función auxiliar para normalizar rutas
    def normalizar_ruta(ruta):
        if not ruta:
            return ""

        # Si ya es una URL completa, extraer la ruta relativa
        if ruta.startswith("http"):
            ruta = (
                ruta.split("/api/catalogos/")[-1]
                if "/api/catalogos/" in ruta
                else ruta.split("/ver-ruta/")[-1]
            )

        # Remover prefijo "catalogos/" si existe
        if ruta.startswith("catalogos/"):
            ruta = ruta.replace("catalogos/", "")

        # Corregir "noviembre" por "11-noviembre"
        if "/noviembre/" in ruta:
            ruta = ruta.replace("/noviembre/", "/11-noviembre/")

        # Reordenar si es "2025/fnb/" a "fnb/2025/"
        if ruta.startswith("2025/fnb/") or ruta.startswith("2025/gaso/"):
            partes = ruta.split("/")
            if partes[0] == "2025" and partes[1] in ["fnb", "gaso"]:
                segmento = partes[1]
                year = partes[0]
                resto = "/".join(partes[2:])
                ruta = f"{segmento}/{year}/{resto}"

        # Validar que inicie con segmento válido
        if not ruta or (not ruta.startswith("fnb/") and not ruta.startswith("gaso/")):
            return ""

        # Construir URL completa
        return f"{SERVER_URL}/api/catalogos/{ruta}"

    # Actualizar imagen_listado
    if p.imagen_listado:
        ruta_nueva = normalizar_ruta(p.imagen_listado)
        if ruta_nueva and ruta_nueva != p.imagen_listado:
            p.imagen_listado = ruta_nueva
            actualizado = True
        elif not ruta_nueva:
            p.imagen_listado = ""
            actualizado = True

    # Actualizar imagen_caracteristicas
    if p.imagen_caracteristicas:
        ruta_nueva = normalizar_ruta(p.imagen_caracteristicas)
        if ruta_nueva and ruta_nueva != p.imagen_caracteristicas:
            p.imagen_caracteristicas = ruta_nueva
            actualizado = True
        elif not ruta_nueva:
            p.imagen_caracteristicas = ""
            actualizado = True

    if actualizado:
        actualizados += 1
        print(f"  ✓ {p.codigo}")
        print(f"    - listado: {p.imagen_listado}")
        print(f"    - características: {p.imagen_caracteristicas}")

db.commit()
db.close()

print(f"\nTotal actualizado: {actualizados} productos")
