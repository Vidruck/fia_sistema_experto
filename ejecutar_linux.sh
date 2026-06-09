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
PY_MINOR_DETECTED=0
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        raw_ver=$("$cmd" --version 2>&1)
        version=$(echo "$raw_ver" | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [[ "$major" -ge 3 ]] && [[ "$minor" -ge 10 ]]; then
            PYTHON_CMD="$cmd"
            PY_MINOR_DETECTED=$minor
            ok "Python $raw_ver detectado"
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

# ── Advertencia si Python >= 3.13 ────────────────────────────────────────────
# PyQt6 puede no tener wheel pre-compilada para versiones muy nuevas de Python.
# En ese caso se usará PyQt6 del sistema (apt) en lugar de pip.
USE_SYSTEM_PYQT=false
if [[ "$PY_MINOR_DETECTED" -ge 13 ]]; then
    warn "Python 3.${PY_MINOR_DETECTED} detectado. PyQt6 puede no tener wheel para esta versión."
    warn "Se intentará instalar PyQt6 desde el gestor de paquetes del sistema (más rápido y seguro)."
    USE_SYSTEM_PYQT=true
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

# ── Instalar PyQt6 desde el sistema si Python es demasiado nuevo ─────────────
if [[ "$USE_SYSTEM_PYQT" == true ]]; then
    log "Instalando PyQt6 y librerías gráficas desde el sistema..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y \
            python3-pyqt6 \
            python3-pyqt6.qtwidgets \
            libxcb-xinerama0 \
            libgl1 \
            libxkbcommon-x11-0 \
            libdbus-1-3 2>/dev/null && ok "PyQt6 del sistema instalado" \
            || warn "Instalación parcial. Continuando..."
    else
        warn "Sistema no es Debian/Ubuntu. Intentando con pip de todas formas..."
        USE_SYSTEM_PYQT=false
    fi
else
    # ── Verificar dependencias gráficas para distros Debian/Ubuntu ───────────
    log "Verificando dependencias del sistema para la interfaz gráfica..."
    MISSING_PKGS=()
    for lib in libxcb-xinerama0 libgl1 libxkbcommon-x11-0 libdbus-1-3; do
        if command -v dpkg &>/dev/null && ! dpkg -l "$lib" 2>/dev/null | grep -q "^ii"; then
            MISSING_PKGS+=("$lib")
        fi
    done
    if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
        warn "Instalando librerías gráficas del sistema..."
        sudo apt-get install -y "${MISSING_PKGS[@]}" 2>/dev/null || \
            warn "No se pudieron instalar algunas librerías. La GUI podría no funcionar."
    else
        ok "Librerías del sistema OK"
    fi
fi

# ── Crear o reutilizar entorno virtual ───────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
    log "Creando entorno virtual en .venv_viajaia/ ..."

    if [[ "$USE_SYSTEM_PYQT" == true ]]; then
        # Con --system-site-packages PyQt6 del sistema queda accesible dentro del venv
        "$PYTHON_CMD" -m venv --system-site-packages "$VENV_DIR"
        ok "Entorno virtual creado (con acceso a PyQt6 del sistema)"

        log "Instalando dependencias adicionales (pytest y otras)..."
        # Limpiar cache corrupta antes de instalar
        "$VENV_DIR/bin/pip" cache purge 2>/dev/null || true
        # Instalar todo excepto PyQt6 (ya viene del sistema)
        # Usamos --prefer-binary y --no-cache-dir para evitar compilaciones lentas
        "$VENV_DIR/bin/pip" install \
            --prefer-binary \
            --no-cache-dir \
            pytest==8.0.0
        ok "Dependencias adicionales instaladas"
    else
        "$PYTHON_CMD" -m venv "$VENV_DIR"

        log "Instalando dependencias (PyQt6 puede tardar 2-3 minutos en la primera vez)..."
        echo "  → Limpiando caché de pip..."
        "$VENV_DIR/bin/pip" cache purge 2>/dev/null || true

        echo "  → Actualizando pip..."
        "$VENV_DIR/bin/pip" install --upgrade pip --no-cache-dir --quiet

        echo "  → Instalando PyQt6 y pytest (muestra progreso)..."
        # --prefer-binary: prefiere wheels pre-compiladas, evita compilar desde fuente
        # --no-cache-dir:  evita los "Cache entry deserialization failed"
        "$VENV_DIR/bin/pip" install \
            --prefer-binary \
            --no-cache-dir \
            -r "$REQ_FILE"
        ok "Dependencias instaladas correctamente"
    fi
else
    ok "Entorno virtual existente reutilizado (.venv_viajaia/)"
    # Verificar que PyQt6 esté disponible
    if ! "$VENV_DIR/bin/python" -c "import PyQt6" 2>/dev/null; then
        warn "PyQt6 no encontrado. Reinstalando dependencias..."
        "$VENV_DIR/bin/pip" install \
            --prefer-binary \
            --no-cache-dir \
            -r "$REQ_FILE"
        ok "Dependencias reinstaladas"
    fi
fi

# ── Verificación rápida antes de lanzar ──────────────────────────────────────
log "Verificando integridad antes de lanzar..."
if "$VENV_DIR/bin/python" -c "import PyQt6; print('  ✅ PyQt6 OK')" 2>/dev/null; then
    true
else
    warn "PyQt6 no disponible. La app intentará arrancar en modo CLI."
fi

# ── Lanzar la aplicación ─────────────────────────────────────────────────────
log "Iniciando ViajaIA... 🌴"
echo ""
cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" src/main.py "$@"
