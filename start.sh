#!/bin/bash

# ============================================================
# Script para ejecutar srv-img-totem sin Docker
# ============================================================
# Uso: ./start.sh [opciones]
# Opciones:
#   --help              Mostrar esta ayuda
#   --prod              Ejecutar en modo producción
#   --port PORT         Puerto personalizado (default: 8000)
#   --host HOST         Host personalizado (default: 0.0.0.0)
# ============================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables por defecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/venv"
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
WORKERS=2
RELOAD_FLAG="--reload"
LOG_LEVEL="info"

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            grep "^#" "$0" | tail -n +2
            exit 0
            ;;
        --prod)
            RELOAD_FLAG=""
            LOG_LEVEL="warning"
            WORKERS=4
            echo -e "${YELLOW}Modo producción activado${NC}"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            exit 1
            ;;
    esac
done

# Función para imprimir con colores
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "${SCRIPT_DIR}/main.py" ]; then
    print_error "main.py no encontrado en ${SCRIPT_DIR}"
fi

print_header "INICIANDO SRV-IMG-TOTEM"

# Verificar si venv existe
if [ ! -d "${VENV_PATH}" ]; then
    print_error "venv no encontrado. Ejecuta: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

print_success "venv encontrado"

# Activar venv
print_info "Activando venv..."
source "${VENV_PATH}/bin/activate"
print_success "venv activado"

# Verificar dependencias
print_info "Verificando dependencias..."
python3 -c "import fastapi, uvicorn, sqlalchemy" || print_error "Dependencias no instaladas correctamente"
print_success "Dependencias OK"

# Crear directorio de datos si no existe
if [ ! -d "${SCRIPT_DIR}/data" ]; then
    mkdir -p "${SCRIPT_DIR}/data"
    print_info "Directorio de datos creado: ${SCRIPT_DIR}/data"
fi

# Verificar .env
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    if [ -f "${SCRIPT_DIR}/.env.example" ]; then
        cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
        print_info "Archivo .env creado desde .env.example"
        print_info "Edita ${SCRIPT_DIR}/.env si necesitas cambiar la configuración"
    fi
fi

# Mostrar información de ejecución
print_header "INFORMACIÓN DE EJECUCIÓN"
echo -e "Directorio:     ${BLUE}${SCRIPT_DIR}${NC}"
echo -e "Python:         ${BLUE}$(python3 --version)${NC}"
echo -e "Host:           ${BLUE}${HOST}${NC}"
echo -e "Puerto:         ${BLUE}${PORT}${NC}"
echo -e "Reload:         ${BLUE}$([ -z "$RELOAD_FLAG" ] && echo "Deshabilitado (Producción)" || echo "Habilitado (Desarrollo)")${NC}"
echo -e "Log Level:      ${BLUE}${LOG_LEVEL}${NC}"
echo -e "Workers:        ${BLUE}${WORKERS}${NC}"

# URL de acceso
echo ""
echo -e "📌 ${GREEN}URL de acceso:${NC}"
echo -e "   ${BLUE}http://${HOST}:${PORT}${NC}"
echo -e "   ${BLUE}http://192.168.5.25:${PORT}${NC} (desde tu red)"
echo ""

# Crear archivo de log
LOG_FILE="${SCRIPT_DIR}/srv-img.log"
PID_FILE="${SCRIPT_DIR}/.srv-img.pid"

# Ejecutar servidor en segundo plano
print_header "INICIANDO SERVIDOR UVICORN"
print_info "El servidor continuará ejecutándose después de cerrar la terminal"
echo ""

if [ -z "$RELOAD_FLAG" ]; then
    # Modo producción (sin reload)
    nohup python3 -m uvicorn main:app \
        --host "${HOST}" \
        --port "${PORT}" \
        --log-level "${LOG_LEVEL}" \
        --workers "${WORKERS}" \
        > "${LOG_FILE}" 2>&1 &
else
    # Modo desarrollo (con reload)
    nohup python3 -m uvicorn main:app \
        --host "${HOST}" \
        --port "${PORT}" \
        --reload \
        --log-level "${LOG_LEVEL}" \
        > "${LOG_FILE}" 2>&1 &
fi

# Capturar PID del proceso
PID=$!
echo "$PID" > "${PID_FILE}"

print_success "Servidor iniciado con PID: ${BLUE}${PID}${NC}"
echo ""
echo -e "${GREEN}📌 Información importante:${NC}"
echo -e "   • PID guardado en: ${BLUE}${PID_FILE}${NC}"
echo -e "   • Logs guardados en: ${BLUE}${LOG_FILE}${NC}"
echo -e "   • Ver logs: ${BLUE}tail -f ${LOG_FILE}${NC}"
echo -e "   • Detener: ${BLUE}./stop.sh${NC}"
echo ""

# Esperar un segundo y verificar que el proceso sigue corriendo
sleep 2
if kill -0 "$PID" 2>/dev/null; then
    print_success "Servidor está corriendo correctamente"
    echo ""
    echo -e "${GREEN}📌 URL de acceso:${NC}"
    echo -e "   ${BLUE}http://localhost:${PORT}${NC}"
    echo -e "   ${BLUE}http://192.168.5.25:${PORT}${NC} (desde tu red)"
    echo ""
else
    print_error "El servidor falló al iniciar. Revisa los logs: tail -f ${LOG_FILE}"
fi
