#!/usr/bin/env python3
"""
BarFlow - Gestione Finanziaria per Bar
Applicazione desktop per la gestione centralizzata dei dati finanziari

Autore: BarFlow Team
Versione: 1.0.0
Data: 2025
"""

import sys
import os
from pathlib import Path

# Aggiungi il percorso src al PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """
    Funzione principale per avviare l'applicazione BarFlow
    """
    try:
        # Importa dopo aver impostato il path
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QDir
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
        
        # Applica tema scuro se disponibile
        try:
            import qdarktheme
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
        except ImportError:
            # Se qdarktheme non è disponibile, usa stile di base
            pass
        
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
        print("pip install PySide6 plotly pandas openpyxl xlsxwriter")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Errore nell'avvio dell'applicazione: {e}")
        sys.exit(1)


def check_dependencies():
    """
    Verifica che tutte le dipendenze necessarie siano installate
    """
    required_packages = [
        'PySide6',
        'plotly', 
        'pandas',
        'openpyxl',
        'xlsxwriter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Pacchetti mancanti rilevati:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalla i pacchetti mancanti con:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def create_sample_data():
    """
    Crea dati di esempio per testare l'applicazione
    """
    try:
        from database.database_manager import DatabaseManager
        from datetime import datetime, timedelta
        import random
        
        print("🔧 Creazione dati di esempio...")
        
        db = DatabaseManager()
        
        # Crea alcune transazioni di esempio
        sample_transactions = []
        
        # Categorie esistenti (Bevande=1, Cibo=2, Personale=3)
        categories = [1, 2, 3]
        
        # Genera transazioni per gli ultimi 30 giorni
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(50):  # 50 transazioni di esempio
            transaction_date = start_date + timedelta(days=random.randint(0, 30))
            
            # Alterna tra entrate e uscite
            is_income = random.choice([True, False])
            
            if is_income:
                # Entrate (vendite)
                descriptions = [
                    "Vendita bevande", "Vendita cibo", "Vendita aperitivi",
                    "Vendita pranzo", "Vendita cena", "Vendita colazione"
                ]
                amount = random.uniform(50, 500)
                category_id = random.choice([1, 2])  # Bevande o Cibo
            else:
                # Uscite
                descriptions = [
                    "Acquisto ingredienti", "Stipendio personale", "Affitto locale",
                    "Utenze", "Pulizie", "Manutenzione"
                ]
                amount = random.uniform(20, 300)
                category_id = random.choice(categories)
            
            sample_transactions.append({
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'description': random.choice(descriptions),
                'amount': round(amount, 2),
                'is_income': is_income,
                'category_id': category_id
            })
        
        # Aggiungi le transazioni al database
        count = db.add_transactions(sample_transactions)
        print(f"✅ Creati {count} esempi di transazioni")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione dati di esempio: {e}")
        return False


if __name__ == "__main__":
    # Verifica le dipendenze
    if not check_dependencies():
        sys.exit(1)
    
    # Opzione per creare dati di esempio
    if len(sys.argv) > 1 and sys.argv[1] == "--sample-data":
        if create_sample_data():
            print("✅ Dati di esempio creati. Avvia l'applicazione normalmente.")
        sys.exit(0)
    
    # Avvia l'applicazione
    main()