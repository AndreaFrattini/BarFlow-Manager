#!/usr/bin/env python3
"""
BarFlow - Entry point principale per l'applicazione
"""
import sys
import logging
from pathlib import Path

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Funzione principale dell'applicazione BarFlow"""
    try:
        # Inizializza il database prima di tutto
        from barflow.data.db_manager import initialize_and_migrate_db
        initialize_and_migrate_db()
        
        # Importa e avvia l'interfaccia grafica
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from barflow.ui.main_window import MainWindow
        
        # Crea l'applicazione Qt
        app = QApplication(sys.argv)
        app.setApplicationName("BarFlow")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Andrea Frattini")
        app.setStyle("Fusion")
        
        # Crea e mostra la finestra principale
        window = MainWindow()
        
        # Centra la finestra
        screen = app.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = window.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            window.move(window_geometry.topLeft())
        
        window.show()
        
        print("🚀 BarFlow avviato con successo!")
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore nell'avvio: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()