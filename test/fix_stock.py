#!/usr/bin/env python3
"""Script temporal para sincronizar stock con estado"""
import sqlite3

conn = sqlite3.connect('catalogos.db')
cur = conn.cursor()

# Sincronizar: si estado='agotado', stock debe ser 0
cur.execute("UPDATE productos SET stock=0 WHERE estado='agotado'")
conn.commit()

print("✅ Actualizado: productos agotados ahora tienen stock=0")
print("\nResultados actuales:")
cur.execute("SELECT codigo, estado, stock FROM productos")
for r in cur.fetchall():
    print(f"  {r[0]}: estado={r[1]}, stock={r[2]}")

conn.close()
