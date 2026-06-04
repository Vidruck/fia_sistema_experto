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
    QLabel, QComboBox, QPushButton, QTextBrowser, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from src.ports.inbound import RecommendationUseCase
from src.domain.models import Mood, TimeDuration
from src.domain.exceptions import DomainError

# Definimos la hoja de estilos QSS para dotar a la UI de un acabado oscuro y premium
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
QTextBrowser #resultsBrowser {
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
        """
        Constructor que recibe el puerto de entrada.
        
        :param use_case: Instancia de RecommendationUseCase.
        """
        super().__init__()
        self._use_case = use_case
        self.init_ui()

    def init_ui(self):
        """Inicializa todos los widgets y layouts de la interfaz."""
        self.setWindowTitle("Asistente Experto de Vacaciones")
        self.resize(950, 650)
        self.setMinimumSize(850, 550)
        
        # Aplicar la hoja de estilos personalizada
        self.setStyleSheet(QSS_STYLESHEET)

        # Widget central y layout general horizontal (dos columnas)
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)

        # ================= COLUMNA IZQUIERDA: FORMULARIO =================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Cabecera
        title_label = QLabel("Vacation Expert")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Descubre tu destino ideal según tu estado de ánimo.")
        subtitle_label.setObjectName("subtitleLabel")
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)

        # Selector 1: Estado de Ánimo
        mood_label = QLabel("¿Cuál es tu estado de ánimo actual?")
        mood_label.setObjectName("sectionLabel")
        self.mood_combo = QComboBox()
        for m in Mood:
            self.mood_combo.addItem(m.value.capitalize(), m.value)
        left_layout.addWidget(mood_label)
        left_layout.addWidget(self.mood_combo)
        left_layout.addSpacing(15)

        # Selector 2: Tiempo disponible
        duration_label = QLabel("¿De cuánto tiempo dispones?")
        duration_label.setObjectName("sectionLabel")
        self.duration_combo = QComboBox()
        for d in TimeDuration:
            label_text = d.value.replace("_", " ").capitalize()
            self.duration_combo.addItem(label_text, d.value)
        left_layout.addWidget(duration_label)
        left_layout.addWidget(self.duration_combo)

        # Botón de Procesar Recomendaciones
        self.btn_recommend = QPushButton("Buscar Destinos Perfectos")
        self.btn_recommend.setObjectName("recommendButton")
        self.btn_recommend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recommend.clicked.connect(self.on_recommend_clicked)
        left_layout.addWidget(self.btn_recommend)

        # Integrar columna izquierda al layout principal
        main_layout.addWidget(left_panel, stretch=1)

        # ================= COLUMNA DERECHA: RESULTADOS =================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        results_title = QLabel("Recomendaciones sugeridas:")
        results_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f5c2e7;")
        right_layout.addWidget(results_title)

        self.results_browser = QTextBrowser()
        self.results_browser.setObjectName("resultsBrowser")
        self.results_browser.setOpenExternalLinks(True)
        # HTML inicial de bienvenida
        self.mostrar_bienvenida()

        right_layout.addWidget(self.results_browser)
        main_layout.addWidget(right_panel, stretch=2)

    def mostrar_bienvenida(self):
        """Muestra un mensaje de bienvenida estructurado en la caja de texto."""
        html = """
        <div style='color: #a6adc8; font-family: sans-serif; font-size: 14px; text-align: center; margin-top: 100px;'>
            <h2 style='color: #89b4fa;'>¡Bienvenido a tu Asistente Experto de Vacaciones!</h2>
            <p>Selecciona tu estado de ánimo y tu tiempo disponible en el panel izquierdo y haz clic en</p>
            <p style='color: #f5c2e7; font-weight: bold;'>'Buscar Destinos Perfectos'</p>
            <p>para que nuestro motor de inferencia analice las mejores opciones para ti.</p>
        </div>
        """
        self.results_browser.setHtml(html)

    def on_recommend_clicked(self):
        """Manejador del evento clic en el botón de recomendación."""
        mood_str = self.mood_combo.currentData()
        duration_str = self.duration_combo.currentData()

        try:
            # Llamamos al caso de uso (puerto de entrada)
            recomendaciones = self._use_case.obtener_recomendacion(mood_str, duration_str)
            self.render_recommendations(recomendaciones)
        except DomainError as err:
            QMessageBox.warning(self, "Error de Dominio", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un fallo inesperado: {err}")

    def render_recommendations(self, recommendations):
        """Genera el código HTML para mostrar los resultados en el QTextBrowser."""
        if not recommendations:
            self.results_browser.setHtml(
                "<div style='color: #f38ba8; font-size: 16px; text-align: center; margin-top: 100px;'>"
                "<h3>No se encontraron coincidencias</h3>"
                "<p>Intenta variando tu combinación de estado de ánimo y tiempo disponible.</p>"
                "</div>"
            )
            return

        html_content = "<div style='font-family: sans-serif; color: #cdd6f4;'>"
        
        for idx, rec in enumerate(recommendations, 1):
            dest = rec.destination
            
            # Formateamos las etiquetas como pequeñas píldoras
            tags_html = "".join([
                f"<span style='background-color: #313244; color: #f5c2e7; padding: 3px 8px; "
                f"margin-right: 5px; border-radius: 4px; font-size: 11px;'>#{tag}</span>"
                for tag in dest.tags
            ])

            # Determinamos el color de la insignia según la puntuación
            badge_color = "#a6e3a1" if rec.score >= 2.0 else "#f9e2af"

            html_content += f"""
            <div style='background-color: #181825; border: 1px solid #313244; border-radius: 8px; padding: 15px; margin-bottom: 15px;'>
                <table width='100%' style='border-collapse: collapse;'>
                    <tr>
                        <td style='font-size: 18px; font-weight: bold; color: #89b4fa;'>{idx}. {dest.name}</td>
                        <td align='right'>
                            <span style='background-color: {badge_color}; color: #11111b; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px;'>
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
                <div style='margin-bottom: 12px;'>
                    {tags_html}
                </div>
                <div style='background-color: #1e1e2e; border-left: 3px solid #cba6f7; padding: 8px 12px; font-style: italic; font-size: 12px; color: #bac2de;'>
                    <strong>Explicación del Sistema Experto:</strong> {rec.explanation}
                </div>
            </div>
            """
        
        html_content += "</div>"
        self.results_browser.setHtml(html_content)
