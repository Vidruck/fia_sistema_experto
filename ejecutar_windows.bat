@echo off
:: ===========================================================================
::  ViajaIA — Lanzador para Windows 11
::  Detecta Python, instala dependencias y ejecuta la aplicación.
::  Doble clic para iniciar. Si falla, ejecutar como Administrador.
:: ===========================================================================
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title ViajaIA — Sistema Experto de Vacaciones

set "SCRIPT_DIR=%~dp0"
:: Quitar barra final
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "VENV_DIR=%SCRIPT_DIR%\.venv_viajaia"
set "REQ_FILE=%SCRIPT_DIR%\requirements.txt"

:: ── Banner ──────────────────────────────────────────────────────────────────
echo.
echo   ^+--------------------------------------------------^+
echo   ^|                                                  ^|
echo   ^|    ViajaIA - Sistema Experto de Vacaciones       ^|
echo   ^|    Lanzador para Windows 11                      ^|
echo   ^|                                                  ^|
echo   ^+--------------------------------------------------^+
echo.

:: ── Argumento --reinstalar ──────────────────────────────────────────────────
if /i "%~1"=="--reinstalar" (
    echo   [*] Modo reinstalacion: eliminando entorno anterior...
    if exist "%VENV_DIR%" (
        rmdir /s /q "%VENV_DIR%"
        echo   [OK] Entorno eliminado. Se instalara desde cero.
    )
)

:: ── Verificar Python ────────────────────────────────────────────────────────
echo   [*] Verificando Python...

:: Intentar python primero, luego py
set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    set "PYTHON_CMD=python"
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2 delims= " %%v in ('py --version 2^>^&1') do set "PY_VER=%%v"
    set "PYTHON_CMD=py"
    goto :python_found
)

:: Python no encontrado
echo.
echo   [ERROR] Python no encontrado en el sistema.
echo.
echo   Pasos para instalarlo:
echo     1. Ve a: https://python.org/downloads
echo     2. Descarga Python 3.11 o superior
echo     3. En el instalador, marca: "Add Python to PATH"
echo     4. Reinicia esta ventana y vuelve a ejecutar
echo.
echo   Si ya lo instalaste, cierra y vuelve a abrir esta ventana.
echo.
pause
exit /b 1

:python_found
echo   [OK] Python %PY_VER% detectado (%PYTHON_CMD%)

:: Verificar version minima (3.10+)
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)
if %PY_MAJOR% lss 3 (
    echo   [ERROR] Se requiere Python 3.10+. Version actual: %PY_VER%
    pause
    exit /b 1
)
if %PY_MAJOR% equ 3 if %PY_MINOR% lss 10 (
    echo   [AVISO] Version %PY_VER% puede funcionar pero se recomienda 3.11+
)

:: ── Crear o reutilizar entorno virtual ──────────────────────────────────────
if not exist "%VENV_DIR%" (
    echo   [*] Creando entorno virtual en .venv_viajaia\ ...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo   [ERROR] No se pudo crear el entorno virtual.
        echo   Intenta: %PYTHON_CMD% -m pip install virtualenv
        pause
        exit /b 1
    )

    echo   [*] Instalando dependencias ^(PyQt6 puede tardar 2-3 minutos^)...
    "%VENV_DIR%\Scripts\pip.exe" install --upgrade pip --quiet
    "%VENV_DIR%\Scripts\pip.exe" install -r "%REQ_FILE%" --quiet
    if errorlevel 1 (
        echo   [ERROR] Fallo al instalar dependencias.
        echo   Verifica tu conexion a internet e intenta nuevamente.
        echo   O ejecuta: ejecutar_windows.bat --reinstalar
        pause
        exit /b 1
    )
    echo   [OK] Dependencias instaladas
) else (
    echo   [OK] Entorno virtual encontrado ^(.venv_viajaia\^)

    :: Verificar que PyQt6 exista
    "%VENV_DIR%\Scripts\python.exe" -c "import PyQt6" >nul 2>&1
    if errorlevel 1 (
        echo   [*] PyQt6 no encontrado. Reinstalando dependencias...
        "%VENV_DIR%\Scripts\pip.exe" install -r "%REQ_FILE%" --quiet
        echo   [OK] Dependencias reinstaladas
    )
)

:: ── Lanzar la aplicación ────────────────────────────────────────────────────
echo   [*] Iniciando ViajaIA...
echo.
cd /d "%SCRIPT_DIR%"
"%VENV_DIR%\Scripts\python.exe" src\main.py %*

:: Si la app cierra con error, mantener la ventana abierta
if errorlevel 1 (
    echo.
    echo   [ERROR] La aplicacion cerro con un error ^(codigo: %errorlevel%^).
    echo   Revisa el mensaje de error arriba.
    echo.
    pause
)
endlocal
