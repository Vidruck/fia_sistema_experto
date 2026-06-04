"""
MÓDULO: src/domain/models.py
PROPÓSITO:
    Este archivo define los modelos de datos del Dominio (el núcleo de la Arquitectura Hexagonal).
    Como estamos usando Arquitectura Hexagonal (o limpia), este archivo está libre de dependencias
    externas (como frameworks de base de datos o interfaces de usuario). Esto asegura que las reglas
    y objetos del negocio sean portables y fáciles de probar.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Usamos `Enum` para restringir los valores válidos y evitar errores de dedo (ej. "estresado" vs "estresada").
    - Usamos `@dataclass` porque provee de manera automática constructores y métodos de comparación limpios.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

class Mood(Enum):
    """
    Representa el estado de ánimo actual del usuario.
    Esta enumeración limita las opciones para el análisis del sistema experto.
    """
    ESTRESADO = "estresado"
    AVENTURERO = "aventurero"
    RELAJADO = "relajado"
    ABURRIDO = "aburrido"
    CANSADO = "cansado"

    @classmethod
    def from_str(cls, value: str) -> "Mood":
        """Convierte una cadena de texto a su correspondiente valor de Enum."""
        try:
            return cls(value.lower().strip())
        except ValueError:
            raise ValueError(f"'{value}' no es un estado de ánimo válido. Opciones: {[e.value for e in cls]}")


class TimeDuration(Enum):
    """
    Representa la cantidad de tiempo de vacaciones del que dispone el usuario.
    """
    FIN_DE_SEMANA = "fin_de_semana"
    UNA_SEMANA = "una_semana"
    MAS_DE_UNA_SEMANA = "mas_de_una_semana"

    @classmethod
    def from_str(cls, value: str) -> "TimeDuration":
        """Convierte una cadena de texto a su correspondiente valor de Enum."""
        # Reemplazamos espacios por guiones bajos para que coincida con el enum
        normalized = value.lower().strip().replace(" ", "_")
        try:
            return cls(normalized)
        except ValueError:
            raise ValueError(f"'{value}' no es una duración válida. Opciones: {[e.value for e in cls]}")


@dataclass(frozen=True)
class Destination:
    """
    Representa un destino turístico de la base de conocimiento.
    Es un 'Value Object' en el contexto de Domain-Driven Design (DDD) debido a que es inmutable.
    """
    id: str
    name: str
    description: str
    budget: str
    tags: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """
    Representa el resultado final que genera el Sistema Experto.
    Contiene el destino sugerido y una puntuación (o score de coincidencia) que justifica
    por qué este destino fue seleccionado por el motor de inferencia.
    """
    destination: Destination
    score: float
    matched_tags: List[str] = field(default_factory=list)
    explanation: str = ""
