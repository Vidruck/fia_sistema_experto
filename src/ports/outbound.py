"""
MÓDULO: src/ports/outbound.py
PROPÓSITO:
    Define los puertos de salida (Driven Ports).
    En Arquitectura Hexagonal, un puerto de salida es una interfaz que define lo que el núcleo de
    la aplicación (el dominio) necesita del mundo exterior, como acceder a una base de datos,
    cargar un archivo local o comunicarse con un servicio web externo.

DOCENCIA (Para el equipo de desarrollo universitario):
    - El Dominio es el "dueño" del puerto. El dominio define *qué* datos necesita,
      y los adaptadores de salida (como `json_repository.py`) definen *cómo* se obtienen técnicamente.
    - Al usar esta abstracción, el motor de inferencia de nuestro sistema experto no se entera
      si las reglas vienen de un archivo JSON, de SQLite, o de un servicio en la nube (AWS/GCP).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.models import Destination

class DestinationRepository(ABC):
    """
    Puerto de Salida que define cómo acceder a la base de conocimiento del sistema experto.
    """

    @abstractmethod
    def obtener_todos_los_destinos(self) -> List[Destination]:
        """
        Carga y devuelve todos los destinos disponibles en la base de conocimiento.
        
        :return: Lista de objetos Destination.
        """
        pass

    @abstractmethod
    def obtener_reglas_de_inferencia(self) -> List[Dict[str, Any]]:
        """
        Carga y devuelve las reglas de producción para el motor de inferencia.
        
        :return: Lista de diccionarios que describen las reglas.
        """
        pass
