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

import sys
from PyQt6.QtWidgets import QApplication
from src.ports.inbound import RecommendationUseCase
from src.adapters.inbound.pyqt_app.main_window import MainWindow

def iniciar_gui(use_case: RecommendationUseCase):
    """
    Función que inicia la aplicación gráfica de PyQt6.
    
    :param use_case: Implementación del caso de uso RecommendationUseCase (Inyección de dependencias).
    """
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
