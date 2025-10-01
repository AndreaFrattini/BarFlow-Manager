"""
Widget per l'importazione dei dati
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                               QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt, Signal
import pandas as pd
import xml.etree.ElementTree as ET

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

        btn_fornitori = QPushButton("Ordini Fornitori (XLSM)")
        btn_fornitori.setMinimumHeight(50)
        btn_fornitori.clicked.connect(lambda: self.open_file_dialog("Fornitore"))
        layout.addWidget(btn_fornitori)

        btn_pos = QPushButton("Transazioni Point of Sales (POS - XLSX)")
        btn_pos.setMinimumHeight(50)
        btn_pos.clicked.connect(lambda: self.open_file_dialog("POS"))
        layout.addWidget(btn_pos)

        btn_manuale = QPushButton("Manuale")
        btn_manuale.setMinimumHeight(50)
        btn_manuale.clicked.connect(self.import_manuale)
        layout.addWidget(btn_manuale)

    def open_file_dialog(self, source_type):
        """Apre un QFileDialog per selezionare il file da importare."""
        file_filter = "Excel Files (*.xlsm)" if source_type == "Fornitore" else "Excel Files (*.xlsx)"
        file_path, _ = QFileDialog.getOpenFileName(self, f"Seleziona file {source_type}", "", file_filter)

        if file_path:
            self.import_data(source_type, file_path)

    def import_data(self, source_type, file_path):
        """Legge e processa i dati dal file selezionato."""
        try:
            if source_type == "Fornitore":
                transactions = self.parse_supplier_xlsm(file_path)
            elif source_type == "POS":
                transactions = self.parse_pos_xlsx(file_path)
            else:
                return

            self.data_imported.emit(source_type, transactions)
            QMessageBox.information(self, "Importazione Riuscita", 
                                    f"{len(transactions)} record importati con successo da {file_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Errore di Importazione", 
                                 f"Impossibile importare il file {file_path}.\n\nErrore: {e}")

    def parse_supplier_xlsm(self, file_path):
        """Esegue il parsing di un file XLSM di ordini fornitore."""
        df = pd.read_excel(file_path, engine='openpyxl')
        transactions = []
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        for _, row in df.iterrows():
            transaction = {
                'transaction_date': pd.to_datetime(row['data_ordine']).strftime('%Y-%m-%d'),
                'description': f"Acquisto: {row['descrizione_prodotto']}",
                'amount': f"{-float(row['costo_totale']):.2f}"  # Costo, quindi negativo
            }
            transactions.append(transaction)
        return transactions

    def parse_pos_xlsx(self, file_path):
        """Esegue il parsing di un file XLSX di transazioni POS."""
        df = pd.read_excel(file_path)
        transactions = []
        # Assicurati che le colonne abbiano i nomi corretti
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        for _, row in df.iterrows():
            transaction = {
                'transaction_date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                'description': f"Vendita: {row['product_name']}",
                'amount': f"{float(row['total_amount']):.2f}" # Vendita, quindi positivo
            }
            transactions.append(transaction)
        return transactions

    def import_manuale(self):
        """Gestisce il caso dell'importazione manuale."""
        QMessageBox.information(self, "Importazione Manuale", "Questa funzionalità non è ancora implementata.")
        return