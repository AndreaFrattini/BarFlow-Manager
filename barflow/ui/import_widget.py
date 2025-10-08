"""
Widget per l'importazione dei dati
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QInputDialog, QDialog, QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox, QDialogButtonBox, QDateTimeEdit
from PySide6.QtCore import Qt, Signal, QDate, QDateTime
import pandas as pd

class ManualInputDialog(QDialog):
    """Dialog per l'inserimento manuale di una transazione."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inserisci Dati Transazione")
        
        self.layout = QFormLayout(self)
        
        self.date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        
        self.supplier_edit = QLineEdit()
        self.supplier_number_edit = QLineEdit()
        self.pos_operation_edit = QLineEdit()
        self.pos_gross_amount_edit = QDoubleSpinBox()
        self.pos_gross_amount_edit.setRange(0, 1000000)
        self.pos_gross_amount_edit.setDecimals(2)
        self.pos_commission_edit = QDoubleSpinBox()
        self.pos_commission_edit.setRange(0, 1000000)
        self.pos_commission_edit.setDecimals(2)
        self.net_amount_edit = QDoubleSpinBox()
        self.net_amount_edit.setRange(-1000000, 1000000)
        self.net_amount_edit.setDecimals(2)
        
        self.layout.addRow("Data:", self.date_edit)
        self.layout.addRow("Fornitore:", self.supplier_edit)
        self.layout.addRow("Numero Fornitore:", self.supplier_number_edit)
        self.layout.addRow("Numero Operazione POS:", self.pos_operation_edit)
        self.layout.addRow("Importo Lordo POS:", self.pos_gross_amount_edit)
        self.layout.addRow("Commissione POS:", self.pos_commission_edit)
        self.layout.addRow("Importo Netto:", self.net_amount_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """Restituisce i dati inseriti nel dialogo."""
        return {
            'DATA': self.date_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
            'FORNITORE': self.supplier_edit.text() or None,
            'NUMERO FORNITORE': self.supplier_number_edit.text() or None,
            'NUMERO OPERAZIONE POS': self.pos_operation_edit.text() or None,
            'IMPORTO LORDO POS': self.pos_gross_amount_edit.value() if self.pos_gross_amount_edit.value() > 0 else None,
            'COMMISSIONE POS': self.pos_commission_edit.value() if self.pos_commission_edit.value() > 0 else None,
            'IMPORTO NETTO': self.net_amount_edit.value()
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

        btn_fornitori = QPushButton("Importa Dati Fornitori")
        btn_fornitori.setMinimumHeight(50)
        btn_fornitori.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1B2631;
            }
        """)
        btn_fornitori.clicked.connect(lambda: self.open_file_dialog("Fornitore"))
        layout.addWidget(btn_fornitori)

        btn_pos = QPushButton("Importa Dati POS")
        btn_pos.setMinimumHeight(50)
        btn_pos.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1B2631;
            }
        """)
        btn_pos.clicked.connect(lambda: self.open_file_dialog("POS"))
        layout.addWidget(btn_pos)

        btn_manuale = QPushButton("Importa Dati Manualmente")
        btn_manuale.setMinimumHeight(50)
        btn_manuale.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1B2631;
            }
        """)
        btn_manuale.clicked.connect(self.import_manuale)
        layout.addWidget(btn_manuale)

    def open_file_dialog(self, source_type):
        """Apre un QFileDialog per selezionare il file da importare."""
        file_filter = "Excel Files (*.xlsx)"
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
                                    f"{len(transactions)} record importati con successo nella tabella temporanea da {file_path}.\n"
                                    f"Usa 'Salva nello Storico' per rendere permanenti i dati.")
        except Exception as e:
            QMessageBox.critical(self, "Errore di Importazione", 
                                 f"Impossibile importare il file {file_path}.\n\nErrore: {e}")

    def parse_supplier_xlsm(self, file_path):
        """Esegue il parsing di un file XLSX di ordini fornitore."""
        df = pd.read_excel(file_path, engine='openpyxl', sheet_name=0, header=3)
        
        # Applica la logica di pulizia fornita dall'utente
        fornitori = df.dropna(subset=['Totale'])
        fornitori = fornitori[['Data', 'Numero Rif.', 'Fornitore', 'Totale']]
        
        transactions = []
        for _, row in fornitori.iterrows():
            # Converte la data al formato con i secondi
            data_obj = pd.to_datetime(row['Data'])
            data_formatted = data_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            transaction = {
                'DATA': data_formatted,
                'FORNITORE': row.get('Fornitore'),
                'NUMERO FORNITORE': str(row.get('Numero Rif.', '')) if row.get('Numero Rif.') is not None else None,
                'NUMERO OPERAZIONE POS': None,
                'IMPORTO LORDO POS': None,
                'COMMISSIONE POS': None,
                'IMPORTO NETTO': -abs(float(row['Totale']))  # Converti in negativo (uscita/costo)
            }
            transactions.append(transaction)
        return transactions

    def parse_pos_xlsx(self, file_path):
        """Esegue il parsing di un file XLSX di transazioni POS."""
        df = pd.read_excel(file_path)
        
        # Applica la logica di pulizia fornita dall'utente
        pos = df.dropna(subset=['Importo netto'])
        pos = pos[['Data Transazione', 'Numero operazione', 'Importo lordo', 'Commissioni', 'Importo netto']]
        
        transactions = []
        for _, row in pos.iterrows():
            # La data transazione è già nel formato corretto con i secondi
            data_obj = pd.to_datetime(row['Data Transazione'])
            data_formatted = data_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            transaction = {
                'DATA': data_formatted,
                'FORNITORE': None,
                'NUMERO FORNITORE': None,
                'NUMERO OPERAZIONE POS': str(row.get('Numero operazione', '')),  # Converti sempre in stringa
                'IMPORTO LORDO POS': float(row.get('Importo lordo', 0)),
                'COMMISSIONE POS': float(row.get('Commissioni', 0)),
                'IMPORTO NETTO': float(row['Importo netto'])
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
                
                importo_netto = data['IMPORTO NETTO']
                if item == "Aggiungi spesa":
                    importo_netto = -abs(importo_netto)

                transaction = {
                    'DATA': data['DATA'],
                    'FORNITORE': data['FORNITORE'],
                    'NUMERO FORNITORE': data['NUMERO FORNITORE'],
                    'NUMERO OPERAZIONE POS': data['NUMERO OPERAZIONE POS'],
                    'IMPORTO LORDO POS': data['IMPORTO LORDO POS'],
                    'COMMISSIONE POS': data['COMMISSIONE POS'],
                    'IMPORTO NETTO': importo_netto
                }
                
                self.data_imported.emit("Manuale", [transaction])
                QMessageBox.information(self, "Importazione Riuscita", 
                                        "Record manuale aggiunto con successo alla tabella temporanea.\n"
                                        "Usa 'Salva nello Storico' per rendere permanenti i dati.")