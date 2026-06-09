"""
MÓDULO: src/adapters/inbound/pyqt_app/main_window.py
PROPÓSITO:
    Define la ventana principal de la interfaz de usuario en PyQt6 (Inbound Adapter).
    Presenta un diseño moderno, responsivo y oscuro con estilos personalizados (CSS/QSS)
    inspirado en el esquema de color Catppuccin Mocha.
DOCENCIA (Para el equipo de desarrollo universitario):
    - Esta clase hereda de `QMainWindow` y representa la capa de presentación.
    - Se comunica únicamente con la abstracción `RecommendationUseCase` mediante inyección
      de dependencias en el constructor.
    - Usamos HTML enriquecido dentro de un `QTextBrowser` para renderizar las recomendaciones de forma
      atractiva, con insignias de puntuación y justificaciones formateadas sin necesidad de componentes complejos.
    - Se manejan excepciones locales y se reportan visualmente al usuario mediante diálogos de error.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextBrowser,
    QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from src.ports.inbound import RecommendationUseCase
from src.domain.models import Mood, TimeDuration
from src.domain.exceptions import DomainError

# ================= DATOS DE DESTINOS =================
DESTINOS_DATA = {
    "bacalar": {
        "nombre":      "Bacalar",
        "estado":      "Quintana Roo",
        "rating":      "⭐ 4.8  (1,250 reseñas)",
        "precio":      "Desde $8,200 por persona",
        "descripcion": "La Laguna de los Siete Colores te espera con\nsus aguas cristalinas, tranquilidad y paisajes\nde ensueño.",
        "tags":        ["☀️ Relajación", "🏖️ Playa", "🌿 Naturaleza", "💚 Romántico"],
        "plan_titulo": "Bacalar, Quintana Roo",
        "plan_dias":   "4 a 7 días",
        "itinerario": [
            ("Día 1", "Llegada y paseo en velero al atardecer"),
            ("Día 2", "Tour a los rápidos y Cenote Azul"),
            ("Día 3", "Día libre para relajarte"),
            ("Día 4", "Kayak en la laguna y despedida"),
        ],
        "incluye": [
            ("✅", "Hospedaje 4 noches en hotel boutique"),
            ("✅", "Desayunos incluidos cada día"),
            ("✅", "Tour en velero al atardecer"),
            ("✅", "Traslados aeropuerto–hotel"),
        ],
        "opcionales": [
            ("➕", "Kayak privado — $800 extra"),
            ("➕", "Cena romántica en la laguna — $1,200"),
            ("➕", "Clase de paddleboard — $600"),
        ],
    },
    "holbox": {
        "nombre":      "Holbox",
        "estado":      "Quintana Roo",
        "rating":      "⭐ 4.7  (980 reseñas)",
        "precio":      "Desde $9,100 por persona",
        "descripcion": "Isla sin coches, con playas de arena blanca,\nbioluminiscencia nocturna y la magia\nde un pueblo pesquero auténtico.",
        "tags":        ["🌅 Sunset", "🦈 Tiburón ballena", "🌿 Ecológico", "🐚 Playa"],
        "plan_titulo": "Holbox, Quintana Roo",
        "plan_dias":   "4 a 7 días",
        "itinerario": [
            ("Día 1", "Llegada en ferry y paseo al atardecer"),
            ("Día 2", "Snorkel con tiburón ballena (temporada)"),
            ("Día 3", "Tour en kayak por los manglares"),
            ("Día 4", "Día libre en la playa y despedida"),
        ],
        "incluye": [
            ("✅", "Hospedaje 4 noches frente al mar"),
            ("✅", "Ferry de ida y vuelta"),
            ("✅", "Tour de bioluminiscencia nocturna"),
            ("✅", "Desayunos incluidos"),
        ],
        "opcionales": [
            ("➕", "Tour tiburón ballena — $1,500 extra"),
            ("➕", "Masaje en la playa — $900"),
            ("➕", "Renta de golf cart — $500/día"),
        ],
    },
    "vallarta": {
        "nombre":      "Puerto Vallarta",
        "estado":      "Jalisco",
        "rating":      "⭐ 4.6  (2,100 reseñas)",
        "precio":      "Desde $8,900 por persona",
        "descripcion": "Ciudad costera vibrante con el Malecón,\nrestaurantes de autor, vida nocturna\ny playas de aguas cálidas.",
        "tags":        ["🌆 Ciudad", "🍽️ Gastronomía", "🎭 Cultura", "🏖️ Playa"],
        "plan_titulo": "Puerto Vallarta, Jalisco",
        "plan_dias":   "4 a 7 días",
        "itinerario": [
            ("Día 1", "Llegada y cena en el Malecón"),
            ("Día 2", "Tour en barco a las Islas Marietas"),
            ("Día 3", "Recorrido por el centro histórico"),
            ("Día 4", "Playa Los Muertos y despedida"),
        ],
        "incluye": [
            ("✅", "Hospedaje 4 noches zona hotelera"),
            ("✅", "Tour en barco Islas Marietas"),
            ("✅", "Traslados aeropuerto–hotel"),
            ("✅", "Desayunos incluidos"),
        ],
        "opcionales": [
            ("➕", "Clase de cocina local — $700 extra"),
            ("➕", "Zip-line en la Sierra — $1,100"),
            ("➕", "Cena romántica en la playa — $1,400"),
        ],
    },
}

# ================= HOJA DE ESTILOS QSS =================
QSS_STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget#centralWidget {
    background-color: #1e1e2e;
}
QLabel {
    color: #cdd6f4;
    font-family: 'Segoe UI', -apple-system, Roboto, sans-serif;
    font-size: 14px;
}
QLabel#titleLabel {
    color: #cba6f7;
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 5px;
}
QLabel#subtitleLabel {
    color: #a6adc8;
    font-size: 13px;
    margin-bottom: 20px;
}
QLabel#sectionLabel {
    color: #f5c2e7;
    font-size: 15px;
    font-weight: bold;
    margin-top: 10px;
}
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    min-width: 200px;
}
QComboBox:hover {
    border: 1px solid #cba6f7;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    selection-color: #cba6f7;
    border: 1px solid #45475a;
}
QPushButton#recommendButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #cba6f7, stop:1 #f5c2e7);
    color: #11111b;
    border: none;
    border-radius: 8px;
    padding: 14px;
    font-size: 15px;
    font-weight: bold;
    margin-top: 25px;
}
QPushButton#recommendButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b4befe, stop:1 #cba6f7);
}
QPushButton#recommendButton:pressed {
    background: #a6e3a1;
}
QTextBrowser#resultsBrowser {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 15px;
}
"""


class MainWindow(QMainWindow):
    """
    Ventana principal de la interfaz gráfica.
    """

    def __init__(self, use_case: RecommendationUseCase):
        super().__init__()
        self._use_case = use_case

        # Estado de la conversación — aquí se guardan TODAS las selecciones del usuario
        self.tipo_viaje = ""
        self.tipo_escapada = ""
        self.presupuesto = ""
        self.sentimiento = ""
        self.clima = ""
        self.duracion = ""
        self.destino = ""
        self.recomendaciones = []          # Resultados del motor de inferencia
        self.recomendacion_actual = None   # Recomendación actualmente seleccionada

        # Primero inicializamos la UI base que crea el 'self.stack' primordial
        self.init_ui()

    # ------------------------------------------------------------------
    # MÉTODOS AUXILIARES DE NAVEGACIÓN (guardan estado + actualizan UI)
    # ------------------------------------------------------------------

    def _ir_a_romantica(self, tipo):
        self.tipo_viaje = tipo
        iconos = {
            'Solo':    '🧍  Solo',
            'Pareja':  '❤️  Pareja',
            'Familia': '👨\u200d👩\u200d👧  Familia',
            'Amigos':  '👥  Amigos',
        }
        self.lbl_categoria_romantica.setText(iconos.get(tipo, tipo))
        self.stack.setCurrentWidget(self.romantic_page)

    def _ir_a_presupuesto(self, escapada):
        self.tipo_escapada = escapada
        self._actualizar_tags_presupuesto()
        self.stack.setCurrentWidget(self.budget_page)

    def _ir_a_sentimiento(self, presupuesto):
        self.presupuesto = presupuesto
        self._actualizar_tags_sentimiento()
        self.stack.setCurrentWidget(self.feeling_page)

    def _ir_a_clima(self, sentimiento):
        self.sentimiento = sentimiento
        self._actualizar_tags_clima()
        self.stack.setCurrentWidget(self.climate_page)

    def _ir_a_duracion(self, clima):
        self.clima = clima
        self._actualizar_tags_duracion()
        self.stack.setCurrentWidget(self.duration_page)

    def _ir_a_destinos(self, duracion):
        self.duracion = duracion
        
        # 1. Obtener el diccionario de hechos (Fase 4 del MVP)
        user_facts, mood_str, duration_str = self._mapear_selecciones()
        
        # 2. Llamar al motor de inferencia real pasándole el diccionario
        try:
            # Aquí se corrige el antiguo typo "obtener_recommendacion"
            self.recomendaciones = self._use_case.obtener_recomendacion(user_facts)
            
            # (Opcional) Imprimir en terminal para debugging
            print(f"Hechos enviados al motor: {user_facts}")
            print(f"Destinos inferidos: {len(self.recomendaciones)}")
            
        except Exception as err:
            print(f"[ADVERTENCIA] Error en inferencia: {err}")
            self.recomendaciones = []
            
        # 3. Poblar la pantalla de destinos (Tu lógica ya hace esto muy bien)
        self._poblar_destinos_dinamicos()
        self.stack.setCurrentWidget(self.destinos_page)

    def _mapear_selecciones(self):
        """Mapea todas las selecciones conversacionales de la GUI a un diccionario de hechos para el motor."""
        
        # 1. Mapeo de Sentimiento -> Mood (Mantenemos tu lógica original como base)
        mapa_sentimiento = {
            'Relajación':                 'relajado',
            'Contacto con la naturaleza': 'aventurero',
            'Aventura':                   'aventurero',
            'Cultura e historia':         'aburrido',
            'Diversión nocturna':         'aburrido',
        }
        mapa_escapada = {
            'Escapada romántica': 'relajado',
            'Aventura juntos':    'aventurero',
            'Relax y bienestar':  'relajado',
            'Ciudad y encanto':   'aburrido',
        }
        mood_str = (
            mapa_sentimiento.get(self.sentimiento)
            or mapa_escapada.get(self.tipo_escapada, 'relajado')
        )

        # 2. Mapeo de Duración -> TimeDuration
        mapa_duracion = {
            'Fin de semana (2-3 días)': 'fin_de_semana',
            '4 a 7 días':               'una_semana',
            'Más de una semana':        'mas_de_una_semana',
        }
        duration_str = mapa_duracion.get(self.duracion, 'una_semana')

        # 3. Mapeo de Presupuesto
        # Convertimos los textos de la interfaz a los valores que probablemente uses en el JSON
        mapa_presupuesto = {
            'Menos de $5,000':        'Bajo',
            '$5,000 - $15,000':       'Medio',
            'Más de $15,000':         'Alto'
        }
        presupuesto_str = mapa_presupuesto.get(self.presupuesto, 'Medio')

        # 4. Construimos el diccionario de hechos completo para la Fase 4
        user_facts = {
            "mood": mood_str,
            "duration": duration_str,
            "presupuesto": presupuesto_str,
            "clima": self.clima.lower() if self.clima and self.clima != 'No importa' else None,
            "tipo_viaje": self.tipo_viaje.lower() if self.tipo_viaje else None
        }

        # Limpiar el diccionario de valores None
        user_facts = {k: v for k, v in user_facts.items() if v is not None}
        
        return user_facts, mood_str, duration_str # Devolvemos los strings extra para que tu UI no se rompa

    def _poblar_destinos_dinamicos(self):
        """Limpia y repuebla las tarjetas de destinos con resultados del motor de inferencia."""
        
        # --- CAMBIA ESTA LÍNEA ---
        user_facts, mood_str, duration_str = self._mapear_selecciones()
        # -------------------------
        
        mapa_mood_legible = {
            'relajado':   '🌴 Relajación',
            'aventurero': '⛰️ Aventura',
            'aburrido':   '🏛️ Cultura / Diversión',
            'estresado':  '🌿 Tranquilidad',
            'cansado':    '🛌 Descanso',
        }
        
        mapa_dur_legible = {
            'fin_de_semana':     'fin de semana',
            'una_semana':        '4–7 días',
            'mas_de_una_semana': 'más de una semana',
        }
        mood_legible = mapa_mood_legible.get(mood_str, mood_str)
        dur_legible  = mapa_dur_legible.get(duration_str, duration_str)
        self.lbl_destinos_sub.setText(
            f"Perfil detectado: {mood_legible}  •  {dur_legible}\n"
            f"↓ Ordenados por compatibilidad con tus preferencias"
        )

        # Limpiar el contenedor de tarjetas actual
        while self.destinos_cards_layout.count():
            item = self.destinos_cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:13px; font-weight:bold;
                          text-align:left; padding:12px; }
            QPushButton:hover { background:#11c5c6; }
        """
        presupuesto_icons = {"Bajo": "💚", "Bajo-Medio": "💛", "Medio": "🟡", "Alto": "💜"}
        destinos_a_mostrar = self.recomendaciones[:4] if self.recomendaciones else []

        if not destinos_a_mostrar:
            lbl = QLabel("No se encontraron destinos para tus preferencias.\nIntenta con otras opciones.")
            lbl.setStyleSheet("color:#f38ba8; font-size:15px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.destinos_cards_layout.addWidget(lbl)
            return

        for rec in destinos_a_mostrar:
            dest = rec.destination
            icono = presupuesto_icons.get(dest.budget, "💰")
            num_estrellas = min(int(rec.score / 1.5) + 1, 5)
            stars = "⭐" * num_estrellas
            etiqueta = (
                f"{dest.name}\n\n"
                f"{icono} Presupuesto: {dest.budget}\n\n"
                f"Compatibilidad: {stars}\n({rec.score:.1f} pts)"
            )
            btn = QPushButton(etiqueta)
            btn.setFixedSize(200, 200)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(_btn_style)
            btn.clicked.connect(lambda _, r=rec: self._ir_a_detalle_rec(r))
            self.destinos_cards_layout.addWidget(btn)

        self.destinos_cards_layout.addStretch()

    # ------------------------------------------------------------------
    # MÉTODOS QUE ACTUALIZAN LOS TAGS DINÁMICOS DE CADA PANTALLA
    # ------------------------------------------------------------------

    def _tag_style(self):
        return """
            background:#134f53;
            color:white;
            padding:8px;
            border-radius:15px;
            font-size:14px;
            font-weight:bold;
        """

    def _actualizar_tags_presupuesto(self):
        iconos_viaje = {
            'Solo': '🧍', 'Pareja': '❤️', 'Familia': '👨\u200d👩\u200d👧', 'Amigos': '👥'
        }
        icono = iconos_viaje.get(self.tipo_viaje, '🧳')
        self.tag_budget_viaje.setText(f"{icono}  {self.tipo_viaje}")
        self.tag_budget_escapada.setText(f"✨  {self.tipo_escapada}")

    def _actualizar_tags_sentimiento(self):
        self._actualizar_tags_presupuesto()
        iconos_viaje = {
            'Solo': '🧍', 'Pareja': '❤️', 'Familia': '👨\u200d👩\u200d👧', 'Amigos': '👥'
        }
        icono = iconos_viaje.get(self.tipo_viaje, '🧳')
        self.tag_feeling_viaje.setText(f"{icono}  {self.tipo_viaje}")
        self.tag_feeling_escapada.setText(f"✨  {self.tipo_escapada}")
        self.tag_feeling_presupuesto.setText(f"💰  {self.presupuesto}")

    def _actualizar_tags_clima(self):
        iconos_viaje = {
            'Solo': '🧍', 'Pareja': '❤️', 'Familia': '👨\u200d👩\u200d👧', 'Amigos': '👥'
        }
        icono = iconos_viaje.get(self.tipo_viaje, '🧳')
        self.tag_clima_viaje.setText(f"{icono}  {self.tipo_viaje}")
        self.tag_clima_escapada.setText(f"✨  {self.tipo_escapada}")
        self.tag_clima_presupuesto.setText(f"💰  {self.presupuesto}")
        self.tag_clima_sentimiento.setText(f"🌴  {self.sentimiento}")

    def _actualizar_tags_duracion(self):
        iconos_viaje = {
            'Solo': '🧍', 'Pareja': '❤️', 'Familia': '👨\u200d👩\u200d👧', 'Amigos': '👥'
        }
        icono = iconos_viaje.get(self.tipo_viaje, '🧳')
        self.tag_dur_viaje.setText(f"{icono}  {self.tipo_viaje}")
        self.tag_dur_escapada.setText(f"✨  {self.tipo_escapada}")
        self.tag_dur_presupuesto.setText(f"💰  {self.presupuesto}")
        self.tag_dur_sentimiento.setText(f"🌴  {self.sentimiento}")
        self.tag_dur_clima.setText(f"🏝️  {self.clima}")

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA UI (Métodos de página migrados dentro de MainWindow)
    # ------------------------------------------------------------------

    def init_ui(self):
        """Inicializa todos los widgets y layouts de la interfaz."""
        self.setWindowTitle("Asistente Experto de Vacaciones")
        self.resize(950, 650)
        self.setMinimumSize(850, 550)
        self.setStyleSheet(QSS_STYLESHEET)

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Creamos PRIMERO el QStackedWidget fundamental
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # 2. Ahora sí construimos cada pantalla de forma segura sin romper referencias
        self._build_welcome_page()    # índice 0
        self._build_travel_page()     # índice 1
        self._build_romantic_page()   # índice 2
        self._build_budget_page()     # índice 3
        self._build_feeling_page()    # índice 4
        self._build_climate_page()    # índice 5
        self._build_duration_page()   # índice 6
        self._build_destinos_page()   # índice 7
        self._build_detalle_page()    # índice 8
        
        self._build_plan_page()       # índice 9 (Bacalar por defecto)
        self._build_plan_holbox_page()   
        self._build_plan_vallarta_page() 
        
        self._build_saved_page()      # índice 10
        self._build_profile_page()    # índice 11
        self._build_main_page()       # índice 12

        self.stack.setCurrentIndex(0)

    # ================= PANTALLA 0: BIENVENIDA =================
    def _build_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        titulo = QLabel("ViajaIA")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:#5ce1e6; font-size:34px; font-weight:bold;")

        subtitulo = QLabel("Tu asistente inteligente de viajes")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color:white; font-size:16px;")

        robot = QLabel("🤖")
        robot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        robot.setStyleSheet("font-size:60px;")

        texto = QLabel("Cuéntame qué tienes en mente\ny yo encontraré el viaje perfecto\npara ti.")
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texto.setStyleSheet("color:white; font-size:20px;")

        btn_inicio = QPushButton("Comenzar")
        btn_inicio.setFixedHeight(55)
        btn_inicio.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_inicio.setStyleSheet("""
            QPushButton { background:#11c5c6; color:white; border:none; border-radius:25px;
                          font-size:18px; font-weight:bold; padding:10px; }
            QPushButton:hover { background:#19d8d9; }
        """)
        btn_inicio.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(25)
        layout.addWidget(robot)
        layout.addWidget(texto)
        layout.addSpacing(30)
        layout.addWidget(btn_inicio)
        layout.addStretch()

        self.stack.addWidget(page)

    # ================= PANTALLA 1: ¿CON QUIÉN VIAJAS? =================
    def _build_travel_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        titulo = QLabel("¿Con quién vas a viajar?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        sub = QLabel("Selecciona una opción")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#b0b0b0; font-size:15px;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border-radius:18px;
                          font-size:18px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_solo    = QPushButton("🧍\n\nSolo")
        btn_pareja  = QPushButton("❤️\n\nPareja")
        btn_familia = QPushButton("👨\u200d👩\u200d👧\n\nFamilia")
        btn_amigos  = QPushButton("👥\n\nAmigos")

        for b in [btn_solo, btn_pareja, btn_familia]:
            b.setFixedSize(180, 150)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)

        btn_amigos.setFixedSize(250, 150)
        btn_amigos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_amigos.setStyleSheet(_btn_style)

        btn_solo.clicked.connect(   lambda: self._ir_a_romantica('Solo'))
        btn_pareja.clicked.connect( lambda: self._ir_a_romantica('Pareja'))
        btn_familia.clicked.connect(lambda: self._ir_a_romantica('Familia'))
        btn_amigos.clicked.connect( lambda: self._ir_a_romantica('Amigos'))

        fila = QHBoxLayout()
        fila.addWidget(btn_solo)
        fila.addWidget(btn_pareja)
        fila.addWidget(btn_familia)

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(sub)
        layout.addSpacing(30)
        layout.addLayout(fila)
        layout.addSpacing(15)
        layout.addWidget(btn_amigos, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.stack.addWidget(page)

    # ================= PANTALLA 2: ESCAPADA ROMÁNTICA =================
    def _build_romantic_page(self):
        self.romantic_page = QWidget()
        layout = QVBoxLayout(self.romantic_page)

        btn_back = QPushButton("← Volver")
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        self.lbl_categoria_romantica = QLabel("❤️  Pareja")
        self.lbl_categoria_romantica.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_categoria_romantica.setStyleSheet("""
            background:#134f53; color:white; padding:8px;
            border-radius:15px; font-size:16px; font-weight:bold;
        """)

        titulo = QLabel("¿Qué tipo de escapada\nromántica prefieren?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:16px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_romantica = QPushButton("🌴\n\nEscapada\nromántica")
        btn_aventura  = QPushButton("🏕️\n\nAventura\njuntos")
        btn_relax     = QPushButton("🌊\n\nRelax y\nbienestar")
        btn_ciudad    = QPushButton("🌆\n\nCiudad y\nencanto")

        fila = QHBoxLayout()
        for b in [btn_romantica, btn_aventura, btn_relax, btn_ciudad]:
            b.setFixedSize(150, 170)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            fila.addWidget(b)

        btn_romantica.clicked.connect(lambda: self._ir_a_presupuesto('Escapada romántica'))
        btn_aventura.clicked.connect( lambda: self._ir_a_presupuesto('Aventura juntos'))
        btn_relax.clicked.connect(    lambda: self._ir_a_presupuesto('Relax y bienestar'))
        btn_ciudad.clicked.connect(   lambda: self._ir_a_presupuesto('Ciudad y encanto'))

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_categoria_romantica)
        layout.addSpacing(25)
        layout.addWidget(titulo)
        layout.addSpacing(35)
        layout.addLayout(fila)
        layout.addStretch()

        self.stack.addWidget(self.romantic_page)

    # ================= PANTALLA 3: PRESUPUESTO =================
    def _build_budget_page(self):
        self.budget_page = QWidget()
        layout = QVBoxLayout(self.budget_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.romantic_page))

        _tag_style = "background:#134f53; color:white; padding:8px; border-radius:15px; font-size:16px; font-weight:bold;"

        self.tag_budget_viaje   = QLabel("❤️  Pareja")
        self.tag_budget_escapada = QLabel("✨  Escapada romántica")
        for t in [self.tag_budget_viaje, self.tag_budget_escapada]:
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setStyleSheet(_tag_style)

        titulo = QLabel("¿Qué presupuesto aproximado tienen?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:14px; font-size:18px; text-align:left; padding-left:20px; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_b1 = QPushButton("Menos de $5,000")
        btn_b2 = QPushButton("Entre $5,000 y $15,000")
        btn_b3 = QPushButton("Más de $15,000")

        for b in [btn_b1, btn_b2, btn_b3]:
            b.setFixedHeight(60)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)

        btn_b1.clicked.connect(lambda: self._ir_a_sentimiento('Menos de $5,000'))
        btn_b2.clicked.connect(lambda: self._ir_a_sentimiento('$5,000 - $15,000'))
        btn_b3.clicked.connect(lambda: self._ir_a_sentimiento('Más de $15,000'))

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        layout.addWidget(self.tag_budget_viaje)
        layout.addSpacing(10)
        layout.addWidget(self.tag_budget_escapada)
        layout.addSpacing(25)
        layout.addWidget(titulo)
        layout.addSpacing(30)
        for b in [btn_b1, btn_b2, btn_b3]:
            layout.addWidget(b)
            layout.addSpacing(12)
        layout.addStretch()

        self.stack.addWidget(self.budget_page)

    # ================= PANTALLA 4: ¿QUÉ TE GUSTARÍA SENTIR? =================
    def _build_feeling_page(self):
        self.feeling_page = QWidget()
        layout = QVBoxLayout(self.feeling_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.budget_page))

        _tag_style = "background:#134f53; color:white; padding:8px; border-radius:15px; font-size:14px; font-weight:bold;"

        self.tag_feeling_viaje      = QLabel("❤️  Pareja")
        self.tag_feeling_escapada   = QLabel("✨  Escapada romántica")
        self.tag_feeling_presupuesto = QLabel("💰  $5,000 - $15,000")
        for t in [self.tag_feeling_viaje, self.tag_feeling_escapada, self.tag_feeling_presupuesto]:
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setStyleSheet(_tag_style)

        titulo = QLabel("¿Qué te gustaría sentir\nen este viaje?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:15px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_relajacion = QPushButton("🌴\n\nRelajación")
        btn_naturaleza = QPushButton("🌲\n\nContacto\ncon la naturaleza")
        btn_aventura   = QPushButton("⛰️\n\nAventura")
        btn_cultura    = QPushButton("🏛️\n\nCultura e\nhistoria")
        btn_diversion  = QPushButton("🌃\n\nDiversión\nnocturna")

        fila = QHBoxLayout()
        for b in [btn_relajacion, btn_naturaleza, btn_aventura, btn_cultura, btn_diversion]:
            b.setFixedSize(135, 170)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            fila.addWidget(b)

        btn_relajacion.clicked.connect(lambda: self._ir_a_clima('Relajación'))
        btn_naturaleza.clicked.connect(lambda: self._ir_a_clima('Contacto con la naturaleza'))
        btn_aventura.clicked.connect(  lambda: self._ir_a_clima('Aventura'))
        btn_cultura.clicked.connect(   lambda: self._ir_a_clima('Cultura e historia'))
        btn_diversion.clicked.connect( lambda: self._ir_a_clima('Diversión nocturna'))

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        layout.addWidget(self.tag_feeling_viaje)
        layout.addSpacing(8)
        layout.addWidget(self.tag_feeling_escapada)
        layout.addSpacing(8)
        layout.addWidget(self.tag_feeling_presupuesto)
        layout.addSpacing(25)
        layout.addWidget(titulo)
        layout.addSpacing(30)
        layout.addLayout(fila)
        layout.addStretch()

        self.stack.addWidget(self.feeling_page)

    # ================= PANTALLA 5: CLIMA =================
    def _build_climate_page(self):
        self.climate_page = QWidget()
        layout = QVBoxLayout(self.climate_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.feeling_page))

        _tag_style = "background:#134f53; color:white; padding:8px; border-radius:15px; font-size:14px; font-weight:bold;"

        self.tag_clima_viaje       = QLabel("❤️  Pareja")
        self.tag_clima_escapada    = QLabel("✨  Escapada romántica")
        self.tag_clima_presupuesto = QLabel("💰  $5,000 - $15,000")
        self.tag_clima_sentimiento = QLabel("🌴  Relajación")
        for t in [self.tag_clima_viaje, self.tag_clima_escapada,
                  self.tag_clima_presupuesto, self.tag_clima_sentimiento]:
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setStyleSheet(_tag_style)

        titulo = QLabel("¿Qué clima prefieren?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:16px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_calido      = QPushButton("🏝️\n\nCálido")
        btn_templado    = QPushButton("🍂\n\nTemplado")
        btn_frio        = QPushButton("❄️\n\nFrío")
        btn_indiferente = QPushButton("☁️\n\nNo importa")

        fila = QHBoxLayout()
        for b in [btn_calido, btn_templado, btn_frio, btn_indiferente]:
            b.setFixedSize(150, 170)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            fila.addWidget(b)

        btn_calido.clicked.connect(     lambda: self._ir_a_duracion('Cálido'))
        btn_templado.clicked.connect(   lambda: self._ir_a_duracion('Templado'))
        btn_frio.clicked.connect(       lambda: self._ir_a_duracion('Frío'))
        btn_indiferente.clicked.connect(lambda: self._ir_a_duracion('No importa'))

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        layout.addWidget(self.tag_clima_viaje)
        layout.addSpacing(8)
        layout.addWidget(self.tag_clima_escapada)
        layout.addSpacing(8)
        layout.addWidget(self.tag_clima_presupuesto)
        layout.addSpacing(8)
        layout.addWidget(self.tag_clima_sentimiento)
        layout.addSpacing(25)
        layout.addWidget(titulo)
        layout.addSpacing(30)
        layout.addLayout(fila)
        layout.addStretch()

        self.stack.addWidget(self.climate_page)

    # ================= PANTALLA 6: DURACIÓN =================
    def _build_duration_page(self):
        self.duration_page = QWidget()
        layout = QVBoxLayout(self.duration_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.climate_page))

        _tag_style = "background:#134f53; color:white; padding:8px; border-radius:15px; font-size:14px; font-weight:bold;"

        self.tag_dur_viaje       = QLabel("❤️  Pareja")
        self.tag_dur_escapada    = QLabel("✨  Escapada romántica")
        self.tag_dur_presupuesto = QLabel("💰  $5,000 - $15,000")
        self.tag_dur_sentimiento = QLabel("🌴  Relajación")
        self.tag_dur_clima       = QLabel("🏝️  Cálido")
        for t in [self.tag_dur_viaje, self.tag_dur_escapada, self.tag_dur_presupuesto,
                  self.tag_dur_sentimiento, self.tag_dur_clima]:
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setStyleSheet(_tag_style)

        titulo = QLabel("¿Cuántos días planean viajar?")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:white; font-size:28px; font-weight:bold;")

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:16px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        btn_fin    = QPushButton("🗓️\n\nFin de semana\n(2 - 3 días)")
        btn_4dias  = QPushButton("📅\n\n4 a 7 días")
        btn_semana = QPushButton("🗓️\n\nMás de una\nsemana")

        fila = QHBoxLayout()
        for b in [btn_fin, btn_4dias, btn_semana]:
            b.setFixedSize(180, 170)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            fila.addWidget(b)

        btn_fin.clicked.connect(   lambda: self._ir_a_destinos('Fin de semana (2-3 días)'))
        btn_4dias.clicked.connect( lambda: self._ir_a_destinos('4 a 7 días'))
        btn_semana.clicked.connect(lambda: self._ir_a_destinos('Más de una semana'))

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        for t in [self.tag_dur_viaje, self.tag_dur_escapada, self.tag_dur_presupuesto,
                  self.tag_dur_sentimiento, self.tag_dur_clima]:
            layout.addWidget(t)
            layout.addSpacing(8)
        layout.addSpacing(25)
        layout.addWidget(titulo)
        layout.addSpacing(30)
        layout.addLayout(fila)
        layout.addStretch()

        self.stack.addWidget(self.duration_page)

    # ================= PANTALLA 7: DESTINOS =================
    def _build_destinos_page(self):
        self.destinos_page = QWidget()
        layout = QVBoxLayout(self.destinos_page)

        titulo = QLabel("🤖 ¡Tengo opciones perfectas para ustedes!")
        titulo.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        self.lbl_destinos_sub = QLabel("Basadas en sus preferencias encontré\nestos destinos ideales.")
        self.lbl_destinos_sub.setStyleSheet("color:#cdd6f4; font-size:15px;")
        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_destinos_sub)
        layout.addSpacing(25)

        # Contenedor dinámico — se puebla al completar el flujo conversacional
        self.destinos_cards_widget = QWidget()
        self.destinos_cards_layout = QHBoxLayout(self.destinos_cards_widget)
        self.destinos_cards_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.destinos_cards_widget)
        layout.addSpacing(30)

        btn_ver_mas = QPushButton("Ver más destinos   →")
        btn_ver_mas.setFixedSize(300, 55)
        btn_ver_mas.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ver_mas.setStyleSheet("""
            QPushButton { background:#11c5c6; color:white; border:none;
                          border-radius:25px; font-size:18px; font-weight:bold; }
            QPushButton:hover { background:#19d8d9; }
        """)
        btn_ver_mas.clicked.connect(lambda: self.stack.setCurrentWidget(self.saved_page))
        layout.addWidget(btn_ver_mas, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.stack.addWidget(self.destinos_page)

    # ================= MÉTODO AUXILIAR: IR A DETALLE =================
    def _ir_a_detalle(self, key: str):
        self.destino = key
        d = DESTINOS_DATA[key]

        self.lbl_detalle_titulo.setText(d["nombre"])
        self.lbl_detalle_estado.setText(d["estado"])
        self.lbl_detalle_rating.setText(d["rating"])
        self.lbl_detalle_precio.setText(d["precio"])
        self.lbl_detalle_desc.setText(d["descripcion"])
        self.frame_se.hide()  # Nav. directa: no hay inferencia que mostrar

        tag_textos = d["tags"]
        for i, btn in enumerate(self.btns_detalle_tags):
            if i < len(tag_textos):
                btn.setText(tag_textos[i])
                btn.show()
            else:
                btn.hide()

        self._cargar_plan(key)
        self.stack.setCurrentWidget(self.detalle_page)

    def _ir_a_detalle_rec(self, rec):
        """Navega al detalle usando un objeto Recommendation del motor de inferencia."""
        self.recomendacion_actual = rec
        dest = rec.destination

        # Verificar si el destino tiene datos enriquecidos en DESTINOS_DATA
        key_map = {
            "Bacalar":         "bacalar",
            "Holbox":          "holbox",
            "Puerto Vallarta": "vallarta",
        }
        dest_key = key_map.get(dest.name)

        if dest_key and dest_key in DESTINOS_DATA:
            # Usar los datos enriquecidos del diccionario local
            self.destino = dest_key
            d = DESTINOS_DATA[dest_key]
            self.lbl_detalle_titulo.setText(d["nombre"])
            self.lbl_detalle_estado.setText(d["estado"])
            self.lbl_detalle_rating.setText(d["rating"])
            self.lbl_detalle_precio.setText(d["precio"])
            self.lbl_detalle_desc.setText(d["descripcion"])
            tag_textos = d["tags"]
            self._cargar_plan(dest_key)
            # Mostrar explicación si el motor la generó
            if rec.explanation:
                self.lbl_se_texto.setText(rec.explanation)
                self.frame_se.show()
            else:
                self.frame_se.hide()
        else:
            # Usar directamente los datos del dominio
            self.destino = "__dominio__"
            presupuesto_icons = {"Bajo": "💚", "Bajo-Medio": "💛", "Medio": "🟡", "Alto": "💜"}
            icono = presupuesto_icons.get(dest.budget, "💰")
            self.lbl_detalle_titulo.setText(dest.name)
            self.lbl_detalle_estado.setText(f"Presupuesto: {icono}  {dest.budget}")
            self.lbl_detalle_rating.setText(
                f"Compatibilidad: {rec.score:.1f} pts  |  "
                f"{len(rec.matched_tags)} factores coincidentes"
            )
            self.lbl_detalle_precio.setText("🎯 Recomendado especialmente para ti")
            self.lbl_detalle_desc.setText(dest.description)
            tag_textos = [f"#{t}" for t in dest.tags[:4]]
            self._cargar_plan_generico(rec)
            # Siempre mostrar explicación para destinos del dominio
            self.lbl_se_texto.setText(rec.explanation)
            self.frame_se.show()

        for i, btn in enumerate(self.btns_detalle_tags):
            if i < len(tag_textos):
                btn.setText(tag_textos[i])
                btn.show()
            else:
                btn.hide()

        self.stack.setCurrentWidget(self.detalle_page)

    def _cargar_plan_generico(self, rec):
        """Genera un plan sugerido basado en los datos de una Recommendation del dominio."""
        dest = rec.destination
        self.lbl_plan_titulo.setText(dest.name)
        self.lbl_plan_dias.setText("Plan sugerido por el Sistema Experto")

        # Limpiar los 3 contenedores de plan
        for widget in [self.plan_contenido_itinerario,
                       self.plan_contenido_incluye,
                       self.plan_contenido_opcionales]:
            while widget.layout().count():
                item = widget.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        def _item(widget, badge_txt, desc_txt):
            fila = QHBoxLayout()
            badge = QLabel(badge_txt)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedSize(65, 35)
            badge.setStyleSheet(
                "background:#0b6f73; color:white; border:1px solid #11c5c6; "
                "border-radius:17px; font-size:13px; font-weight:bold;"
            )
            desc = QLabel(desc_txt)
            desc.setStyleSheet("color:white; font-size:14px;")
            desc.setWordWrap(True)
            fila.addWidget(badge)
            fila.addSpacing(10)
            fila.addWidget(desc)
            fila.addStretch()
            card = QWidget()
            card.setLayout(fila)
            card.setStyleSheet(
                "QWidget { background:#24363b; border:1px solid #35585f; border-radius:12px; }"
            )
            card.setMinimumHeight(55)
            widget.layout().addWidget(card)
            widget.layout().addSpacing(8)

        # Itinerario — explicación del motor experto
        explicacion_corta = rec.explanation[:130] + "..." if len(rec.explanation) > 130 else rec.explanation
        _item(self.plan_contenido_itinerario, "🧠", explicacion_corta)
        for tag in rec.matched_tags[:3]:
            _item(self.plan_contenido_itinerario, "✅", f"Coincide con tu preferencia: '{tag}'")

        # Incluye — características del destino
        for tag in dest.tags:
            _item(self.plan_contenido_incluye, "🏷️", f"Característica: {tag}")

        # Opcionales — sugerencias genéricas
        for badge, texto in [
            ("➕", "Investigar actividades locales disponibles"),
            ("➕", "Comparar opciones de hospedaje según presupuesto"),
            ("➕", "Revisar temporada y clima antes de reservar"),
        ]:
            _item(self.plan_contenido_opcionales, badge, texto)

    # ================= PANTALLA 8: DETALLE DESTINO =================
    def _build_detalle_page(self):
        self.detalle_page = QWidget()
        layout = QVBoxLayout(self.detalle_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.destinos_page))

        self.lbl_detalle_titulo  = QLabel("Bacalar")
        self.lbl_detalle_titulo.setStyleSheet("color:white; font-size:34px; font-weight:bold;")
        self.lbl_detalle_estado  = QLabel("Quintana Roo")
        self.lbl_detalle_estado.setStyleSheet("color:#cdd6f4; font-size:18px;")
        self.lbl_detalle_rating  = QLabel("⭐ 4.8  (1,250 reseñas)")
        self.lbl_detalle_rating.setStyleSheet("color:#ffd43b; font-size:14px; font-weight:bold;")
        self.lbl_detalle_precio  = QLabel("Desde $8,200 por persona")
        self.lbl_detalle_precio.setStyleSheet("color:white; font-size:22px; font-weight:bold;")
        self.lbl_detalle_desc    = QLabel("")
        self.lbl_detalle_desc.setStyleSheet("color:#d0d0d0; font-size:16px;")
        self.lbl_detalle_desc.setWordWrap(True)

        # Panel de Explicación del Sistema Experto (visible solo con resultados del motor)
        self.frame_se = QWidget()
        self.frame_se.setStyleSheet(
            "QWidget { background:#1e1e2e; border-left:3px solid #cba6f7; "
            "border-radius:6px; padding:8px; }"
        )
        frame_se_layout = QVBoxLayout(self.frame_se)
        frame_se_layout.setContentsMargins(12, 8, 8, 8)
        frame_se_layout.setSpacing(4)
        lbl_se_titulo = QLabel("🧠  ¿Por qué te recomendamos este destino?")
        lbl_se_titulo.setStyleSheet("color:#cba6f7; font-size:13px; font-weight:bold; background:transparent; border:none;")
        self.lbl_se_texto = QLabel("")
        self.lbl_se_texto.setStyleSheet("color:#bac2de; font-size:13px; font-style:italic; background:transparent; border:none;")
        self.lbl_se_texto.setWordWrap(True)
        frame_se_layout.addWidget(lbl_se_titulo)
        frame_se_layout.addWidget(self.lbl_se_texto)
        self.frame_se.hide()  # Oculto por defecto

        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(15)
        layout.addWidget(self.lbl_detalle_titulo)
        layout.addWidget(self.lbl_detalle_estado)
        layout.addSpacing(8)
        layout.addWidget(self.lbl_detalle_rating)
        layout.addSpacing(12)
        layout.addWidget(self.lbl_detalle_precio)
        layout.addSpacing(12)
        layout.addWidget(self.lbl_detalle_desc)
        layout.addSpacing(10)
        layout.addWidget(self.frame_se)
        layout.addSpacing(20)

        _btn_style = """
            QPushButton { background:#2b2d42; color:white; border:1px solid #11c5c6;
                          border-radius:18px; font-size:13px; font-weight:bold; }
            QPushButton:hover { background:#11c5c6; }
        """
        fila_tags = QHBoxLayout()
        self.btns_detalle_tags = []
        for _ in range(4):
            b = QPushButton("")
            b.setFixedSize(100, 90)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            fila_tags.addWidget(b)
            self.btns_detalle_tags.append(b)
        layout.addLayout(fila_tags)
        layout.addSpacing(35)

        btn_plan = QPushButton("Ver plan sugerido      →")
        btn_plan.setFixedHeight(55)
        btn_plan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_plan.setStyleSheet("""
            QPushButton { background:#11c5c6; color:white; border:none;
                          border-radius:25px; font-size:18px; font-weight:bold; }
            QPushButton:hover { background:#19d8d9; }
        """)

        def redirigir_a_plan():
            if self.destino == "holbox":
                self.stack.setCurrentWidget(self.plan_holbox_page)
            elif self.destino == "vallarta":
                self.stack.setCurrentWidget(self.plan_vallarta_page)
            else:
                self.stack.setCurrentWidget(self.plan_page)

        btn_plan.clicked.connect(redirigir_a_plan)
        layout.addWidget(btn_plan)
        layout.addStretch()

        self.stack.addWidget(self.detalle_page)

    # ================= MÉTODO AUXILIAR: CARGAR PLAN =================
    def _cargar_plan(self, key: str):
        d = DESTINOS_DATA[key]
        
        if key == "holbox":
            self.lbl_plan_holbox_titulo.setText(d["plan_titulo"])
            self.lbl_plan_holbox_dias.setText(d["plan_dias"])
            secciones = [
                (self.plan_holbox_contenido_itinerario, d["itinerario"]),
                (self.plan_holbox_contenido_incluye,    d["incluye"]),
                (self.plan_holbox_contenido_opcionales, d["opcionales"]),
            ]
        elif key == "vallarta":
            self.lbl_plan_vallarta_titulo.setText(d["plan_titulo"])
            self.lbl_plan_vallarta_dias.setText(d["plan_dias"])
            secciones = [
                (self.plan_vallarta_contenido_itinerario, d["itinerario"]),
                (self.plan_vallarta_contenido_incluye,    d["incluye"]),
                (self.plan_vallarta_contenido_opcionales, d["opcionales"]),
            ]
        else:
            self.lbl_plan_titulo.setText(d["plan_titulo"])
            self.lbl_plan_dias.setText(d["plan_dias"])
            secciones = [
                (self.plan_contenido_itinerario, d["itinerario"]),
                (self.plan_contenido_incluye,    d["incluye"]),
                (self.plan_contenido_opcionales, d["opcionales"]),
            ]

        for widget, items in secciones:
            while widget.layout().count():
                item = widget.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            for badge_txt, desc_txt in items:
                fila = QHBoxLayout()
                badge = QLabel(badge_txt)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setFixedSize(65, 35)
                badge.setStyleSheet(
                    "background:#0b6f73; color:white; border:1px solid #11c5c6; "
                    "border-radius:17px; font-size:14px; font-weight:bold;"
                )
                desc = QLabel(desc_txt)
                desc.setStyleSheet("color:white; font-size:15px;")
                fila.addWidget(badge)
                fila.addSpacing(10)
                fila.addWidget(desc)
                fila.addStretch()

                card = QWidget()
                card.setLayout(fila)
                card.setStyleSheet(
                    "QWidget { background:#24363b; border:1px solid #35585f; border-radius:12px; }"
                )
                card.setFixedHeight(55)
                widget.layout().addWidget(card)
                widget.layout().addSpacing(8)

    # ================= PANTALLA 9: PLAN SUGERIDO =================
    def _build_plan_page(self):
        self.plan_page = QWidget()
        layout = QVBoxLayout(self.plan_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.detalle_page))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)

        self.lbl_plan_titulo = QLabel("Bacalar, Quintana Roo")
        self.lbl_plan_titulo.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        self.lbl_plan_dias = QLabel("4 a 7 días")
        self.lbl_plan_dias.setStyleSheet("color:#cdd6f4; font-size:15px;")
        layout.addWidget(self.lbl_plan_titulo)
        layout.addWidget(self.lbl_plan_dias)
        layout.addSpacing(25)

        _tab_style_activo = """
            QPushButton { background:#11c5c6; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
        """
        _tab_style_normal = """
            QPushButton { background:#1f3d42; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
            QPushButton:hover { background:#11c5c6; }
        """
        self.btn_tab_itinerario = QPushButton("Itinerario")
        self.btn_tab_incluye    = QPushButton("Incluye")
        self.btn_tab_opcionales = QPushButton("Opcionales")

        tabs_btns = [self.btn_tab_itinerario, self.btn_tab_incluye, self.btn_tab_opcionales]
        for b in tabs_btns:
            b.setFixedHeight(42)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_tab_style_normal)

        self.btn_tab_itinerario.setStyleSheet(_tab_style_activo)

        def cambiar_tab(indice):
            self.plan_stack.setCurrentIndex(indice)
            for i, b in enumerate(tabs_btns):
                b.setStyleSheet(_tab_style_activo if i == indice else _tab_style_normal)

        self.btn_tab_itinerario.clicked.connect(lambda: cambiar_tab(0))
        self.btn_tab_incluye.clicked.connect(   lambda: cambiar_tab(1))
        self.btn_tab_opcionales.clicked.connect(lambda: cambiar_tab(2))

        tabs_layout = QHBoxLayout()
        for b in tabs_btns:
            tabs_layout.addWidget(b)
        layout.addLayout(tabs_layout)
        layout.addSpacing(20)

        self.plan_stack = QStackedWidget()
        self.plan_contenido_itinerario = QWidget()
        self.plan_contenido_itinerario.setLayout(QVBoxLayout())
        self.plan_contenido_incluye    = QWidget()
        self.plan_contenido_incluye.setLayout(QVBoxLayout())
        self.plan_contenido_opcionales = QWidget()
        self.plan_contenido_opcionales.setLayout(QVBoxLayout())

        self.plan_stack.addWidget(self.plan_contenido_itinerario)
        self.plan_stack.addWidget(self.plan_contenido_incluye)
        self.plan_stack.addWidget(self.plan_contenido_opcionales)
        self.plan_stack.setCurrentIndex(0)
        layout.addWidget(self.plan_stack)

        nota = QLabel("Plan personalizable según tus intereses.")
        nota.setStyleSheet("background:#24363b; color:#cdd6f4; padding:14px; border-radius:12px; font-size:15px;")
        layout.addSpacing(15)
        layout.addWidget(nota)
        layout.addStretch()

        self.stack.addWidget(self.plan_page)

    # ================= PANTALLA: PLAN SUGERIDO - HOLBOX =================
    def _build_plan_holbox_page(self):
        self.plan_holbox_page = QWidget()
        layout = QVBoxLayout(self.plan_holbox_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.detalle_page))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)

        self.lbl_plan_holbox_titulo = QLabel("Holbox, Quintana Roo")
        self.lbl_plan_holbox_titulo.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        self.lbl_plan_holbox_dias = QLabel("4 a 7 días")
        self.lbl_plan_holbox_dias.setStyleSheet("color:#cdd6f4; font-size:15px;")
        layout.addWidget(self.lbl_plan_holbox_titulo)
        layout.addWidget(self.lbl_plan_holbox_dias)
        layout.addSpacing(25)

        _tab_style_activo = """
            QPushButton { background:#11c5c6; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
        """
        _tab_style_normal = """
            QPushButton { background:#1f3d42; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
            QPushButton:hover { background:#11c5c6; }
        """
        self.btn_tab_holbox_itinerario = QPushButton("Itinerario")
        self.btn_tab_holbox_incluye    = QPushButton("Incluye")
        self.btn_tab_holbox_opcionales = QPushButton("Opcionales")

        tabs_btns = [self.btn_tab_holbox_itinerario, self.btn_tab_holbox_incluye, self.btn_tab_holbox_opcionales]
        for b in tabs_btns:
            b.setFixedHeight(42)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_tab_style_normal)

        self.btn_tab_holbox_itinerario.setStyleSheet(_tab_style_activo)

        def cambiar_tab_holbox(indice):
            self.plan_holbox_stack.setCurrentIndex(indice)
            for i, b in enumerate(tabs_btns):
                b.setStyleSheet(_tab_style_activo if i == indice else _tab_style_normal)

        self.btn_tab_holbox_itinerario.clicked.connect(lambda: cambiar_tab_holbox(0))
        self.btn_tab_holbox_incluye.clicked.connect(   lambda: cambiar_tab_holbox(1))
        self.btn_tab_holbox_opcionales.clicked.connect(lambda: cambiar_tab_holbox(2))

        tabs_layout = QHBoxLayout()
        for b in tabs_btns:
            tabs_layout.addWidget(b)
        layout.addLayout(tabs_layout)
        layout.addSpacing(20)

        self.plan_holbox_stack = QStackedWidget()
        self.plan_holbox_contenido_itinerario = QWidget()
        self.plan_holbox_contenido_itinerario.setLayout(QVBoxLayout())
        self.plan_holbox_contenido_incluye    = QWidget()
        self.plan_holbox_contenido_incluye.setLayout(QVBoxLayout())
        self.plan_holbox_contenido_opcionales = QWidget()
        self.plan_holbox_contenido_opcionales.setLayout(QVBoxLayout())

        self.plan_holbox_stack.addWidget(self.plan_holbox_contenido_itinerario)
        self.plan_holbox_stack.addWidget(self.plan_holbox_contenido_incluye)
        self.plan_holbox_stack.addWidget(self.plan_holbox_contenido_opcionales)
        self.plan_holbox_stack.setCurrentIndex(0)
        layout.addWidget(self.plan_holbox_stack)

        nota = QLabel("Plan personalizable según tus intereses.")
        nota.setStyleSheet("background:#24363b; color:#cdd6f4; padding:14px; border-radius:12px; font-size:15px;")
        layout.addSpacing(15)
        layout.addWidget(nota)
        layout.addStretch()

        self.stack.addWidget(self.plan_holbox_page)

    # ================= PANTALLA: PLAN SUGERIDO - PUERTO VALLARTA =================
    def _build_plan_vallarta_page(self):
        self.plan_vallarta_page = QWidget()
        layout = QVBoxLayout(self.plan_vallarta_page)

        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.detalle_page))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)

        self.lbl_plan_vallarta_titulo = QLabel("Puerto Vallarta, Jalisco")
        self.lbl_plan_vallarta_titulo.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        self.lbl_plan_vallarta_dias = QLabel("4 a 7 días")
        self.lbl_plan_vallarta_dias.setStyleSheet("color:#cdd6f4; font-size:15px;")
        layout.addWidget(self.lbl_plan_vallarta_titulo)
        layout.addWidget(self.lbl_plan_vallarta_dias)
        layout.addSpacing(25)

        _tab_style_activo = """
            QPushButton { background:#11c5c6; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
        """
        _tab_style_normal = """
            QPushButton { background:#1f3d42; color:white; border:1px solid #11c5c6;
                          border-radius:12px; font-size:15px; font-weight:bold;
                          padding-left:15px; padding-right:15px; }
            QPushButton:hover { background:#11c5c6; }
        """
        self.btn_tab_vallarta_itinerario = QPushButton("Itinerario")
        self.btn_tab_vallarta_incluye    = QPushButton("Incluye")
        self.btn_tab_vallarta_opcionales = QPushButton("Opcionales")

        tabs_btns = [self.btn_tab_vallarta_itinerario, self.btn_tab_vallarta_incluye, self.btn_tab_vallarta_opcionales]
        for b in tabs_btns:
            b.setFixedHeight(42)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_tab_style_normal)

        self.btn_tab_vallarta_itinerario.setStyleSheet(_tab_style_activo)

        def cambiar_tab_vallarta(indice):
            self.plan_vallarta_stack.setCurrentIndex(indice)
            for i, b in enumerate(tabs_btns):
                b.setStyleSheet(_tab_style_activo if i == indice else _tab_style_normal)

        self.btn_tab_vallarta_itinerario.clicked.connect(lambda: cambiar_tab_vallarta(0))
        self.btn_tab_vallarta_incluye.clicked.connect(   lambda: cambiar_tab_vallarta(1))
        self.btn_tab_vallarta_opcionales.clicked.connect(lambda: cambiar_tab_vallarta(2))

        tabs_layout = QHBoxLayout()
        for b in tabs_btns:
            tabs_layout.addWidget(b)
        layout.addLayout(tabs_layout)
        layout.addSpacing(20)

        self.plan_vallarta_stack = QStackedWidget()
        self.plan_vallarta_contenido_itinerario = QWidget()
        self.plan_vallarta_contenido_itinerario.setLayout(QVBoxLayout())
        self.plan_vallarta_contenido_incluye    = QWidget()
        self.plan_vallarta_contenido_incluye.setLayout(QVBoxLayout())
        self.plan_vallarta_contenido_opcionales = QWidget()
        self.plan_vallarta_contenido_opcionales.setLayout(QVBoxLayout())

        self.plan_vallarta_stack.addWidget(self.plan_vallarta_contenido_itinerario)
        self.plan_vallarta_stack.addWidget(self.plan_vallarta_contenido_incluye)
        self.plan_vallarta_stack.addWidget(self.plan_vallarta_contenido_opcionales)
        self.plan_vallarta_stack.setCurrentIndex(0)
        layout.addWidget(self.plan_vallarta_stack)

        nota = QLabel("Plan personalizable según tus intereses.")
        nota.setStyleSheet("background:#24363b; color:#cdd6f4; padding:14px; border-radius:12px; font-size:15px;")
        layout.addSpacing(15)
        layout.addWidget(nota)
        layout.addStretch()

        self.stack.addWidget(self.plan_vallarta_page)

    # ================= PANTALLA 10: GUARDADOS =================
    def _build_saved_page(self):
        self.saved_page = QWidget()
        layout = QVBoxLayout(self.saved_page)

        titulo = QLabel("Guardados")
        titulo.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        layout.addWidget(titulo)
        layout.addSpacing(20)

        tarjetas = [
            ("🏝️", "Bacalar",                "4 a 7 días  •  $8,200 por persona", "Guardado el 20 may 2025", "♥"),
            ("🏛️", "San Miguel de Allende",  "3 a 4 días  •  $7,900 por persona", "Guardado el 18 may 2025", "♡"),
            ("🌴", "Tulum",                   "4 a 6 días  •  $9,400 por persona", "Guardado el 15 may 2025", "♡"),
        ]
        for emoji, nombre, detalle, fecha, fav_icon in tarjetas:
            card = QWidget()
            card.setFixedHeight(95)
            card.setStyleSheet("QWidget { background:#24363b; border:1px solid #35585f; border-radius:14px; }")
            fila = QHBoxLayout(card)

            img = QLabel(emoji)
            img.setFixedSize(70, 70)
            img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img.setStyleSheet("background:#1b262c; border-radius:10px; font-size:32px;")

            info = QVBoxLayout()
            lbl_nombre = QLabel(nombre)
            lbl_nombre.setStyleSheet("color:white; font-size:18px; font-weight:bold;")
            lbl_detalle = QLabel(detalle)
            lbl_detalle.setStyleSheet("color:#cdd6f4; font-size:13px;")
            lbl_fecha = QLabel(fecha)
            lbl_fecha.setStyleSheet("color:#8b949e; font-size:12px;")
            info.addWidget(lbl_nombre)
            info.addWidget(lbl_detalle)
            info.addWidget(lbl_fecha)

            btn_fav = QPushButton(fav_icon)
            btn_fav.setFixedSize(45, 45)
            btn_fav.setStyleSheet("QPushButton { background:transparent; color:white; border:none; font-size:24px; }")

            fila.addWidget(img)
            fila.addLayout(info)
            fila.addStretch()
            fila.addWidget(btn_fav)

            layout.addWidget(card)
            layout.addSpacing(12)

        layout.addStretch()
        layout.addLayout(self._build_bottom_menu())
        self.stack.addWidget(self.saved_page)

    # ================= PANTALLA 11: PERFIL =================
    def _build_profile_page(self):
        self.profile_page = QWidget()
        layout = QVBoxLayout(self.profile_page)

        fila_top = QHBoxLayout()
        btn_back = QPushButton("← Volver")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("QPushButton { background:transparent; color:#5ce1e6; border:none; font-size:15px; }")
        btn_back.clicked.connect(lambda: self.stack.setCurrentWidget(self.saved_page))
        titulo_profile = QLabel("Perfil y Preferencias")
        titulo_profile.setStyleSheet("color:white; font-size:22px; font-weight:bold;")
        fila_top.addWidget(btn_back)
        fila_top.addSpacing(10)
        fila_top.addWidget(titulo_profile)
        fila_top.addStretch()
        layout.addLayout(fila_top)
        layout.addSpacing(20)

        fila_user = QHBoxLayout()
        avatar = QLabel("👩")
        avatar.setFixedSize(70, 70)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("background:#24363b; border-radius:35px; font-size:34px;")
        datos = QVBoxLayout()
        QLabel_nombre = QLabel("María Fernanda")
        QLabel_nombre.setStyleSheet("color:white; font-size:24px; font-weight:bold;")
        QLabel_correo = QLabel("mariaf@gmail.com")
        QLabel_correo.setStyleSheet("color:#cdd6f4; font-size:14px;")
        datos.addWidget(QLabel_nombre)
        datos.addWidget(QLabel_correo)
        editar = QPushButton("Editar perfil   ✎")
        editar.setCursor(Qt.CursorShape.PointingHandCursor)
        editar.setStyleSheet("QPushButton { background:transparent; color:white; border:none; font-size:14px; }")
        fila_user.addWidget(avatar)
        fila_user.addSpacing(12)
        fila_user.addLayout(datos)
        fila_user.addStretch()
        fila_user.addWidget(editar)
        layout.addLayout(fila_user)
        layout.addSpacing(30)

        lbl_pref = QLabel("Mis preferencias")
        lbl_pref.setStyleSheet("color:white; font-size:18px; font-weight:bold;")
        layout.addWidget(lbl_pref)
        layout.addSpacing(15)

        for titulo_pref, valor in [
            ("🪙  Presupuesto",      "$5,000 - $15,000"),
            ("🧳  Tipo de viaje",    "Relajación"),
            ("☀️  Clima preferido",  "Cálido"),
            ("📅  Duración preferida", "4 a 7 días"),
        ]:
            fila = QHBoxLayout()
            izq = QLabel(titulo_pref)
            izq.setStyleSheet("color:white; font-size:15px; font-weight:bold;")
            der = QLabel(valor)
            der.setStyleSheet("color:#cdd6f4; font-size:15px;")
            flecha = QLabel("❯")
            flecha.setStyleSheet("color:#888; font-size:16px;")
            fila.addWidget(izq)
            fila.addStretch()
            fila.addWidget(der)
            fila.addSpacing(10)
            fila.addWidget(flecha)
            card = QWidget()
            card.setLayout(fila)
            card.setFixedHeight(55)
            card.setStyleSheet("QWidget { background:#24363b; border:1px solid #35585f; border-radius:12px; }")
            layout.addWidget(card)
            layout.addSpacing(8)

        layout.addStretch()
        layout.addLayout(self._build_bottom_menu())
        self.stack.addWidget(self.profile_page)

    # ================= PANTALLA 12: FORMULARIO EXPERTO =================
    def _build_main_page(self):
        main_page = QWidget()
        main_layout = QHBoxLayout(main_page)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("Vacation Expert")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Descubre tu destino ideal según tu estado de ánimo.")
        subtitle_label.setObjectName("subtitleLabel")
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)

        mood_label = QLabel("¿Cuál es tu estado de ánimo actual?")
        mood_label.setObjectName("sectionLabel")
        self.mood_combo = QComboBox()
        for m in Mood:
            self.mood_combo.addItem(m.value.capitalize(), m.value)
        left_layout.addWidget(mood_label)
        left_layout.addWidget(self.mood_combo)
        left_layout.addSpacing(15)

        duration_label = QLabel("¿De cuánto tiempo dispones?")
        duration_label.setObjectName("sectionLabel")
        self.duration_combo = QComboBox()
        for d in TimeDuration:
            self.duration_combo.addItem(d.value.replace("_", " ").capitalize(), d.value)
        left_layout.addWidget(duration_label)
        left_layout.addWidget(self.duration_combo)

        self.btn_recommend = QPushButton("Buscar Destinos Perfectos")
        self.btn_recommend.setObjectName("recommendButton")
        self.btn_recommend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recommend.clicked.connect(self.on_recommend_clicked)
        left_layout.addWidget(self.btn_recommend)

        main_layout.addWidget(left_panel, stretch=1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        results_title = QLabel("Recomendaciones sugeridas:")
        results_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f5c2e7;")
        right_layout.addWidget(results_title)

        self.results_browser = QTextBrowser()
        self.results_browser.setObjectName("resultsBrowser")
        self.results_browser.setOpenExternalLinks(True)
        self.mostrar_bienvenida()
        right_layout.addWidget(self.results_browser)

        main_layout.addWidget(right_panel, stretch=2)
        self.stack.addWidget(main_page)

    # ================= MENÚ INFERIOR COMPARTIDO =================
    def _build_bottom_menu(self):
        menu = QHBoxLayout()
        _btn_style = """
            QPushButton { background:transparent; color:white; border:none;
                          font-size:14px; font-weight:bold; }
            QPushButton:hover { color:#11c5c6; }
        """
        btn_explorar  = QPushButton("🔍\nExplorar")
        btn_guardados = QPushButton("♥\nGuardados")
        btn_viajes    = QPushButton("🧳\nMis viajes")
        btn_perfil    = QPushButton("👤\nPerfil")

        for b in [btn_explorar, btn_guardados, btn_viajes, btn_perfil]:
            b.setFixedHeight(60)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_btn_style)
            menu.addWidget(b)

        btn_explorar.clicked.connect( lambda: self.stack.setCurrentWidget(self.destinos_page))
        btn_guardados.clicked.connect(lambda: self.stack.setCurrentWidget(self.saved_page))
        btn_viajes.clicked.connect(   lambda: self.stack.setCurrentWidget(self.plan_page))
        btn_perfil.clicked.connect(   lambda: self.stack.setCurrentWidget(self.profile_page))

        return menu

    # ------------------------------------------------------------------
    # LÓGICA DEL SISTEMA EXPERTO
    # ------------------------------------------------------------------

    def mostrar_bienvenida(self):
        html = """
        <div style='color: #a6adc8; font-family: sans-serif; font-size: 14px;
                    text-align: center; margin-top: 100px;'>
            <h2 style='color: #89b4fa;'>¡Bienvenido a tu Asistente Experto de Vacaciones!</h2>
            <p>Selecciona tu estado de ánimo y tu tiempo disponible en el panel izquierdo y haz clic en</p>
            <p style='color: #f5c2e7; font-weight: bold;'>'Buscar Destinos Perfectos'</p>
            <p>para que nuestro motor de inferencia analice las mejores opciones para ti.</p>
        </div>
        """
        self.results_browser.setHtml(html)

    def on_recommend_clicked(self):
        mood_str     = self.mood_combo.currentData()
        duration_str = self.duration_combo.currentData()
        # La nueva API (Fase 4) espera un diccionario de hechos, no parámetros posicionales
        user_facts = {k: v for k, v in {"mood": mood_str, "duration": duration_str}.items() if v}
        try:
            recomendaciones = self._use_case.obtener_recomendacion(user_facts)
            self.render_recommendations(recomendaciones)
        except DomainError as err:
            QMessageBox.warning(self, "Error de Dominio", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un fallo inesperado: {err}")

    def render_recommendations(self, recommendations):
        if not recommendations:
            self.results_browser.setHtml(
                "<div style='color: #f38ba8; font-size: 16px; text-align: center; margin-top: 100px;'>"
                "<h3>No se encontraron modificaciones</h3>"
                "<p>Intenta variando tu combinación de estado de ánimo y tiempo disponible.</p>"
                "</div>"
            )
            return

        html_content = "<div style='font-family: sans-serif; color: #cdd6f4;'>"
        for idx, rec in enumerate(recommendations, 1):
            dest = rec.destination
            tags_html = "".join([
                f"<span style='background-color: #313244; color: #f5c2e7; padding: 3px 8px; "
                f"margin-right: 5px; border-radius: 4px; font-size: 11px;'>#{tag}</span>"
                for tag in dest.tags
            ])
            badge_color = "#a6e3a1" if rec.score >= 2.0 else "#f9e2af"
            html_content += f"""
            <div style='background-color: #181825; border: 1px solid #313244;
                        border-radius: 8px; padding: 15px; margin-bottom: 15px;'>
                <table width='100%' style='border-collapse: collapse;'>
                    <tr>
                        <td style='font-size: 18px; font-weight: bold; color: #89b4fa;'>
                            {idx}. {dest.name}
                        </td>
                        <td align='right'>
                            <span style='background-color: {badge_color}; color: #11111b;
                                         padding: 4px 10px; border-radius: 12px;
                                         font-weight: bold; font-size: 12px;'>
                                Score: {rec.score}
                            </span>
                        </td>
                    </tr>
                </table>
                <p style='margin: 8px 0; font-size: 13px; color: #cdd6f4;'>{dest.description}</p>
                <div style='margin: 5px 0 10px 0;'>
                    <span style='font-weight: bold; color: #a6adc8; font-size: 12px;'>Presupuesto:</span>
                    <span style='color: #f5c2e7; font-size: 12px; font-weight: bold;'>{dest.budget}</span>
                </div>
                <div style='margin-bottom: 12px;'>{tags_html}</div>
                <div style='background-color: #1e1e2e; border-left: 3px solid #cba6f7;
                             padding: 8px 12px; font-style: italic; font-size: 12px; color: #bac2de;'>
                    <strong>Explicación del Sistema Experto:</strong> {rec.explanation}
                </div>
            </div>
            """
        html_content += "</div>"
        self.results_browser.setHtml(html_content)