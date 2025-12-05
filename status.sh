#!/bin/bash

# ============================================================
# Script para verificar estado de srv-img-totem
# ============================================================
# Uso: ./status.sh
# ============================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/.srv-img.pid"
LOG_FILE="${SCRIPT_DIR}/srv-img.log"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_running() {
    echo -e "${GREEN}●${NC} EJECUTÁNDOSE"
}

print_stopped() {
    echo -e "${RED}●${NC} DETENIDO"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_header "ESTADO DE SRV-IMG-TOTEM"

# Verificar si existe archivo PID
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        echo ""
        echo -e "Estado:          $(print_running)"
        echo -e "PID:             ${BLUE}${PID}${NC}"
        echo -e "Archivo PID:     ${BLUE}${PID_FILE}${NC}"
        echo ""
        
        # Obtener información adicional del proceso
        if command -v ps &> /dev/null; then
            echo -e "${YELLOW}Información del proceso:${NC}"
            ps -p "$PID" -o pid,cmd,etime,rss | tail -n +2 | \
            awk -v blue="$BLUE" -v nc="$NC" '{printf "  PID: %s, Memoria: %s KB, Tiempo: %s\n", $1, $4, $3}'
        fi
        
        echo ""
        echo -e "${YELLOW}Puertos escuchando:${NC}"
        if command -v lsof &> /dev/null; then
            lsof -p "$PID" -P -n | grep LISTEN | awk '{print "  " $9}' || echo "  (No se pueden obtener detalles)"
        elif command -v netstat &> /dev/null; then
            netstat -tlnp 2>/dev/null | grep "$PID" | awk '{print "  " $4}' || echo "  (No se pueden obtener detalles)"
        fi
    else
        echo ""
        echo -e "Estado:          $(print_stopped)"
        echo -e "PID en archivo:  ${RED}${PID} (no existe)${NC}"
        echo ""
        print_info "Eliminar archivo PID..."
        rm -f "$PID_FILE"
    fi
else
    # Buscar por proceso
    PID=$(pgrep -f "uvicorn main:app" | head -1)
    
    if [ -n "$PID" ]; then
        echo ""
        echo -e "Estado:          $(print_running)"
        echo -e "PID encontrado:  ${BLUE}${PID}${NC}"
        echo -e "Nota:            El archivo PID no existe (iniciado manualmente?)"
    else
        echo ""
        echo -e "Estado:          $(print_stopped)"
        echo -e "Nota:            El servidor no está ejecutándose"
    fi
fi

echo ""
echo -e "${YELLOW}Archivos útiles:${NC}"
echo -e "  Logs:        ${BLUE}${LOG_FILE}${NC}"
echo -e "  Ver logs:    ${BLUE}tail -f ${LOG_FILE}${NC}"
echo -e "  Últimas 20:  ${BLUE}tail -20 ${LOG_FILE}${NC}"

echo ""
echo -e "${YELLOW}Comandos disponibles:${NC}"
echo -e "  Iniciar:     ${BLUE}./start.sh${NC}"
echo -e "  Detener:     ${BLUE}./stop.sh${NC}"
echo -e "  Logs:        ${BLUE}tail -f srv-img.log${NC}"
echo -e "  Acceso:      ${BLUE}http://192.168.5.25:8000${NC}"

echo ""
