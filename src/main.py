"""
MÓDULO: src/main.py
PROPÓSITO:
    Punto de entrada principal de la aplicación (Composition Root o Raíz de Composición).
    Aquí se realiza el ensamblado de todas las piezas de la Arquitectura Hexagonal:
    1. Se lee la configuración global (ruta del archivo JSON).
    2. Se instancia el adaptador de salida (`JSONDestinationRepository`).
    3. Se inyecta el repositorio en el caso de uso (`VacationRecommendationService`).
    4. Se decide qué adaptador de entrada arrancar (GUI PyQt6 o Consola CLI) basado en los argumentos.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Raíz de Composición: Es un concepto clave. Las capas internas (Dominio y Puertos) no
      saben cómo se crean las dependencias. Solo esta clase `main.py` tiene la responsabilidad de
      instanciar y "conectar" los cables de la arquitectura.
    - Robustez: Si el usuario ejecuta la aplicación dentro de Docker (donde no suele haber un entorno gráfico X11),
      el programa detectará la falta de PyQt6 de forma amigable e iniciará automáticamente la CLI de terminal
      para que la aplicación nunca se rompa.
"""

import argparse
import os
import sys

# Agregar la raíz del proyecto al sys.path para que los imports de 'src.*' funcionen
# tanto con 'python src/main.py' como con 'python -m src.main'
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.adapters.outbound.json_repository import JSONDestinationRepository
from src.config import KNOWLEDGE_BASE_PATH
from src.domain.services import VacationRecommendationService


def main():
    # 1. Parsear los argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="Sistema Experto Hexagonal de Recomendación de Vacaciones."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cli",
        action="store_true",
        help="Iniciar la aplicación directamente en la terminal (línea de comandos).",
    )
    group.add_argument(
        "--gui",
        action="store_true",
        help="Iniciar la aplicación con la interfaz gráfica nativa (PyQt6).",
    )
    args = parser.parse_args()

    # 2. Inicializar los adaptadores de salida y servicios (Inyección de Dependencias)
    # Creamos el adaptador de persistencia JSON
    repositorio = JSONDestinationRepository(KNOWLEDGE_BASE_PATH)

    # Inyectamos el adaptador de salida en el puerto de entrada (caso de uso)
    servicio = VacationRecommendationService(repositorio)

    # 3. Decidir el modo de ejecución (GUI por defecto, CLI de respaldo)
    modo_cli = args.cli

    if not modo_cli:
        try:
            # Intentamos importar y ejecutar la interfaz gráfica PyQt6
            print("[INFO] Intentando iniciar la interfaz gráfica PyQt6...")
            from src.adapters.inbound.pyqt_app.app import iniciar_gui

            iniciar_gui(servicio)
        except (ImportError, Exception) as err:
            # Si falla la carga de PyQt6 (por ejemplo, en un contenedor Docker sin entorno visual),
            # avisamos al usuario y degradamos la ejecución elegantemente al modo consola (CLI).
            print(
                f"\n[ADVERTENCIA] No se pudo cargar la interfaz gráfica (Falta PyQt6 o no hay pantalla activa)."
            )
            print(f"Detalle del error: {err}")
            print("[INFO] Cambiando automáticamente al modo de consola (CLI)...")
            modo_cli = True

    # Ejecución en modo CLI (Consola)
    if modo_cli:
        from src.adapters.inbound.cli import CLIAdapter

        adaptador_cli = CLIAdapter(servicio)
        adaptador_cli.iniciar()


if __name__ == "__main__":
    main()
