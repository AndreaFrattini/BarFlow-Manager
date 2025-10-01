#!/usr/bin/env python3
"""
BarFlow - Gestione Finanziaria per Bar
Applicazione desktop per la gestione centralizzata dei dati finanziari

Autore: BarFlow Team
Versione: 1.0.0
Data: 2025
"""

import sys
from pathlib import Path

# Aggiungi il percorso src al PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """
    Funzione principale per avviare l'applicazione BarFlow.
    """
    try:
        # Importa dopo aver impostato il path
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        
        # Importa la finestra principale
        from ui.main_window import MainWindow
        
        # Crea l'applicazione Qt
        app = QApplication(sys.argv)
        
        # Configurazione dell'applicazione
        app.setApplicationName("BarFlow")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("BarFlow Solutions")
        app.setOrganizationDomain("barflow.com")
        
        # Imposta lo stile dell'applicazione
        app.setStyle("Fusion")
        
        # Crea e mostra la finestra principale
        window = MainWindow()
        
        # Centra la finestra sullo schermo
        screen = app.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = window.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            window.move(window_geometry.topLeft())
        
        # Mostra la finestra
        window.show()
        
        # Messaggio di benvenuto nella console
        print("=" * 60)
        print("🚀 BarFlow - Gestione Finanziaria per Bar")
        print("   Versione 1.0.0")
        print("   Applicazione avviata con successo!")
        print("=" * 60)
        
        # Avvia il loop principale dell'applicazione
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        print("\nAssicurati di aver installato tutte le dipendenze:")
        print("uv sync")
        print("\nOppure con pip tradizionale:")
        print("pip install PySide6 plotly pandas openpyxl xlsxwriter lxml")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Errore nell'avvio dell'applicazione: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Avvia l'applicazione
    main()