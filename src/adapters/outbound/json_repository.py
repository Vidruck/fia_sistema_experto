"""
MÓDULO: src/adapters/outbound/json_repository.py
PROPÓSITO:
    Implementa el puerto de salida `DestinationRepository` (Outbound Adapter).
    Este adaptador lee un archivo físico JSON (`destinations.json`) que actúa como nuestra
    base de conocimiento persistente.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Al heredar de `DestinationRepository`, estamos obligados a implementar
      `obtener_todos_los_destinos` y `obtener_reglas_de_inferencia`.
    - En un sistema real de bajos recursos, leer un archivo JSON es sumamente veloz y no consume
      memoria de servidores de bases de datos adicionales (como PostgreSQL o MySQL).
    - Manejamos los posibles errores de lectura (archivo inexistente o mal formado) traduciéndolos
      a excepciones del dominio para no contaminar las capas superiores con detalles de I/O.
"""

import json
import os
from typing import List, Dict, Any
from src.ports.outbound import DestinationRepository
from src.domain.models import Destination
from src.domain.exceptions import IncompleteKnowledgeBaseError

class JSONDestinationRepository(DestinationRepository):
    """
    Adaptador concreto para leer la base de conocimiento desde un archivo plano JSON.
    """

    def __init__(self, file_path: str):
        """
        Inicializa el adaptador con la ruta al archivo JSON.
        
        :param file_path: Ruta absoluta o relativa al archivo JSON.
        """
        self._file_path = file_path

    def _cargar_datos(self) -> Dict[str, Any]:
        """
        Método interno para leer y parsear el archivo JSON.
        """
        if not os.path.exists(self._file_path):
            raise IncompleteKnowledgeBaseError(
                f"No se encontró el archivo de base de conocimiento en: {self._file_path}"
            )
        
        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as err:
            raise IncompleteKnowledgeBaseError(
                f"El archivo JSON de base de conocimiento está mal formado: {err}"
            )
        except Exception as err:
            raise IncompleteKnowledgeBaseError(
                f"Error inesperado al leer la base de conocimiento: {err}"
            )

    def obtener_todos_los_destinos(self) -> List[Destination]:
        """
        Lee el archivo JSON, mapea cada entrada a la entidad 'Destination' del Dominio
        y las devuelve como lista.
        """
        datos = self._cargar_datos()
        destinos_raw = datos.get("destinations", [])
        
        destinos = []
        for dest in destinos_raw:
            try:
                destinos.append(
                    Destination(
                        id=str(dest["id"]),
                        name=dest["name"],
                        description=dest["description"],
                        budget=dest["budget"],
                        tags=dest.get("tags", [])
                    )
                )
            except KeyError as err:
                raise IncompleteKnowledgeBaseError(
                    f"Falta el campo obligatorio '{err.args[0]}' en el destino de ID {dest.get('id', 'desconocido')}"
                )
                
        return destinos

    def obtener_reglas_de_inferencia(self) -> List[Dict[str, Any]]:
        """
        Lee el archivo JSON y extrae la lista de reglas de inferencia.
        """
        datos = self._cargar_datos()
        return datos.get("rules", [])
