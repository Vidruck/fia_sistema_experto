# Sistema Experto de Recomendación de Vacaciones 🌴✈️

Este es un **Sistema Experto inicial** diseñado para analizar el estado de ánimo de un usuario y su disponibilidad de tiempo a través de un diálogo interactivo, recomendando el destino turístico ideal sobre una base de conocimiento y reglas de producción.

El proyecto está diseñado bajo un esquema riguroso de **Arquitectura Hexagonal (Puertos y Adaptadores)** y empaquetado con **Docker** para su desarrollo, priorizando la optimización de recursos y las buenas prácticas de desarrollo de software para el equipo universitario.

---

## 🎯 Objetivos del Proyecto
1. **Analizar Hechos**: Determinar el mejor destino según la combinación de Estado de Ánimo (`Mood`) y Duración del Viaje (`TimeDuration`).
2. **Explicabilidad**: El sistema experto es transparente y justifica sus decisiones indicando qué reglas se activaron para sugerir un destino.
3. **Multiplataforma**: La interfaz visual se desacopla del core lógico. La interfaz de usuario funciona en Windows, Linux y macOS de forma nativa.
4. **Pedagogía Activa**: El código contiene comentarios explicativos detallados en español para que los estudiantes comprendan cada decisión de diseño.

---

## 🏗️ Directiva de Diseño: Arquitectura Hexagonal

La arquitectura se divide en tres capas fundamentales, separadas por límites claros:

```text
               ┌──────────────────────────────────────────────────┐
               │                    ADAPTADORES                   │
               │   ┌──────────────────────────────────────────┐   │
               │   │                 PUERTOS                  │   │
               │   │   ┌──────────────────────────────────┐   │   │
               │   │   │             DOMINIO              │   │   │
               │   │   │   ┌──────────────────────────┐   │   │   │
               │   │   │   │ Modelos de datos         │   │   │   │
               │   │   │   │ (Mood, TimeDuration...)  │   │   │   │
               │   │   │   └──────────────────────────┘   │   │   │
               │   │   │   ┌──────────────────────────┐   │   │   │
  PyQt GUI ───>│──>│──>│   │ Motor de Inferencia      │   │   │   │
  (Inbound)    │   │   │   │ (Forward Chaining)       │   │   │   │
               │   │   │   └──────────────────────────┘   │   │   │
  CLI Console ─>│──>│──>│                              │   │   │   │
  (Inbound)    │   │   └──────────────────────────────────┘   │   │   │
               │   │                                          │   │   │
               │   │   ┌──────────────────────────────────┐   │   │   │
               │   └──>│ DestinationRepository (Puerto)   │──>│───┼─> Archivo JSON
               │       └──────────────────────────────────┘   │   │   (Outbound)
               └──────────────────────────────────────────┘   │
               └──────────────────────────────────────────────────┘
```

### 1. Capa de Dominio (Hexágono Interno)
* **Modelos (`src/domain/models.py`)**: Clases de datos inmutables y enums limpios. No tienen dependencias de bases de datos o frameworks.
* **Motor de Inferencia (`src/domain/rules_engine.py`)**: Implementa un algoritmo de *Forward Chaining* (Encadenamiento hacia adelante). Busca qué reglas en formato JSON coinciden con los hechos actuales y puntúa los destinos según el peso de cada consecuencia.
* **Excepciones (`src/domain/exceptions.py`)**: Control de errores específicos del dominio.

### 2. Capa de Puertos (Interfaces)
* **Puertos de Entrada (Driving Ports - `src/ports/inbound.py`)**: Contrato (`RecommendationUseCase`) que la interfaz gráfica o consola debe utilizar para comunicarse con el negocio.
* **Puertos de Salida (Driven Ports - `src/ports/outbound.py`)**: Contrato (`DestinationRepository`) que define qué datos necesita el núcleo del negocio de fuentes externas.

### 3. Capa de Adaptadores (Implementaciones)
* **Adaptadores de Entrada (Inbound Adapters)**:
  * **Consola (`src/adapters/inbound/cli.py`)**: Menú interactivo por línea de comandos para depuración rápida.
  * **PyQt GUI (`src/adapters/inbound/pyqt_app/`)**: Interfaz gráfica moderna, responsiva, estilizada con hojas de estilos oscuras (esquema Catppuccin Mocha) y soporte de HTML interactivo para mostrar resultados.
* **Adaptadores de Salida (Outbound Adapters)**:
  * **Persistencia JSON (`src/adapters/outbound/json_repository.py`)**: Lee la base de conocimiento estructurada de `data/destinations.json`.

---

## 📂 Base de Conocimiento (`data/destinations.json`)

La base de conocimiento es editable y consta de dos secciones:
1. **`destinations`**: Los lugares disponibles para viajar, categorizados por presupuesto y etiquetas (`tags`).
2. **`rules`**: Reglas lógicas de formato `SI <condiciones> ENTONCES <consecuencias>`.
   * Ejemplo: Si el estado de ánimo es *estresado* y la duración es *fin de semana*, se recomiendan etiquetas de *bosque*, *tranquilidad* y *relajación* con un modificador de peso de `2.5`.

---

## 🛠️ Guía de Uso del Entorno

### Opción A: Ejecución en Contenedor (Recomendado para desarrollo/CLI)
Esta opción es ideal para correr el proyecto y sus pruebas automatizadas en cualquier sistema operativo sin instalar dependencias locales. Por defecto levantará la interfaz de consola interactiva.

1. **Construir el contenedor y arrancar la CLI**:
   ```bash
   docker-compose up --build
   ```
2. **Ejecutar las pruebas unitarias dentro del contenedor**:
   ```bash
   docker-compose run app pytest
   ```

---

### Opción B: Ejecución Nativa (Recomendado para la Interfaz Gráfica PyQt6)
Para ver la interfaz gráfica enriquecida, es recomendable ejecutarla nativamente en tu computadora host, ya que el motor de renderizado gráfico nativo corre con mayor velocidad y fluidez sin configurar X11 en Docker.

1. **Crear y activar un entorno virtual (venv)**:
   * **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar la aplicación con la interfaz gráfica (GUI)**:
   ```bash
   python src/main.py
   ```
   *(Nota: Puedes forzar la CLI de forma nativa usando `python src/main.py --cli`)*

4. **Ejecutar pruebas unitarias locales**:
   ```bash
   pytest
   ```

---

## 🧪 Pruebas Automatizadas

El código cuenta con una suite completa de pruebas unitarias localizadas en la carpeta `tests/` para verificar:
1. La correcta activación de las reglas de producción en el motor de inferencia (`test_rules_engine.py`).
2. La resiliencia ante archivos JSON mal formados o vacíos en el repositorio (`test_json_repository.py`).
