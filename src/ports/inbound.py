"""
MÓDULO: src/ports/inbound.py
PROPÓSITO:
    Define los puertos de entrada (Driving Ports). 
    En Arquitectura Hexagonal, un puerto de entrada es una interfaz que define la API del negocio,
    es decir, las operaciones que los adaptadores externos (como la interfaz PyQt o la CLI) 
    pueden solicitarle al núcleo de la aplicación (el dominio).

    - Usamos la clase `ABC` (Abstract Base Class) de Python para crear interfaces puras.
    - El decorador `@abstractmethod` obliga a las subclases a implementar dicho método.
    - Esto desacopla totalmente los controladores visuales del flujo de negocio. Si mañana cambiamos
      PyQt por Flutter o una API Web (FastAPI), este puerto no cambia en absoluto.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.models import Recommendation

class RecommendationUseCase(ABC):
    """
    Caso de Uso (Puerto de Entrada) para obtener recomendaciones de vacaciones.
    Las interfaces de usuario interactúan con esta abstracción, sin saber cómo se calculan
    internamente ni de dónde se obtienen los datos.
    """

    @abstractmethod
    def obtener_recomendacion(self, user_facts: Dict[str, Any]) -> List[Recommendation]:
        """
        Solicita una lista de destinos recomendados en base a un diccionario dinámico
        de hechos (preferencias) enviados por el usuario desde cualquier interfaz de usuario.
        
        :param user_facts: Diccionario con las selecciones del usuario (ej. presupuesto, clima).
        :return: Lista de objetos Recommendation ordenados por afinidad.
        """
        pass