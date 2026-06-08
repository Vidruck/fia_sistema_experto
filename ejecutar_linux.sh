#!/usr/bin/env bash
# ===========================================================================
#  ViajaIA — Lanzador inteligente para Linux
#  Detecta dependencias, crea el entorno virtual y ejecuta la aplicación.
#  Uso:
#    ./ejecutar_linux.sh              → instala (si es necesario) y ejecuta
#    ./ejecutar_linux.sh --reinstalar → borra el entorno y reinstala desde cero
# ===========================================================================

set -euo pipefail

# ── Colores ─────────────────────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; BOLD='\033[1m'; RESET='\033[0m'

log()   { echo -e "${CYAN}${BOLD}[ViajaIA]${RESET} $1"; }
ok()    { echo -e "${GREEN}  ✅ $1${RESET}"; }
warn()  { echo -e "${YELLOW}  ⚠️  $1${RESET}"; }
error() { echo -e "${RED}  ❌ $1${RESET}"; }

# ── Rutas ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv_viajaia"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

# ── Banner ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}"
echo "  ██╗   ██╗██╗ █████╗      ██╗ █████╗ "
echo "  ██║   ██║██║██╔══██╗     ██║██╔══██╗"
echo "  ██║   ██║██║███████║     ██║███████║"
echo "  ╚██╗ ██╔╝██║██╔══██║██   ██║██╔══██║"
echo "   ╚████╔╝ ██║██║  ██║╚█████╔╝██║  ██║"
echo "    ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚════╝ ╚═╝  ╚═╝"
echo -e "${RESET}"
echo -e "  ${BOLD}Sistema Experto de Recomendación de Vacaciones${RESET}"
echo "  ─────────────────────────────────────────────"
echo ""

# ── Argumento --reinstalar ───────────────────────────────────────────────────
if [[ "${1:-}" == "--reinstalar" ]]; then
    warn "Modo reinstalación: eliminando entorno virtual anterior..."
    rm -rf "$VENV_DIR"
    ok "Entorno eliminado. Se instalará desde cero."
fi

# ── Verificar Python 3 ───────────────────────────────────────────────────────
log "Verificando Python..."
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -ge 3 ]] && [[ "$minor" -ge 10 ]]; then
            PYTHON_CMD="$cmd"
            ok "Python $("$cmd" --version) detectado"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    error "Se requiere Python 3.10 o superior."
    echo ""
    echo "  Instalar en Ubuntu/Debian:"
    echo "    sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
    echo ""
    echo "  Instalar en Fedora/RHEL:"
    echo "    sudo dnf install -y python3 python3-pip"
    echo ""
    exit 1
fi

# ── Verificar python3-venv ───────────────────────────────────────────────────
if ! "$PYTHON_CMD" -c "import venv" 2>/dev/null; then
    warn "Módulo 'venv' no disponible. Intentando instalar..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-venv python3-pip
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-pip
    else
        error "Instala python3-venv manualmente y vuelve a ejecutar."
        exit 1
    fi
fi

# ── Verificar dependencias del sistema para PyQt6 (solo Linux) ──────────────
log "Verificando dependencias del sistema para la interfaz gráfica..."
MISSING_PKGS=()
for lib in libxcb-xinerama0 libgl1-mesa-glx libxkbcommon-x11-0 libdbus-1-3; do
    if command -v dpkg &>/dev/null && ! dpkg -l "$lib" 2>/dev/null | grep -q "^ii"; then
        MISSING_PKGS+=("$lib")
    fi
done

if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
    warn "Instalando librerías gráficas del sistema necesarias para PyQt6..."
    sudo apt-get install -y "${MISSING_PKGS[@]}" 2>/dev/null || \
        warn "No se pudieron instalar algunas librerías. La GUI podría no funcionar."
else
    ok "Librerías del sistema OK"
fi

# ── Crear o reutilizar entorno virtual ───────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
    log "Creando entorno virtual en .venv_viajaia/ ..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"

    log "Instalando dependencias (PyQt6 puede tardar 1-2 minutos)..."
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE" --quiet
    ok "Dependencias instaladas correctamente"
else
    ok "Entorno virtual existente reutilizado (.venv_viajaia/)"
    # Verificar que PyQt6 esté instalado
    if ! "$VENV_DIR/bin/python" -c "import PyQt6" 2>/dev/null; then
        warn "PyQt6 no encontrado en el entorno. Reinstalando dependencias..."
        "$VENV_DIR/bin/pip" install -r "$REQ_FILE" --quiet
        ok "Dependencias reinstaladas"
    fi
fi

# ── Lanzar la aplicación ─────────────────────────────────────────────────────
log "Iniciando ViajaIA... 🌴"
echo ""
cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" src/main.py "$@"
