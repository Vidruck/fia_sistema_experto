# ===========================================================================
#  ViajaIA — Lanzador PowerShell para Windows 11
#  Modo de uso:
#    Click derecho en este archivo → "Ejecutar con PowerShell"
#  O desde terminal:
#    powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1
#    powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1 -Reinstalar
# ===========================================================================
param(
    [switch]$Reinstalar
)

# Habilitar colores en la consola de Windows
$Host.UI.RawUI.WindowTitle = "ViajaIA — Sistema Experto de Vacaciones"

function Write-Banner {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                                  ║" -ForegroundColor Cyan
    Write-Host "  ║   🌴  ViajaIA — Sistema Experto de Vacaciones   ║" -ForegroundColor Cyan
    Write-Host "  ║        Lanzador PowerShell para Windows 11       ║" -ForegroundColor Cyan
    Write-Host "  ║                                                  ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step  { param($msg) Write-Host "  [→] $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "  [✓] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "  [!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "  [✗] $msg" -ForegroundColor Red }

# ── Rutas ────────────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir   = Join-Path $ScriptDir ".venv_viajaia"
$ReqFile   = Join-Path $ScriptDir "requirements.txt"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PipExe    = Join-Path $VenvDir "Scripts\pip.exe"

Write-Banner

# ── Modo reinstalación ───────────────────────────────────────────────────────
if ($Reinstalar) {
    Write-Warn "Modo reinstalación activado. Eliminando entorno anterior..."
    if (Test-Path $VenvDir) {
        Remove-Item -Recurse -Force $VenvDir
        Write-Ok "Entorno eliminado. Se instalará desde cero."
    } else {
        Write-Ok "No había entorno previo."
    }
}

# ── Verificar Python ─────────────────────────────────────────────────────────
Write-Step "Verificando Python..."

$PythonCmd = $null
$PythonVer = $null

# Buscar python, python3, py
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+\.\d+\.\d+)") {
            $versionStr = $Matches[1]
            $parts = $versionStr.Split(".")
            if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 10) {
                $PythonCmd = $cmd
                $PythonVer = $versionStr
                break
            }
        }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Error "Python 3.10 o superior no encontrado."
    Write-Host ""
    Write-Host "  Pasos para instalar Python en Windows:" -ForegroundColor White
    Write-Host "    1. Ve a: https://python.org/downloads" -ForegroundColor White
    Write-Host "    2. Descarga Python 3.11 o superior" -ForegroundColor White
    Write-Host "    3. En el instalador, marca: 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "    4. Reinicia PowerShell y vuelve a ejecutar" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

Write-Ok "Python $PythonVer detectado ($PythonCmd)"

# ── Crear o reutilizar entorno virtual ───────────────────────────────────────
if (-not (Test-Path $VenvDir)) {
    Write-Step "Creando entorno virtual en .venv_viajaia\ ..."
    & $PythonCmd -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "No se pudo crear el entorno virtual."
        Read-Host "Presiona Enter para cerrar"
        exit 1
    }

    Write-Step "Instalando dependencias (PyQt6 puede tardar 2-3 minutos)..."
    & $PipExe install --upgrade pip --quiet
    & $PipExe install -r $ReqFile --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Fallo al instalar dependencias. Verifica tu conexión a internet."
        Write-Warn "Intenta: powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1 -Reinstalar"
        Read-Host "Presiona Enter para cerrar"
        exit 1
    }
    Write-Ok "Dependencias instaladas correctamente"
} else {
    Write-Ok "Entorno virtual reutilizado (.venv_viajaia\)"

    # Verificar que PyQt6 esté instalado
    $pyqt6Check = & $PythonExe -c "import PyQt6; print('ok')" 2>&1
    if ($pyqt6Check -ne "ok") {
        Write-Warn "PyQt6 no encontrado. Reinstalando dependencias..."
        & $PipExe install -r $ReqFile --quiet
        Write-Ok "Dependencias reinstaladas"
    }
}

# ── Lanzar la aplicación ─────────────────────────────────────────────────────
Write-Step "Iniciando ViajaIA... 🌴"
Write-Host ""
Set-Location $ScriptDir

& $PythonExe src\main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Error "La aplicación cerró con un error (código: $LASTEXITCODE)."
    Write-Warn "Si el error es de pantalla/display, verifica que tengas drivers de video actualizados."
    Read-Host "Presiona Enter para cerrar"
}
