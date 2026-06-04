"""
MÓDULO: tests/test_json_repository.py
PROPÓSITO:
    Prueba el adaptador de salida `JSONDestinationRepository`.
    Verifica que el repositorio pueda leer un archivo JSON simulado, mapear correctamente
    los campos a entidades de dominio `Destination`, e identificar errores de formato.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Usamos el módulo estándar `tempfile` para crear archivos JSON temporales. Esto
      evita ensuciar la base de datos real o depender de que exista el archivo destinations.json original.
    - Probamos el "camino feliz" (archivo válido) y el "camino de error" (archivos vacíos o mal formados).
"""

import os
import tempfile
import pytest
from src.adapters.outbound.json_repository import JSONDestinationRepository
from src.domain.exceptions import IncompleteKnowledgeBaseError

def test_cargar_destinos_validos():
    """Prueba que el adaptador lea y parsee un JSON estructurado correctamente."""
    contenido_valido = """
    {
      "destinations": [
        {
          "id": "100",
          "name": "Playa de Prueba",
          "description": "Una descripción corta.",
          "budget": "Bajo",
          "tags": ["test", "playa"]
        }
      ],
      "rules": [
        {
          "id": "rule_test",
          "conditions": {"mood": "estresado"},
          "consequences": {"recommended_tags": ["playa"]}
        }
      ]
    }
    """
    
    # Creamos un archivo temporal con el contenido válido
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json", encoding="utf-8") as temp_file:
        temp_file.write(contenido_valido)
        temp_path = temp_file.name

    try:
        repositorio = JSONDestinationRepository(temp_path)
        
        destinos = repositorio.obtener_todos_los_destinos()
        assert len(destinos) == 1
        assert destinos[0].id == "100"
        assert destinos[0].name == "Playa de Prueba"
        assert destinos[0].budget == "Bajo"
        assert "test" in destinos[0].tags

        reglas = repositorio.obtener_reglas_de_inferencia()
        assert len(reglas) == 1
        assert reglas[0]["id"] == "rule_test"
    finally:
        # Limpieza: borrar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_error_archivo_inexistente():
    """Prueba que se lance IncompleteKnowledgeBaseError al buscar un archivo que no existe."""
    repositorio = JSONDestinationRepository("ruta/no/existente/archivo.json")
    
    with pytest.raises(IncompleteKnowledgeBaseError) as exc_info:
        repositorio.obtener_todos_los_destinos()
    
    assert "No se encontró el archivo" in str(exc_info.value)


def test_error_json_mal_formado():
    """Prueba que se lance IncompleteKnowledgeBaseError si el JSON tiene un error de sintaxis."""
    contenido_corrupto = "{ 'destinations': [ sin_comillas ]"
    
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json", encoding="utf-8") as temp_file:
        temp_file.write(contenido_corrupto)
        temp_path = temp_file.name

    try:
        repositorio = JSONDestinationRepository(temp_path)
        with pytest.raises(IncompleteKnowledgeBaseError) as exc_info:
            repositorio.obtener_todos_los_destinos()
        assert "mal formado" in str(exc_info.value)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
