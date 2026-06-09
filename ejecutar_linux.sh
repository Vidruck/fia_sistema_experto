#!/usr/bin/env bash
# ===========================================================================
#  ViajaIA — Lanzador inteligente para Linux
#  Compatible con: Debian/Ubuntu/Mint · Arch/Manjaro/EndeavourOS · Fedora/RHEL
#  Sesiones: X11 · Wayland (nativo) · XWayland (fallback)
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

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 1: Detectar sesión gráfica (Wayland / X11)
# ════════════════════════════════════════════════════════════════════════════
log "Detectando tipo de sesión gráfica..."

SESSION_TYPE="${XDG_SESSION_TYPE:-x11}"
IS_WAYLAND=false
if [[ -n "${WAYLAND_DISPLAY:-}" ]] || [[ "$SESSION_TYPE" == "wayland" ]]; then
    IS_WAYLAND=true
    ok "Sesión Wayland detectada (WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-?})"
else
    ok "Sesión X11 detectada (DISPLAY=${DISPLAY:-?})"
fi

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 2: Detectar gestor de paquetes y distribución
# ════════════════════════════════════════════════════════════════════════════
log "Detectando distribución de Linux..."

PKG_MGR=""
DISTRO_FAMILY=""

if command -v pacman &>/dev/null; then
    PKG_MGR="pacman"
    DISTRO_FAMILY="arch"
    ok "Familia Arch detectada (pacman)"
elif command -v apt-get &>/dev/null; then
    PKG_MGR="apt-get"
    DISTRO_FAMILY="debian"
    ok "Familia Debian/Ubuntu detectada (apt-get)"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
    DISTRO_FAMILY="fedora"
    ok "Familia Fedora/RHEL detectada (dnf)"
elif command -v zypper &>/dev/null; then
    PKG_MGR="zypper"
    DISTRO_FAMILY="suse"
    ok "Familia openSUSE detectada (zypper)"
else
    warn "No se detectó un gestor de paquetes conocido. Se intentará solo con pip."
    DISTRO_FAMILY="unknown"
fi

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 3: Verificar Python 3
# ════════════════════════════════════════════════════════════════════════════
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
    case "$DISTRO_FAMILY" in
        arch)    echo "  sudo pacman -S python" ;;
        debian)  echo "  sudo apt install python3 python3-pip python3-venv" ;;
        fedora)  echo "  sudo dnf install python3 python3-pip" ;;
        suse)    echo "  sudo zypper install python3 python3-pip" ;;
        *)       echo "  Instala Python 3.10+ desde: https://python.org/downloads" ;;
    esac
    echo ""
    exit 1
fi

# En Arch siempre usamos packages del sistema (Arch actualiza Python y PyQt6 juntos)
USE_SYSTEM_PYQT=false
if [[ "$DISTRO_FAMILY" == "arch" ]]; then
    USE_SYSTEM_PYQT=true
    ok "Arch Linux: se usará PyQt6 del sistema para garantizar compatibilidad"
elif [[ "$PY_MINOR_DETECTED" -ge 13 ]]; then
    warn "Python 3.${PY_MINOR_DETECTED}: sin wheel de PyQt6 en PyPI → se usará PyQt6 del sistema"
    USE_SYSTEM_PYQT=true
fi

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 4: Instalar dependencias del sistema según distro
# ════════════════════════════════════════════════════════════════════════════
_instalar_paquetes_sistema() {
    log "Instalando dependencias del sistema..."

    case "$DISTRO_FAMILY" in
        arch)
            # Arch: python-pyqt6 + qt6-wayland (para soporte Wayland nativo)
            local pkgs=("python-pyqt6" "qt6-wayland" "qt6-base")
            local faltantes=()
            for pkg in "${pkgs[@]}"; do
                if ! pacman -Qq "$pkg" &>/dev/null; then
                    faltantes+=("$pkg")
                fi
            done
            if [[ ${#faltantes[@]} -gt 0 ]]; then
                warn "Instalando: ${faltantes[*]}"
                sudo pacman -S --noconfirm --needed "${faltantes[@]}"
            fi
            ok "Paquetes Arch instalados: python-pyqt6, qt6-wayland"
            ;;

        debian)
            # Debian/Ubuntu: python3-pyqt6 + librerías gráficas + qt6-wayland
            local apt_pkgs=("python3-pyqt6" "libxcb-xinerama0" "libgl1"
                            "libxkbcommon-x11-0" "libdbus-1-3")
            # qt6-wayland puede no estar disponible en versiones viejas de Ubuntu
            if apt-cache show qt6-wayland &>/dev/null 2>&1; then
                apt_pkgs+=("qt6-wayland")
            fi
            local apt_faltantes=()
            for pkg in "${apt_pkgs[@]}"; do
                if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
                    apt_faltantes+=("$pkg")
                fi
            done
            if [[ ${#apt_faltantes[@]} -gt 0 ]]; then
                warn "Instalando: ${apt_faltantes[*]}"
                sudo apt-get install -y "${apt_faltantes[@]}"
            fi
            ok "Paquetes Debian/Ubuntu instalados"
            ;;

        fedora)
            local dnf_pkgs=("python3-pyqt6" "qt6-qtwayland")
            sudo dnf install -y --skip-unavailable "${dnf_pkgs[@]}" 2>/dev/null || \
                warn "Instalación parcial de paquetes Fedora"
            ok "Paquetes Fedora instalados"
            ;;

        suse)
            sudo zypper install -y python3-PyQt6 qt6-wayland 2>/dev/null || \
                warn "Instalación parcial de paquetes openSUSE"
            ok "Paquetes openSUSE instalados"
            ;;

        *)
            warn "Distro no reconocida. Saltando instalación de paquetes del sistema."
            ;;
    esac
}

if [[ "$USE_SYSTEM_PYQT" == true ]]; then
    _instalar_paquetes_sistema
else
    # Solo instalar librerías gráficas (sin PyQt6 del sistema)
    log "Verificando librerías gráficas del sistema..."
    if [[ "$DISTRO_FAMILY" == "debian" ]]; then
        MISSING=()
        for lib in libxcb-xinerama0 libgl1 libxkbcommon-x11-0; do
            dpkg -l "$lib" 2>/dev/null | grep -q "^ii" || MISSING+=("$lib")
        done
        if [[ ${#MISSING[@]} -gt 0 ]]; then
            sudo apt-get install -y "${MISSING[@]}" 2>/dev/null || true
        fi
    fi
    ok "Librerías del sistema verificadas"
fi

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 5: Crear / reutilizar entorno virtual
# ════════════════════════════════════════════════════════════════════════════
if [[ ! -d "$VENV_DIR" ]]; then

    if [[ "$USE_SYSTEM_PYQT" == true ]]; then
        log "Creando entorno virtual con acceso a PyQt6 del sistema..."
        "$PYTHON_CMD" -m venv --system-site-packages "$VENV_DIR"
        ok "Entorno virtual creado (--system-site-packages)"

        log "Instalando dependencias adicionales (pytest)..."
        "$VENV_DIR/bin/pip" cache purge 2>/dev/null || true
        "$VENV_DIR/bin/pip" install --prefer-binary --no-cache-dir pytest==8.0.0
        ok "pytest instalado"

    else
        log "Creando entorno virtual aislado..."
        "$PYTHON_CMD" -m venv "$VENV_DIR"

        log "Instalando dependencias de pip (muestra progreso)..."
        "$VENV_DIR/bin/pip" cache purge 2>/dev/null || true
        "$VENV_DIR/bin/pip" install --upgrade pip --no-cache-dir --quiet
        "$VENV_DIR/bin/pip" install --prefer-binary --no-cache-dir -r "$REQ_FILE"
        ok "Dependencias pip instaladas"
    fi

else
    ok "Entorno virtual existente reutilizado (.venv_viajaia/)"
    if ! "$VENV_DIR/bin/python" -c "import PyQt6" 2>/dev/null; then
        warn "PyQt6 no encontrado. Reinstalando..."
        if [[ "$USE_SYSTEM_PYQT" == true ]]; then
            _instalar_paquetes_sistema
        else
            "$VENV_DIR/bin/pip" install --prefer-binary --no-cache-dir -r "$REQ_FILE"
        fi
        ok "Dependencias reinstaladas"
    fi
fi

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 6: Configurar plataforma Qt según sesión gráfica
# ════════════════════════════════════════════════════════════════════════════
log "Configurando plataforma Qt para la sesión actual..."

if [[ "$IS_WAYLAND" == true ]]; then
    # Verificar que el plugin de Wayland para Qt6 esté disponible
    QT_WAYLAND_OK=false

    case "$DISTRO_FAMILY" in
        arch)
            pacman -Qq qt6-wayland &>/dev/null && QT_WAYLAND_OK=true ;;
        debian)
            (dpkg -l qt6-wayland 2>/dev/null | grep -q "^ii" || \
             ls /usr/lib/*/qt6/plugins/platforms/libqwayland*.so 2>/dev/null | head -1 | grep -q .) \
            && QT_WAYLAND_OK=true ;;
        fedora)
            rpm -q qt6-qtwayland &>/dev/null && QT_WAYLAND_OK=true ;;
        *)
            # Intento genérico: buscar la librería del plugin
            find /usr -name "libqwayland*.so" 2>/dev/null | grep -q . && QT_WAYLAND_OK=true ;;
    esac

    if [[ "$QT_WAYLAND_OK" == true ]]; then
        export QT_QPA_PLATFORM=wayland
        # Necesario en algunos compositores (GNOME/KDE Wayland) para que Qt6 no use decoraciones propias
        export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
        ok "Plataforma Qt: wayland (nativo)"
    else
        warn "Plugin Qt6-Wayland no encontrado → usando XWayland como fallback"
        warn "Para instalarlo:"
        case "$DISTRO_FAMILY" in
            arch)   warn "  sudo pacman -S qt6-wayland" ;;
            debian) warn "  sudo apt install qt6-wayland" ;;
            fedora) warn "  sudo dnf install qt6-qtwayland" ;;
        esac
        export QT_QPA_PLATFORM=xcb
        ok "Plataforma Qt: xcb (XWayland fallback)"
    fi
else
    export QT_QPA_PLATFORM=xcb
    ok "Plataforma Qt: xcb (X11)"
fi

# Variables adicionales de compatibilidad Qt6
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export PYTHONDONTWRITEBYTECODE=1

# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 7: Verificación rápida y lanzamiento
# ════════════════════════════════════════════════════════════════════════════
log "Verificando integridad..."
"$VENV_DIR/bin/python" -c "import PyQt6; print('  ✅ PyQt6 importado OK')" 2>/dev/null \
    || warn "No se pudo importar PyQt6 — la app intentará arrancar en modo CLI"

echo ""
log "Iniciando ViajaIA... 🌴"
echo -e "  Sesión: ${BOLD}$SESSION_TYPE${RESET}  |  Qt platform: ${BOLD}${QT_QPA_PLATFORM}${RESET}"
echo ""
cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" src/main.py "$@"
