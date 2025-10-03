"""
Widget per l'importazione dei dati
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QInputDialog, QDialog, QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox, QDialogButtonBox
from PySide6.QtCore import Qt, Signal, QDate
import pandas as pd
import xml.etree.ElementTree as ET

class ManualInputDialog(QDialog):
    """Dialog per l'inserimento manuale di una transazione."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inserisci Dati Transazione")
        
        self.layout = QFormLayout(self)
        
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.product_edit = QLineEdit()
        self.supplier_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.quantity_edit = QDoubleSpinBox()
        self.quantity_edit.setRange(0, 10000)
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setRange(0, 1000000)
        self.price_edit.setDecimals(2)
        
        self.layout.addRow("Data:", self.date_edit)
        self.layout.addRow("Prodotto:", self.product_edit)
        self.layout.addRow("Fornitore:", self.supplier_edit)
        self.layout.addRow("Categoria:", self.category_edit)
        self.layout.addRow("Quantità:", self.quantity_edit)
        self.layout.addRow("Prezzo:", self.price_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """Restituisce i dati inseriti nel dialogo."""
        return {
            'DATA': self.date_edit.date().toString("yyyy-MM-dd"),
            'PRODOTTO': self.product_edit.text() or None,
            'FORNITORE': self.supplier_edit.text() or None,
            'CATEGORIA': self.category_edit.text() or None,
            'Quantità': self.quantity_edit.value() if self.quantity_edit.value() > 0 else None,
            'IMPORTO': self.price_edit.value()
        }

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
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: grey;")
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
        df = pd.read_excel(file_path, engine='openpyxl', sheet_name=0)
        transactions = []
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        for _, row in df.iterrows():
            prezzo_totale = float(row['quantita']) * float(row['costo_unita'])
            transaction = {
                'DATA': pd.to_datetime(row['data_ordine']).strftime('%Y-%m-%d'),
                'PRODOTTO': row.get('prodotto'),
                'FORNITORE': row.get('fornitore'),
                'CATEGORIA': row.get('categoria'),
                'QUANTITA\'': row.get('quantita'),
                'IMPORTO': f"{-prezzo_totale:.2f}"
            }
            transactions.append(transaction)
        return transactions

    def parse_pos_xlsx(self, file_path):
        """Esegue il parsing di un file XLSX di transazioni POS."""
        df = pd.read_excel(file_path)
        transactions = []
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        for _, row in df.iterrows():
            transaction = {
                'DATA': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                'PRODOTTO': row.get('product_name'),
                'FORNITORE': None,
                'CATEGORIA': None,
                'QUANTITA\'': row.get('quantity'),
                'IMPORTO': f"{float(row['total_amount']):.2f}"
            }
            transactions.append(transaction)
        return transactions

    def import_manuale(self):
        """Gestisce il caso dell'importazione manuale."""
        items = ["Aggiungi spesa", "Aggiungi guadagno"]
        item, ok = QInputDialog.getItem(self, "Seleziona Tipo", "Scegli il tipo di transazione:", items, 0, False)

        if ok and item:
            dialog = ManualInputDialog(self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                
                importo = data['IMPORTO']
                if item == "Aggiungi spesa":
                    importo = -abs(importo)

                transaction = {
                    'DATA': data['DATA'],
                    'PRODOTTO': data['PRODOTTO'],
                    'FORNITORE': data['FORNITORE'],
                    'CATEGORIA': data['CATEGORIA'],
                    'QUANTITA\'': data['Quantità'],
                    'IMPORTO': f"{importo:.2f}"
                }
                
                self.data_imported.emit("Manuale", [transaction])
                QMessageBox.information(self, "Importazione Riuscita", 
                                        "Record manuale aggiunto con successo.")