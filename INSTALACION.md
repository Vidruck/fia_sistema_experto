# 🚀 Guía de Instalación y Ejecución — ViajaIA

> Sistema Experto de Recomendación de Vacaciones  
> Para presentaciones en equipos de escritorio reales

---

## ⚡ Inicio Rápido

### 🐧 Linux (Ubuntu, Fedora, Arch...)

```bash
# 1. Dar permisos de ejecución (solo la primera vez)
chmod +x ejecutar_linux.sh

# 2. Ejecutar
./ejecutar_linux.sh
```

### 🪟 Windows 11

**Opción A — PowerShell (recomendado, con colores y mejor UI):**
```powershell
# Click derecho en ejecutar_windows.ps1 → "Ejecutar con PowerShell"
# O desde una terminal PowerShell:
powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1
```

**Opción B — Doble clic (más sencillo):**
- Doble clic en `ejecutar_windows.bat`

---

## 📋 Requisitos del Sistema

| Plataforma | Requisito | Versión mínima |
|-----------|-----------|---------------|
| Ambas | Python | 3.10+ (recomendado 3.11) |
| Windows | — | Windows 10/11 |
| Linux | Display server | X11 o Wayland |

### Descargar Python
- **Windows/Mac**: https://python.org/downloads  
  ⚠️ En el instalador, marcar **"Add Python to PATH"**
- **Ubuntu/Debian**: `sudo apt install python3 python3-pip python3-venv`
- **Fedora**: `sudo dnf install python3 python3-pip`

---

## 🔄 Cómo funciona el lanzador

Los scripts hacen todo automáticamente:

```
1ª ejecución:                    2ª ejecución en adelante:
┌──────────────────┐             ┌──────────────────┐
│ Verifica Python  │             │ Verifica Python  │
│ Instala librerías│             │ Detecta venv     │
│ del sistema      │             │ existente        │
│ Crea venv        │     →       │ Verifica PyQt6   │
│ Instala PyQt6    │             │ Lanza la app     │
│ Lanza la app     │             └──────────────────┘
└──────────────────┘             (segundos)
```

---

## 🛠️ Solución de Problemas Comunes

### Linux: `No module named 'PyQt6'`
```bash
# Reinstalar desde cero:
./ejecutar_linux.sh --reinstalar
```

### Linux: Error de display / pantalla negra
```bash
# Instalar librerías gráficas:
sudo apt install libxcb-xinerama0 libgl1-mesa-glx libxkbcommon-x11-0

# Si usas Wayland, forzar X11:
QT_QPA_PLATFORM=xcb ./ejecutar_linux.sh
```

### Windows: "La ejecución de scripts está deshabilitada"
```powershell
# Ejecutar con bypass de política:
powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1
```

### Windows: Python no reconocido
- Asegúrate de haber marcado **"Add Python to PATH"** en la instalación
- Reinicia la terminal/cmd después de instalar Python
- Si usas `py` en lugar de `python`, el script lo detecta automáticamente

### Cualquier plataforma: Reinstalar dependencias desde cero
```bash
# Linux:
./ejecutar_linux.sh --reinstalar

# Windows PowerShell:
powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1 -Reinstalar

# Windows CMD:
ejecutar_windows.bat --reinstalar
```

---

## 📁 Estructura de archivos generados

```
Sistema_Experto/
├── ejecutar_linux.sh        ← Script Linux (bash)
├── ejecutar_windows.bat     ← Script Windows (CMD)
├── ejecutar_windows.ps1     ← Script Windows (PowerShell)
├── .venv_viajaia/           ← Entorno virtual (creado automáticamente)
│   └── ...                  ← NO subir a git
└── ...
```

> ✅ El directorio `.venv_viajaia/` está excluido en `.gitignore`

---

## 🏗️ Crear Ejecutable Standalone (avanzado)

Si quieres un `.exe` (Windows) o binario (Linux) que **no requiera Python**:

```bash
# 1. Instalar PyInstaller en el venv
# Linux:
.venv_viajaia/bin/pip install pyinstaller

# Windows:
.venv_viajaia\Scripts\pip install pyinstaller

# 2. Construir el ejecutable (ejecutar en cada plataforma)
# Linux:
.venv_viajaia/bin/pyinstaller --onefile --windowed \
    --name "ViajaIA" \
    --add-data "data:data" \
    src/main.py

# Windows (PowerShell):
.venv_viajaia\Scripts\pyinstaller --onefile --windowed `
    --name "ViajaIA" `
    --add-data "data;data" `
    src\main.py

# 3. El ejecutable estará en:  dist/ViajaIA  (Linux)
#                              dist\ViajaIA.exe  (Windows)
```

> ⚠️ PyInstaller debe ejecutarse **en la misma plataforma** donde se usará el ejecutable.  
> El `.exe` generado en Windows **no** funciona en Linux y viceversa.
