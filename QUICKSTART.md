#!/bin/bash

# ============================================================
# Script de demostración rápida
# ============================================================

cd /home/diego/Documentos/srv-img-totem

echo "================================================"
echo "DEMOSTRACIÓN: srv-img-totem sin Docker"
echo "================================================"
echo ""

echo "1. Iniciando srv-img-totem en segundo plano..."
echo "   ./start.sh"
echo ""

echo "2. El servidor continuará ejecutándose después de cerrar la terminal"
echo ""

echo "3. Ver estado:"
echo "   ./status.sh"
echo ""

echo "4. Ver logs en tiempo real:"
echo "   tail -f srv-img.log"
echo ""

echo "5. Probar el servidor:"
echo "   curl http://192.168.5.25:8000/"
echo ""

echo "6. Detener cuando no lo necesites:"
echo "   ./stop.sh"
echo ""

echo "================================================"
echo "¿Listo para probar? Ejecuta:"
echo ""
echo "  cd /home/diego/Documentos/srv-img-totem"
echo "  ./start.sh"
echo ""
echo "================================================"
