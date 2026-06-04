"""
MÓDULO: src/config.py
PROPÓSITO:
    Define constantes y configuraciones globales de la aplicación.
    De esta forma evitamos rutas en duro (hardcoded) dispersas por el código.
"""

import os

# Obtiene la ruta al directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta al archivo JSON de la base de conocimiento
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "data", "destinations.json")
