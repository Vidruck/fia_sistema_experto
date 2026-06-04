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
        1. Recibir los datos de la interfaz de usuario en texto plano.
        2. Validar y convertirlos a Tipos de Datos del Dominio (Enums `Mood` y `TimeDuration`).
        3. Solicitar datos al adaptador de salida (a través de la abstracción del repositorio).
        4. Instanciar el motor de inferencia y ejecutar la lógica de reglas.
        5. Devolver las recomendaciones limpias para su visualización.
"""

from typing import List
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

    def obtener_recomendacion(self, mood_str: str, duration_str: str) -> List[Recommendation]:
        """
        Implementa la lógica del caso de uso.
        """
        # 1. Validación y transformación de las entradas del usuario a objetos ricos del dominio
        try:
            mood = Mood.from_str(mood_str)
            duration = TimeDuration.from_str(duration_str)
        except ValueError as err:
            # Re-lanzamos como error de dominio para ser capturado adecuadamente
            raise DomainError(str(err))

        # 2. Obtención de datos e inicialización del motor de inferencia
        # Nota: Cargamos las reglas y destinos en cada petición para que, si el archivo JSON cambia,
        # los resultados se actualicen dinámicamente sin necesidad de reiniciar la aplicación.
        destinos = self._repository.obtener_todos_los_destinos()
        reglas = self._repository.obtener_reglas_de_inferencia()

        # 3. Ejecución del motor de inferencia (dominio puro)
        motor = VacationExpertSystem(destinations=destinos, rules=reglas)
        recomendaciones = motor.infer(mood=mood, duration=duration)

        return recomendaciones
