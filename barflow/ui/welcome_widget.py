"""
Widget di benvenuto per AccountFlow
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

class WelcomeWidget(QWidget):
    """Widget che mostra un messaggio di benvenuto e un logo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Inizializza l'interfaccia utente del widget"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Titolo
        title_label = QLabel("AccountFlow - Gestione Finanziaria")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #2C3E50;
                padding-bottom: 20px;
            }
        """)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Costruisci il percorso del logo in modo robusto
        # Partendo dal file corrente (__file__), vai alla directory barflow e poi a resources/logo
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # barflow/ui
        barflow_dir = os.path.dirname(current_file_dir)  # barflow
        logo_path = os.path.join(barflow_dir, 'resources', 'logo', 'logo.png')
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Riduci la dimensione del logo se necessario, mantenendo l'aspect ratio
            logo_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("Logo non trovato")
            logo_label.setStyleSheet("color: red; font-style: italic;")

        layout.addWidget(title_label)
        layout.addWidget(logo_label)
        
        self.setLayout(layout)
