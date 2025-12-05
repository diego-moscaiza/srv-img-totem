#!/bin/bash

# ============================================================
# Script para detener srv-img-totem
# ============================================================
# Uso: ./stop.sh
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

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DETENIENDO SRV-IMG-TOTEM${NC}"
echo -e "${BLUE}========================================${NC}"

# Opción 1: Si existe archivo PID
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    print_info "Encontrado PID en ${PID_FILE}: ${BLUE}${PID}${NC}"
    
    if kill -0 "$PID" 2>/dev/null; then
        print_info "Deteniendo proceso PID ${BLUE}${PID}${NC}..."
        kill "$PID"
        sleep 2
        
        if kill -0 "$PID" 2>/dev/null; then
            print_info "Forzando terminación con kill -9..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        print_success "Proceso detenido"
    else
        print_info "El proceso ${BLUE}${PID}${NC} no está ejecutándose"
        rm -f "$PID_FILE"
    fi
else
    print_info "No se encontró archivo PID. Buscando proceso..."
    
    # Opción 2: Buscar por proceso
    PID=$(pgrep -f "uvicorn main:app" | head -1)
    
    if [ -z "$PID" ]; then
        print_info "No hay proceso de srv-img-totem ejecutándose"
        exit 0
    fi
    
    print_info "Encontrado proceso: ${BLUE}${PID}${NC}"
    kill "$PID" && print_success "Proceso detenido correctamente" || {
        print_info "Forzando terminación..."
        kill -9 "$PID" && print_success "Proceso forzosamente terminado"
    }
fi

echo ""
echo -e "${GREEN}📌 Información:${NC}"
echo -e "   Logs disponibles en: ${BLUE}${LOG_FILE}${NC}"
echo -e "   Ver logs: ${BLUE}tail -f ${LOG_FILE}${NC}"
echo ""
