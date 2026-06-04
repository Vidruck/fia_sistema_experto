"""
MÓDULO: tests/test_rules_engine.py
PROPÓSITO:
    Contiene las pruebas unitarias para validar el motor de inferencia `VacationExpertSystem`.
    Esto nos permite asegurar que las reglas lógicas funcionen de manera correcta y consistente
    independientemente de la interfaz gráfica o de los datos guardados en el disco.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Usamos `pytest` como framework de pruebas.
    - Creamos datos ficticios (fakes/fixtures) controlados para probar exclusivamente la lógica de inferencia.
    - Las pruebas demuestran cómo la arquitectura hexagonal aísla el núcleo de negocio para que sea
      100% testeable en milisegundos.
"""

import pytest
from src.domain.models import Mood, TimeDuration, Destination
from src.domain.rules_engine import VacationExpertSystem

@pytest.fixture
def base_de_conocimiento_test():
    """Fixture que provee una lista de destinos y reglas de prueba controladas."""
    destinos = [
        Destination(
            id="1",
            name="Cabaña de Montaña",
            description="Lugar frío y pacífico.",
            budget="Bajo",
            tags=["bosque", "tranquilidad", "relajacion"]
        ),
        Destination(
            id="2",
            name="Playa Tropical",
            description="Calor, playa y sol.",
            budget="Medio",
            tags=["playa", "sol", "relajacion"]
        ),
        Destination(
            id="3",
            name="Escalada en los Alpes",
            description="Aventura extrema en hielo y roca.",
            budget="Alto",
            tags=["aventura", "montaña", "naturaleza"]
        )
    ]

    reglas = [
        {
            "id": "rule_estresado_corto",
            "description": "Si está estresado y tiene fin de semana, buscar bosque y tranquilidad.",
            "conditions": {
                "mood": "estresado",
                "duration": "fin_de_semana"
            },
            "consequences": {
                "recommended_tags": ["bosque", "tranquilidad"],
                "weight_modifier": 2.0
            }
        },
        {
            "id": "rule_aventura_larga",
            "description": "Si busca aventura y tiene más de una semana, buscar montaña y aventura.",
            "conditions": {
                "mood": "aventurero",
                "duration": "mas_de_una_semana"
            },
            "consequences": {
                "recommended_tags": ["aventura", "montaña"],
                "weight_modifier": 3.0
            }
        }
    ]

    return destinos, reglas


def test_inferencia_estresado_corto(base_de_conocimiento_test):
    """Verifica que un usuario estresado con tiempo corto reciba la cabaña de montaña."""
    destinos, reglas = base_de_conocimiento_test
    motor = VacationExpertSystem(destinations=destinos, rules=reglas)

    # Ejecutar inferencia
    recomendaciones = motor.infer(Mood.ESTRESADO, TimeDuration.FIN_DE_SEMANA)

    assert len(recomendaciones) > 0
    # El primer resultado (el de mayor puntuación) debe ser la Cabaña de Montaña
    top_recommendation = recomendaciones[0]
    assert top_recommendation.destination.id == "1"
    assert "bosque" in top_recommendation.matched_tags
    assert "tranquilidad" in top_recommendation.matched_tags


def test_inferencia_aventurero_largo(base_de_conocimiento_test):
    """Verifica que un aventurero con mucho tiempo sea recomendado a escalar en los Alpes."""
    destinos, reglas = base_de_conocimiento_test
    motor = VacationExpertSystem(destinations=destinos, rules=reglas)

    recomendaciones = motor.infer(Mood.AVENTURERO, TimeDuration.MAS_DE_UNA_SEMANA)

    assert len(recomendaciones) > 0
    top_recommendation = recomendaciones[0]
    assert top_recommendation.destination.id == "3"
    assert "montaña" in top_recommendation.matched_tags
    assert top_recommendation.score >= 3.0


def test_inferencia_sin_reglas_coincidentes(base_de_conocimiento_test):
    """Verifica que si no hay reglas coincidentes, funcione el fallback básico de tags."""
    destinos, reglas = base_de_conocimiento_test
    motor = VacationExpertSystem(destinations=destinos, rules=reglas)

    # Una combinación para la cual no definimos reglas
    # El motor debería buscar destinos con la etiqueta "relajacion" (directamente del mood del usuario)
    recomendaciones = motor.infer(Mood.RELAJADO, TimeDuration.FIN_DE_SEMANA)

    assert len(recomendaciones) > 0
    # Tanto la cabaña (1) como la playa (2) tienen la etiqueta "relajacion"
    ids_recomendados = [r.destination.id for r in recomendaciones]
    assert "1" in ids_recomendados
    assert "2" in ids_recomendados
