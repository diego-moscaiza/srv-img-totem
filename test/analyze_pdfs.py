#!/usr/bin/env python3
"""
Script para analizar y listar todos los PDFs disponibles en imagenes/catalogos/

Uso:
  cd srv-img-totem
  python test/analyze_pdfs.py
"""

from pathlib import Path
from collections import defaultdict

# Ruta base de catálogos
imagenes_dir = Path(__file__).parent.parent / "imagenes" / "catalogos"

print("=" * 80)
print("ANÁLISIS DE PDFs EN imagenes/catalogos/")
print("=" * 80)

if not imagenes_dir.exists():
    print(f"❌ Error: No se encuentra la carpeta {imagenes_dir}")
    exit(1)

# Buscar todos los PDFs
pdfs_por_periodo = defaultdict(list)
pdfs_catalogo_completo = []

for pdf_path in imagenes_dir.rglob("*.pdf"):
    # Obtener la ruta relativa desde imagenes/catalogos
    rel_path = pdf_path.relative_to(imagenes_dir)
    parts = rel_path.parts

    if len(parts) >= 4:
        segmento = parts[0]
        ano = parts[1]
        mes = parts[2]
        categoria = parts[3]

        # Verificar si es catálogo completo (nombre específico)
        nombre_archivo = pdf_path.name.lower()
        if "completo" in nombre_archivo or "catalogo" in nombre_archivo:
            pdfs_catalogo_completo.append(
                {
                    "segmento": segmento,
                    "año": ano,
                    "mes": mes,
                    "archivo": pdf_path.name,
                    "ruta_relativa": str(rel_path),
                    "tamaño": pdf_path.stat().st_size,
                }
            )
        else:
            periodo_key = f"{segmento}/{ano}/{mes}"
            pdfs_por_periodo[periodo_key].append(
                {
                    "categoria": categoria,
                    "archivo": pdf_path.name,
                    "ruta_relativa": str(rel_path),
                    "tamaño": pdf_path.stat().st_size,
                }
            )

# Mostrar PDFs por período
print("\n📋 PDFs POR PERÍODO Y CATEGORÍA:")
print("-" * 80)

if pdfs_por_periodo:
    for periodo in sorted(pdfs_por_periodo.keys()):
        pdfs = pdfs_por_periodo[periodo]
        print(f"\n📁 {periodo}")
        print(f"   Total: {len(pdfs)} PDF(s)")
        for pdf_info in sorted(pdfs, key=lambda x: x["categoria"]):
            tamaño_mb = pdf_info["tamaño"] / (1024 * 1024)
            print(
                f"   ├─ [{pdf_info['categoria']}] {pdf_info['archivo']} ({tamaño_mb:.2f} MB)"
            )
else:
    print("❌ No se encontraron PDFs por categoría")

# Mostrar catálogos completos
print("\n\n🎯 CATÁLOGOS COMPLETOS:")
print("-" * 80)

if pdfs_catalogo_completo:
    for catalogo in sorted(
        pdfs_catalogo_completo, key=lambda x: (x["segmento"], x["año"], x["mes"])
    ):
        tamaño_mb = catalogo["tamaño"] / (1024 * 1024)
        print(f"\n📦 {catalogo['segmento']}/{catalogo['año']}/{catalogo['mes']}")
        print(f"   ├─ {catalogo['archivo']} ({tamaño_mb:.2f} MB)")
        print(f"   └─ Ruta: {catalogo['ruta_relativa']}")
else:
    print("❌ No se encontraron catálogos completos")

# Resumen
print("\n" + "=" * 80)
print("📊 RESUMEN:")
print("=" * 80)
total_pdf_por_periodo = sum(len(v) for v in pdfs_por_periodo.values())
total_catalogo_completo = len(pdfs_catalogo_completo)
total_general = total_pdf_por_periodo + total_catalogo_completo

print(f"PDFs por categoría: {total_pdf_por_periodo}")
print(f"Catálogos completos: {total_catalogo_completo}")
print(f"TOTAL GENERAL: {total_general} PDF(s)")
print("=" * 80)
