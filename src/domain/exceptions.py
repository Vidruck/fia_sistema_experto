"""
MÓDULO: src/domain/exceptions.py
PROPÓSITO:
    Define las excepciones específicas del dominio. En arquitectura hexagonal, es importante
    que el dominio no lance excepciones de bibliotecas de base de datos u otras tecnologías,
    sino sus propios errores que luego los adaptadores de entrada pueden interceptar para mostrarlos
    amigablemente en consola o interfaz gráfica.
"""

class DomainError(Exception):
    """Excepción base para todos los errores de lógica de negocio del sistema experto."""
    pass


class DestinationNotFoundError(DomainError):
    """Se lanza cuando un destino solicitado no existe en el sistema."""
    pass


class IncompleteKnowledgeBaseError(DomainError):
    """Se lanza cuando el motor de inferencia no puede cargar las reglas o los datos obligatorios."""
    pass


class InferenceError(DomainError):
    """Ocurre cuando el motor de inferencia detecta inconsistencias críticas al procesar hechos."""
    pass
