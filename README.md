# ViajaIA — Sistema Experto de Recomendación de Vacaciones 🌴✈️

> **Versión MVP** · Arquitectura Hexagonal · PyQt6 · Motor de Inferencia con Encadenamiento hacia Adelante

Sistema Experto que analiza el perfil del usuario (estado de ánimo, duración del viaje, presupuesto y clima) a través de un diálogo conversacional interactivo, recomendando el destino turístico ideal sustentado en una base de conocimiento de reglas de producción y explicando el razonamiento de cada decisión.

---

## 🎯 Objetivos del Proyecto

| Objetivo | Descripción |
|----------|-------------|
| **Inferencia** | Determinar el mejor destino combinando múltiples variables: estado de ánimo, duración, presupuesto y clima mediante un diccionario dinámico de hechos |
| **Explicabilidad** | El sistema justifica sus decisiones indicando qué reglas se activaron para sugerir cada destino |
| **Multiplataforma** | La GUI nativa PyQt6 funciona en Windows 11 y Linux; la CLI funciona en Docker/cualquier terminal |
| **Pedagogía Activa** | Código comentado en español para que el equipo comprenda cada decisión de diseño |

---

## 🏗️ Arquitectura Hexagonal (Puertos y Adaptadores)

La arquitectura separa el núcleo de negocio de toda tecnología externa mediante tres capas:

```text
  ╔═══════════════════════════════════════════════════════════════╗
  ║                       ADAPTADORES                             ║
  ║                                                               ║
  ║   [Inbound]          [Inbound]          [Outbound]            ║
  ║   PyQt6 GUI ──────►  CLI Console ────►  JSON Repository       ║
  ║      │                   │                    │               ║
  ╠══════│═══════════════════│════════════════════│═══════════════╣
  ║      │    PUERTOS        │                    │               ║
  ║      │  RecommendationUseCase           DestinationRepository ║
  ║      │  (ports/inbound.py)              (ports/outbound.py)   ║
  ╠══════│═══════════════════│════════════════════│═══════════════╣
  ║      │                   │    DOMINIO         │               ║
  ║      └───────────────────┼────────────────────┘               ║
  ║                          │                                    ║
  ║          VacationRecommendationService                        ║
  ║            (domain/services.py)                               ║
  ║                    │                                          ║
  ║          VacationExpertSystem                                 ║
  ║            (domain/rules_engine.py)                           ║
  ║            Forward Chaining + Dict de Hechos                  ║
  ║                    │                                          ║
  ║          Destination · Recommendation · Mood · TimeDuration   ║
  ║            (domain/models.py)                                 ║
  ╚═══════════════════════════════════════════════════════════════╝
```

### 📁 Mapa de Archivos

```
Sistema_Experto/
├── src/
│   ├── main.py                          ← Punto de entrada / Composition Root
│   ├── config.py                        ← Rutas globales del proyecto
│   ├── domain/
│   │   ├── models.py                    ← Entidades: Destination, Recommendation, Mood, TimeDuration
│   │   ├── rules_engine.py              ← Motor de Inferencia (Forward Chaining)
│   │   ├── services.py                  ← Caso de Uso: VacationRecommendationService
│   │   └── exceptions.py               ← DomainError, InferenceError
│   ├── ports/
│   │   ├── inbound.py                   ← Puerto: RecommendationUseCase (ABC)
│   │   └── outbound.py                  ← Puerto: DestinationRepository (ABC)
│   └── adapters/
│       ├── inbound/
│       │   ├── cli.py                   ← Adaptador: Interfaz de consola interactiva
│       │   └── pyqt_app/
│       │       ├── app.py               ← Inicializador de la app PyQt6
│       │       └── main_window.py       ← GUI conversacional + formulario experto
│       └── outbound/
│           └── json_repository.py       ← Adaptador: Lectura de destinations.json
├── data/
│   └── destinations.json                ← Base de Conocimiento (destinos + reglas)
├── tests/
│   ├── test_rules_engine.py             ← Tests del motor de inferencia
│   └── test_json_repository.py          ← Tests del repositorio JSON
├── ejecutar_linux.sh                    ← 🐧 Lanzador para Linux (un clic)
├── ejecutar_windows.bat                 ← 🪟 Lanzador para Windows (CMD)
├── ejecutar_windows.ps1                 ← 🪟 Lanzador para Windows (PowerShell)
├── INSTALACION.md                       ← Guía de instalación y troubleshooting
├── Dockerfile                           ← Imagen Docker (CLI + pruebas)
└── docker-compose.yml                   ← Orquestador Docker
```

---

## 🧠 Motor de Inferencia — Cómo funciona

El motor (`VacationExpertSystem`) implementa **Forward Chaining (Encadenamiento hacia Adelante)**. A partir de la versión MVP (Fase 4) acepta un **diccionario dinámico de hechos** en lugar de solo dos parámetros fijos, lo que permite escalar a más variables sin modificar la firma de la API.

### Flujo de Inferencia

```
 Usuario selecciona en GUI
 ┌─────────────────────────────────────────────────────────┐
 │  estado de ánimo + duración + presupuesto + clima + ... │
 └───────────────────┬─────────────────────────────────────┘
                     │ user_facts = {"mood": "aventurero",
                     │               "duration": "mas_de_una_semana",
                     │               "presupuesto": "Bajo", ...}
                     ▼
         ┌─────────────────────┐
         │  Pattern Matching   │  ← ¿Qué reglas se activan?
         │  _rule_applies()    │    Todas las condiciones deben coincidir
         └────────┬────────────┘
                  │  fired_rules = [rule_aventurero_largo, ...]
                  ▼
         ┌─────────────────────┐
         │  Acumulación de     │  ← tag_weights["aventura"] += 3.0
         │  Pesos por Etiqueta │    tag_weights["montaña"]  += 3.0
         └────────┬────────────┘
                  │
                  ▼
         ┌─────────────────────┐
         │  Evaluación de      │  ← score = Σ tag_weights[tag] para cada
         │  Destinos           │    tag del destino que esté en tag_weights
         └────────┬────────────┘
                  │
                  ▼
         ┌─────────────────────┐
         │  Ranking + Explic.  │  ← Ordenados por score desc.
         │  Generación         │    + texto legible de reglas activadas
         └─────────────────────┘
```

### Reglas de Producción (Ejemplo)

```json
{
  "id": "rule_aventurero_largo",
  "description": "Si el usuario busca aventura y tiene más de una semana...",
  "conditions": {
    "mood": "aventurero",
    "duration": "mas_de_una_semana"
  },
  "consequences": {
    "recommended_tags": ["aventura", "montaña", "naturaleza"],
    "weight_modifier": 3.0
  }
}
```

### API del Servicio

```python
# Firma actual (Fase 4 MVP)
svc.obtener_recomendacion(user_facts: Dict[str, Any]) -> List[Recommendation]

# Ejemplo de llamada
resultados = svc.obtener_recomendacion({
    "mood":        "aventurero",
    "duration":    "mas_de_una_semana",
    "presupuesto": "Bajo"
})
# → [Trekking en la Patagonia (9.0 pts), Mochilazo en la Huasteca (6.0 pts), ...]
```

---

## 📂 Base de Conocimiento (`data/destinations.json`)

La base de conocimiento es editable sin tocar código. Consta de dos secciones:

### Destinos disponibles (6)

| Nombre | Presupuesto | Tags principales |
|--------|------------|-----------------|
| Cabaña en el Bosque (Mazamitla) | Bajo | bosque, tranquilidad, frio, relajacion, economico |
| Playa del Carmen (Riviera Maya) | Alto | playa, sol, calor, relajacion, diversion |
| Trekking extremo en la Patagonia | Alto | montaña, aventura, frio, deporte, naturaleza |
| Mochilazo en la Huasteca Potosina | Bajo-Medio | aventura, calor, naturaleza, agua, economico |
| Tour Cultural en Ciudad de México | Medio | ciudad, historia, cultura, gastronomia, museos |
| Pueblo Mágico del Tequila | Medio | campo, historia, gastronomia, cultura, relajacion |

### Reglas de Producción (6)

| ID | Condiciones | Destinos favorecidos |
|----|-------------|---------------------|
| `rule_estresado_fin_semana` | mood=estresado + fin_de_semana | Bosque, campo |
| `rule_estresado_semana_completa` | mood=estresado + una_semana | Playa |
| `rule_aventurero_largo` | mood=aventurero + mas_de_una_semana | Patagonia |
| `rule_aventurero_corto` | mood=aventurero + fin_de_semana | Huasteca |
| `rule_aburrido_cualquier_tiempo` | mood=aburrido | CDMX, cultura |
| `rule_cansado_corto` | mood=cansado + fin_de_semana | Tequila, campo |

> Las condiciones admiten **cualquier clave del diccionario de hechos**. Para agregar una nueva regla o destino basta con editar el JSON.

---

## 🚀 Guía de Ejecución

### 🐧 Linux — Lanzador Automático (Recomendado)

```bash
# La primera vez, dar permisos de ejecución:
chmod +x ejecutar_linux.sh

# Ejecutar (instala automáticamente todo lo necesario):
./ejecutar_linux.sh

# Si necesitas reinstalar desde cero:
./ejecutar_linux.sh --reinstalar
```

El script hace automáticamente:
1. ✅ Verifica Python 3.10+
2. ✅ Instala librerías gráficas del sistema para PyQt6 (`libxcb`, `libgl1`, `libxkbcommon`)
3. ✅ Crea un entorno virtual `.venv_viajaia/`
4. ✅ Instala todas las dependencias
5. ✅ Lanza la aplicación

---

### 🪟 Windows 11 — Lanzadores Automáticos (Recomendado)

**Opción A — PowerShell (con colores y UI visual):**
```powershell
# Clic derecho en ejecutar_windows.ps1 → "Ejecutar con PowerShell"
# O desde terminal:
powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1

# Reinstalar desde cero:
powershell -ExecutionPolicy Bypass -File ejecutar_windows.ps1 -Reinstalar
```

**Opción B — CMD (doble clic):**
```batch
ejecutar_windows.bat
```

> ⚠️ **Requisito:** Python 3.10+ instalado desde [python.org](https://python.org/downloads).  
> En el instalador, marcar **"Add Python to PATH"**.

---

### 🐳 Docker — CLI (Desarrollo / Pruebas sin GUI)

Ideal para correr pruebas automatizadas o la interfaz de consola en cualquier sistema operativo sin instalar dependencias locales.

```bash
# Arrancar la CLI interactiva:
docker-compose up --build

# Ejecutar pruebas unitarias:
docker-compose run app pytest

# Ejecutar pruebas con salida detallada:
docker-compose run app pytest -v
```

---

### ⚙️ Manual (cualquier plataforma)

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# .\venv\Scripts\Activate.ps1    # Windows PowerShell

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Lanzar con GUI
python src/main.py

# 4. Lanzar solo CLI (sin PyQt6)
python src/main.py --cli
```

---

## 🧪 Pruebas Automatizadas

```bash
# Ejecutar toda la suite
pytest

# Con detalle
pytest -v

# Solo motor de inferencia
pytest tests/test_rules_engine.py -v

# Solo repositorio JSON
pytest tests/test_json_repository.py -v
```

La suite cubre:
- **`test_rules_engine.py`**: Activación correcta de reglas de producción, fallback heurístico cuando no hay reglas activas, y cálculo de puntajes de coincidencia.
- **`test_json_repository.py`**: Carga correcta del JSON, resiliencia ante archivos malformados o vacíos.

---

## 📖 Glosario del Sistema Experto

| Término | Definición |
|---------|-----------|
| **Hecho (Fact)** | Información conocida sobre el usuario: `{"mood": "aventurero", "duration": "fin_de_semana"}` |
| **Regla de Producción** | Estructura `SI <condiciones> ENTONCES <consecuencias>` almacenada en el JSON |
| **Encadenamiento hacia Adelante** | El motor parte de los hechos conocidos y dispara reglas hasta obtener conclusiones |
| **Pattern Matching** | Proceso de comparar los hechos actuales contra las condiciones de cada regla |
| **Peso (weight_modifier)** | Valor numérico que indica cuánto contribuye una regla al puntaje de un destino |
| **Score** | Suma de pesos de todas las etiquetas de un destino que coinciden con las reglas activadas |
| **Explicación** | Texto generado automáticamente que indica qué reglas justifican cada recomendación |
| **Fallback heurístico** | Si ninguna regla se activa, el motor busca por similitud de tags del `mood` |

---

## 👥 Créditos y Contribuciones

Proyecto desarrollado por el equipo universitario para la materia de **Fundamentos de Inteligencia Artificial**.

| Fase | Responsabilidad | Estado |
|------|----------------|--------|
| Fase 1 | Corrección de bugs y conexión GUI↔Motor | ✅ Completa |
| Fase 2 | Integración GUI conversacional con motor de inferencia | ✅ Completa |
| Fase 3 | Expansión de la base de conocimiento | ✅ Completa |
| Fase 4 | Motor de inferencia dinámico (dict de hechos multi-variable) | ✅ Completa |
| Fase 5 | Pulido de presentación (UI, scripts de lanzamiento) | ✅ Completa |
