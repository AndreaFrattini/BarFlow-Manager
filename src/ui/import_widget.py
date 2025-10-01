"""
Widget per l'importazione dei dati
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QMessageBox)
from PySide6.QtCore import Qt, Signal
from datetime import datetime
import random

class ImportWidget(QWidget):
    """Widget per la schermata di importazione dati."""
    
    data_imported = Signal(str, list)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title_label = QLabel("Seleziona la fonte dei dati da importare")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        btn_fornitori = QPushButton("Fornitori")
        btn_fornitori.setMinimumHeight(50)
        btn_fornitori.clicked.connect(lambda: self.import_data("Fornitore"))
        layout.addWidget(btn_fornitori)

        btn_pos = QPushButton("Point of Sales (POS)")
        btn_pos.setMinimumHeight(50)
        btn_pos.clicked.connect(lambda: self.import_data("POS"))
        layout.addWidget(btn_pos)

        btn_manuale = QPushButton("Manuale")
        btn_manuale.setMinimumHeight(50)
        btn_manuale.clicked.connect(lambda: self.import_data("Manuale"))
        layout.addWidget(btn_manuale)

    def import_data(self, source_type):
        """Simula l'importazione di dati e emette un segnale."""
        
        if source_type == "Manuale":
            QMessageBox.information(self, "Importazione Manuale", "Questa funzionalità non è ancora implementata.")
            return

        # Genera dati fittizi
        transactions = []
        num_records = random.randint(5, 15)
        
        for i in range(num_records):
            if source_type == "Fornitore":
                description = f"Fattura Fornitore {random.randint(100, 999)}"
                amount = -random.uniform(50.0, 500.0) # Uscite
            else: # POS
                description = f"Transazione POS {random.randint(1000, 9999)}"
                amount = random.uniform(5.0, 100.0) # Entrate

            transaction = {
                'transaction_date': datetime.now().strftime('%Y-%m-%d'),
                'description': description,
                'amount': f"{amount:.2f}"
            }
            transactions.append(transaction)
            
        self.data_imported.emit(source_type, transactions)