#!/usr/bin/env python3
"""
BarFlow - Entry point principale per l'applicazione packaggiata
"""
import sys
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Funzione principale dell'applicazione AccountFlow"""
    try:
        # Debug: stampa informazioni sull'ambiente di esecuzione
        import sys
        from pathlib import Path
        print(f"🚀 Avvio AccountFlow...")
        print(f"   - Python: {sys.version}")
        print(f"   - Eseguibile: {sys.executable}")
        print(f"   - Frozen: {getattr(sys, 'frozen', False)}")
        print(f"   - Working directory: {Path.cwd()}")
        
        # Inizializza il database prima di tutto
        from barflow.data.db_manager import initialize_and_migrate_db
        initialize_and_migrate_db()
        
        # Importa e avvia l'interfaccia grafica
        from PySide6.QtWidgets import QApplication
        from barflow.ui.main_window import MainWindow
        
        # Crea l'applicazione Qt
        app = QApplication(sys.argv)
        app.setApplicationName("AccountFlow")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AccountFlow Team")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()