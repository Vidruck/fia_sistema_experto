"""
MÓDULO: src/domain/services.py
PROPÓSITO:
    Implementa el puerto de entrada `RecommendationUseCase`. Esta clase actúa como un Servicio
    de Aplicación que coordina las acciones necesarias para cumplir con el caso de uso
    "Obtener recomendación de vacaciones".
    
DOCENCIA (Para el equipo de desarrollo universitario):
    - Inyección de Dependencias: Esta clase no crea su propio repositorio (`JSONDestinationRepository`).
      En su lugar, recibe una interfaz `DestinationRepository` en el constructor. Esto nos permite
      cambiar el origen de datos (por ejemplo, para pruebas automatizadas con datos falsos/mocks)
      sin modificar una sola línea de código de esta clase.
    - Orquestación: El caso de uso se encarga de:
        1. Recibir los datos de la interfaz de usuario estructurados en un diccionario dinámico de hechos.
        2. Validar los campos críticos usando los Tipos de Datos del Dominio (Enums `Mood` y `TimeDuration`).
        3. Solicitar datos al adaptador de salida (a través de la abstracción del repositorio).
        4. Instanciar el motor de inferencia y ejecutar la lógica de reglas.
        5. Devolver las recomendaciones limpias para su visualización.
"""

from typing import List, Dict, Any
from src.ports.inbound import RecommendationUseCase
from src.ports.outbound import DestinationRepository
from src.domain.models import Mood, TimeDuration, Recommendation
from src.domain.rules_engine import VacationExpertSystem
from src.domain.exceptions import DomainError

class VacationRecommendationService(RecommendationUseCase):
    """
    Servicio que implementa y resuelve el caso de uso de recomendación.
    Conecta el puerto de entrada con el motor del dominio y el puerto de salida.
    """

    def __init__(self, repository: DestinationRepository):
        """
        Constructor que recibe la abstracción del repositorio por inyección de dependencias.
        
        :param repository: Objeto que implementa DestinationRepository.
        """
        self._repository = repository

    def obtener_recomendacion(self, user_facts: Dict[str, Any]) -> List[Recommendation]:
        """
        Implementa la lógica del caso de uso procesando múltiples variables dinámicas.
        """
        # 1. Validación de entradas críticas (si existen en los hechos) usando objetos ricos del dominio
        try:
            if "mood" in user_facts and user_facts["mood"]:
                Mood.from_str(user_facts["mood"])
            if "duration" in user_facts and user_facts["duration"]:
                TimeDuration.from_str(user_facts["duration"])
        except ValueError as err:
            # Re-lanzamos como error de dominio para ser capturado adecuadamente
            raise DomainError(f"Error de validación en los datos ingresados: {str(err)}")

        # 2. Obtención de datos e inicialización del motor de inferencia
        # Nota: Cargamos las reglas y destinos en cada petición para que, si el archivo JSON cambia,
        # los resultados se actualicen dinámicamente sin necesidad de reiniciar la aplicación.
        destinos = self._repository.obtener_todos_los_destinos()
        reglas = self._repository.obtener_reglas_de_inferencia()

        # 3. Ejecución del motor de inferencia (dominio puro)
        motor = VacationExpertSystem(destinations=destinos, rules=reglas)
        recomendaciones = motor.infer(user_facts=user_facts)

        return recomendaciones