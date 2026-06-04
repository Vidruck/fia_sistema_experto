"""
MÓDULO: src/domain/rules_engine.py
PROPÓSITO:
    Este módulo contiene el Motor de Inferencia del Sistema Experto.
    Utiliza una estrategia de "Encadenamiento hacia adelante" (Forward Chaining) simplificada:
    1. Toma los hechos conocidos (estado de ánimo y tiempo disponible del usuario).
    2. Busca en la base de conocimiento cuáles reglas de producción "se activan" (es decir, sus condiciones se cumplen).
    3. Acumula las consecuencias de las reglas activadas (etiquetas de destino recomendadas y sus pesos).
    4. Evalúa cada destino disponible, calculando un "puntaje de coincidencia" (score) basado en la concurrencia de etiquetas.
    5. Devuelve los destinos ordenados de mayor a menor relevancia.

DOCENCIA (Para el equipo de desarrollo universitario):
    - Regla de Producción: Es una estructura lógica "SI <condiciones> ENTONCES <consecuencias>".
    - Hecho (Fact): Información conocida y verdadera sobre el estado actual (ej: Estado de Ánimo = Aventurero).
    - Explicabilidad: Un buen sistema experto no solo da una respuesta, sino que "justifica" sus decisiones.
      Aquí generamos una explicación legible detallando qué reglas se activaron para recomendar cada destino.
"""

from typing import List, Dict, Any
from src.domain.models import Mood, TimeDuration, Destination, Recommendation
from src.domain.exceptions import InferenceError

class VacationExpertSystem:
    """
    Motor de inferencia para el sistema experto de selección de vacaciones.
    Diseñado para ser ligero, eficiente y sumamente legible.
    """

    def __init__(self, destinations: List[Destination], rules: List[Dict[str, Any]]):
        """
        Inicializa el motor de inferencia con la base de conocimiento.
        
        :param destinations: Lista de objetos Destination (entidades del dominio).
        :param rules: Lista de diccionarios que representan las reglas de producción.
        """
        self._destinations = destinations
        self._rules = rules

    def infer(self, mood: Mood, duration: TimeDuration) -> List[Recommendation]:
        """
        Realiza el proceso de inferencia y devuelve las recomendaciones ordenadas.
        
        :param mood: Estado de ánimo del usuario (Enum).
        :param duration: Tiempo disponible (Enum).
        :return: Lista de objetos Recommendation ordenados por puntuación descendente.
        """
        if not self._destinations:
            return []

        # 1. Definir los hechos (facts) del entorno a partir de las entradas del usuario
        facts = {
            "mood": mood.value,
            "duration": duration.value
        }

        # 2. Fase de emparejamiento (Pattern Matching): Ver qué reglas se activan
        fired_rules = []
        tag_weights: Dict[str, float] = {}

        for rule in self._rules:
            if self._rule_applies(rule, facts):
                fired_rules.append(rule)
                # Acumular pesos para cada etiqueta recomendada en la consecuencia de la regla
                consequence = rule.get("consequences", {})
                recommended_tags = consequence.get("recommended_tags", [])
                weight_modifier = consequence.get("weight_modifier", 1.0)
                
                for tag in recommended_tags:
                    # Si la etiqueta ya fue recomendada por otra regla, sumamos los pesos
                    tag_weights[tag] = tag_weights.get(tag, 0.0) + weight_modifier

        # 3. Fase de Resolución de Conflictos y Evaluación de Destinos
        # Si ninguna regla se activa, se asigna una pequeña puntuación base si coincide
        # directamente alguna etiqueta con el estado de ánimo (búsqueda heurística básica)
        if not tag_weights:
            # Mapeo semántico simple para relacionar estados de ánimo con etiquetas de destinos
            fallback_mappings = {
                "relajado": ["relajado", "relajacion", "tranquilidad"],
                "estresado": ["estresado", "relajacion", "tranquilidad"],
                "cansado": ["cansado", "relajacion", "descanso", "campo"],
                "aventurero": ["aventurero", "aventura", "naturaleza", "montaña"],
                "aburrido": ["aburrido", "diversion", "cultura", "ciudad"]
            }
            tags_para_buscar = fallback_mappings.get(mood.value, [mood.value])
            for tag in tags_para_buscar:
                tag_weights[tag] = 1.0

        recommendations: List[Recommendation] = []

        for dest in self._destinations:
            score = 0.0
            matched_tags = []
            explanations_list = []

            # Evaluamos cuántas etiquetas del destino coinciden con las recomendadas por las reglas
            for tag in dest.tags:
                if tag in tag_weights:
                    score += tag_weights[tag]
                    matched_tags.append(tag)

            # Si el destino tiene coincidencia, creamos la recomendación
            if score > 0:
                # Construir una explicación legible de por qué se recomienda este destino
                activated_rules_desc = [f"'{r.get('description')}'" for r in fired_rules if any(t in dest.tags for t in r.get("consequences", {}).get("recommended_tags", []))]
                
                if activated_rules_desc:
                    explanation = (
                        f"Recomendado porque coincide con tus preferencias actuales mediante las reglas activadas: "
                        f"{', '.join(activated_rules_desc)}. Coincidencias de etiquetas: {matched_tags}."
                    )
                else:
                    explanation = f"Recomendación básica basada en tu estado de ánimo '{mood.value}'."

                recommendations.append(
                    Recommendation(
                        destination=dest,
                        score=round(score, 2),
                        matched_tags=matched_tags,
                        explanation=explanation
                    )
                )

        # 4. Ordenar las recomendaciones por puntuación de mayor a menor
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations

    def _rule_applies(self, rule: Dict[str, Any], facts: Dict[str, str]) -> bool:
        """
        Determina si una regla de producción se activa con los hechos actuales.
        Soporta reglas cuyas condiciones requieran mood, duration o ambos.
        
        :param rule: Diccionario con la estructura de la regla.
        :param facts: Diccionario con los hechos del usuario (mood y duration).
        :return: True si se cumplen todas las condiciones especificadas, False de lo contrario.
        """
        conditions = rule.get("conditions", {})
        if not conditions:
            return False

        # Para que la regla se active, todas sus condiciones declaradas deben coincidir con los hechos
        for key, expected_value in conditions.items():
            if facts.get(key) != expected_value:
                return False
        return True
