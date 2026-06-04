"""
MÓDULO: src/adapters/inbound/cli.py
PROPÓSITO:
    Implementa un adaptador de entrada (Inbound Adapter) por consola de comandos (CLI).
    Permite al equipo de desarrollo y a los usuarios interactuar con el sistema experto
    de forma ágil directamente en su terminal, ideal para pruebas rápidas dentro del contenedor Docker.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Este adaptador se conecta únicamente con la interfaz `RecommendationUseCase`.
    - No sabe nada acerca del archivo JSON, ni del motor de inferencia interno.
    - Se limita a capturar las entradas de teclado del usuario, llamar al puerto y dar formato a la salida.
"""

import sys
from src.ports.inbound import RecommendationUseCase
from src.domain.models import Mood, TimeDuration
from src.domain.exceptions import DomainError

class CLIAdapter:
    """
    Adaptador de entrada por consola para interactuar con el caso de uso del sistema experto.
    """

    def __init__(self, use_case: RecommendationUseCase):
        """
        Recibe el caso de uso a través del puerto de entrada (abstracción).
        
        :param use_case: Implementación de RecommendationUseCase.
        """
        self._use_case = use_case

    def _mostrar_menu_moods(self) -> str:
        """Muestra las opciones de estado de ánimo y solicita la selección."""
        moods = [e.value for e in Mood]
        print("\n=== ¿CÓMO TE SIENTES HOY? ===")
        for idx, mood in enumerate(moods, 1):
            print(f" {idx}. {mood.capitalize()}")
        
        while True:
            try:
                opcion = input("Selecciona un número: ").strip()
                idx = int(opcion) - 1
                if 0 <= idx < len(moods):
                    return moods[idx]
                print(f"Por favor, introduce un número entre 1 y {len(moods)}.")
            except ValueError:
                print("Entrada inválida. Escribe un número válido.")

    def _mostrar_menu_durations(self) -> str:
        """Muestra las opciones de tiempo disponible y solicita la selección."""
        durations = [e.value for e in TimeDuration]
        print("\n=== ¿CUÁNTO TIEMPO TIENES DISPONIBLE? ===")
        for idx, duration in enumerate(durations, 1):
            # Cambiamos guiones bajos por espacios para mostrarlo amigablemente
            label = duration.replace("_", " ").capitalize()
            print(f" {idx}. {label}")
        
        while True:
            try:
                opcion = input("Selecciona un número: ").strip()
                idx = int(opcion) - 1
                if 0 <= idx < len(durations):
                    return durations[idx]
                print(f"Por favor, introduce un número entre 1 y {len(durations)}.")
            except ValueError:
                print("Entrada inválida. Escribe un número válido.")

    def iniciar(self):
        """Arranca el bucle interactivo de la consola."""
        print("====================================================")
        print("  SISTEMA EXPERTO DE RECOMENDACIÓN DE VACACIONES    ")
        print("    (Arquitectura Hexagonal - Prototipo Inicial)    ")
        print("====================================================")

        while True:
            mood_seleccionado = self._mostrar_menu_moods()
            duracion_seleccionada = self._mostrar_menu_durations()

            print("\nProcesando hechos en el motor de inferencia...")
            
            try:
                # Invocamos el caso de uso a través de la abstracción
                recomendaciones = self._use_case.obtener_recomendacion(
                    mood_str=mood_seleccionado,
                    duration_str=duracion_seleccionada
                )

                if not recomendaciones:
                    print("\n[!] El sistema experto no encontró ningún destino que coincida con tus criterios.")
                else:
                    print("\n====================================================")
                    print(f"  RESULTADOS: {len(recomendaciones)} DESTINOS RECOMENDADOS")
                    print("====================================================")
                    
                    for idx, rec in enumerate(recomendaciones, 1):
                        dest = rec.destination
                        print(f"\n{idx}. ★ {dest.name} ★ (Puntuación de Coincidencia: {rec.score})")
                        print(f"   Descripción: {dest.description}")
                        print(f"   Presupuesto: {dest.budget}")
                        print(f"   Etiquetas coincidentes: {rec.matched_tags}")
                        print(f"   Justificación: {rec.explanation}")
                        print("-" * 50)

            except DomainError as err:
                print(f"\n[ERROR DE NEGOCIO] {err}")
            except Exception as err:
                print(f"\n[ERROR CRÍTICO] Ocurrió un error inesperado: {err}")

            # Preguntar si desea continuar
            print()
            respuesta = input("¿Deseas realizar otra consulta? (s/n): ").strip().lower()
            if respuesta != 's':
                print("\n¡Gracias por usar el sistema experto! Que tengas buenas vacaciones.")
                break
