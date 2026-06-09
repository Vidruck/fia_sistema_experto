"""
MÓDULO: src/adapters/inbound/pyqt_app/app.py
PROPÓSITO:
    Provee el punto de entrada para iniciar la interfaz gráfica de usuario (GUI).
    Inicializa el bucle de eventos de QApplication y enlaza el caso de uso inyectado
    a la ventana principal.
    - Este módulo es el pegamento final para la versión GUI.
    - Se encarga de instanciar `QApplication` (necesario en toda app PyQt) y mostrar
      la ventana `MainWindow` de forma no bloqueante.
"""

import os
import sys

from PyQt6.QtWidgets import QApplication
from src.ports.inbound import RecommendationUseCase
from src.adapters.inbound.pyqt_app.main_window import MainWindow


def _configurar_plataforma_qt() -> None:
    """
    Configura la variable QT_QPA_PLATFORM si no fue establecida externamente
    (por ejemplo, si el usuario lanza 'python src/main.py' directamente sin el script).

    Estrategia:
      - Sesión Wayland → preferir 'wayland'; si falla al iniciar, Qt usa xcb (XWayland) de forma automática.
      - Sesión X11     → dejar que Qt resuelva solo (xcb por defecto).
    """
    if "QT_QPA_PLATFORM" in os.environ:
        # El script de lanzamiento ya lo configuró; no sobreescribir
        return

    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

    if session_type == "wayland" or wayland_display:
        # Intentamos Wayland nativo; Qt hará fallback automático a xcb si el plugin no existe
        os.environ.setdefault("QT_QPA_PLATFORM", "wayland")
        # Desactivar decoraciones propias de Qt en compositors Wayland (GNOME, KDE, Sway...)
        os.environ.setdefault("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
    # else: X11 → Qt usa xcb por defecto, sin configuración extra necesaria

    # Habilitar escalado HiDPI automático
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")


def iniciar_gui(use_case: RecommendationUseCase):
    """
    Función que inicia la aplicación gráfica de PyQt6.

    :param use_case: Implementación del caso de uso RecommendationUseCase (Inyección de dependencias).
    """
    # 0. Configurar plataforma Qt antes de instanciar QApplication
    _configurar_plataforma_qt()

    # 1. Crear el objeto de la aplicación de Qt
    app = QApplication(sys.argv)

    # Configuramos una fuente predeterminada moderna
    app.setFont(QApplication.font())

    # 2. Instanciar la ventana principal pasándole el caso de uso
    window = MainWindow(use_case)

    # 3. Mostrar la ventana al usuario
    window.show()

    # 4. Iniciar el bucle de eventos y retornar su estado de salida al sistema operativo
    sys.exit(app.exec())
