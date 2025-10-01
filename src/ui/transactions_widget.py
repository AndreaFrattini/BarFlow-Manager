"""
Widget per la gestione delle transazioni
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
                              QDateEdit, QLabel, QFrame, QHeaderView, QAbstractItemView,
                              QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
                              QCheckBox, QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime


class TransactionDialog(QDialog):
    """Dialog per aggiungere/modificare transazioni"""
    
    def __init__(self, db_manager, transaction=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.transaction = transaction
        self.is_edit_mode = transaction is not None
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_transaction_data()
    
    def init_ui(self):
        """Inizializza l'interfaccia del dialog"""
        title = "Modifica Transazione" if self.is_edit_mode else "Nuova Transazione"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Form principale
        form_group = QGroupBox("Dettagli Transazione")
        form_layout = QFormLayout(form_group)
        
        # Data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Data:", self.date_edit)
        
        # Descrizione
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Descrizione della transazione...")
        form_layout.addRow("Descrizione:", self.description_edit)
        
        # Importo
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0.01, 999999.99)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setSuffix(" €")
        form_layout.addRow("Importo:", self.amount_spinbox)
        
        # Tipo (Entrata/Uscita)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Entrata", "Uscita"])
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Categoria
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Categoria:", self.category_combo)
        
        layout.addWidget(form_group)
        
        # Note aggiuntive
        notes_group = QGroupBox("Note Aggiuntive (Opzionale)")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Note o informazioni aggiuntive...")
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # Pulsanti
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Stile
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def load_categories(self):
        """Carica le categorie disponibili"""
        try:
            categories = self.db_manager.get_categories()
            
            for category in categories:
                self.category_combo.addItem(category['name'], category['category_id'])
                
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Impossibile caricare le categorie: {e}")
    
    def load_transaction_data(self):
        """Carica i dati della transazione per la modifica"""
        if not self.transaction:
            return
        
        # Data
        date = datetime.strptime(self.transaction['transaction_date'], '%Y-%m-%d')
        self.date_edit.setDate(QDate(date.year, date.month, date.day))
        
        # Descrizione
        self.description_edit.setText(self.transaction['description'])
        
        # Importo
        self.amount_spinbox.setValue(self.transaction['amount'])
        
        # Tipo
        self.type_combo.setCurrentText("Entrata" if self.transaction['is_income'] else "Uscita")
        
        # Categoria
        category_id = self.transaction['category_id']
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == category_id:
                self.category_combo.setCurrentIndex(i)
                break
        
        # Note
        metadata = self.transaction.get('metadata', {})
        if 'notes' in metadata:
            self.notes_edit.setPlainText(metadata['notes'])
    
    def get_transaction_data(self):
        """Ottiene i dati della transazione dal form"""
        # Validazione
        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Errore", "La descrizione è obbligatoria")
            return None
        
        if self.amount_spinbox.value() <= 0:
            QMessageBox.warning(self, "Errore", "L'importo deve essere maggiore di zero")
            return None
        
        if self.category_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Errore", "Seleziona una categoria")
            return None
        
        # Costruisci i dati
        transaction_data = {
            'transaction_date': self.date_edit.date().toString("yyyy-MM-dd"),
            'description': self.description_edit.text().strip(),
            'amount': self.amount_spinbox.value(),
            'is_income': self.type_combo.currentText() == "Entrata",
            'category_id': self.category_combo.currentData()
        }
        
        # Aggiungi note ai metadata se presenti
        notes = self.notes_edit.toPlainText().strip()
        if notes:
            transaction_data['metadata'] = {'notes': notes}
        
        return transaction_data


class TransactionsWidget(QWidget):
    """Widget principale per la gestione delle transazioni"""
    
    # Segnale emesso quando le transazioni cambiano
    transaction_changed = Signal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_transactions = []
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Barra degli strumenti
        self.create_toolbar(layout)
        
        # Filtri
        self.create_filters(layout)
        
        # Tabella transazioni
        self.create_transactions_table(layout)
        
        # Pannello statistiche
        self.create_stats_panel(layout)
    
    def create_toolbar(self, parent_layout):
        """Crea la barra degli strumenti"""
        toolbar_frame = QFrame()
        toolbar_frame.setMaximumHeight(60)
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        
        # Pulsante nuova transazione
        self.add_btn = QPushButton("➕ Nuova Transazione")
        self.add_btn.clicked.connect(self.add_transaction)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        toolbar_layout.addWidget(self.add_btn)
        
        # Pulsante modifica
        self.edit_btn = QPushButton("✏️ Modifica")
        self.edit_btn.clicked.connect(self.edit_transaction)
        self.edit_btn.setEnabled(False)
        toolbar_layout.addWidget(self.edit_btn)
        
        # Pulsante elimina
        self.delete_btn = QPushButton("🗑️ Elimina")
        self.delete_btn.clicked.connect(self.delete_transaction)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        toolbar_layout.addWidget(self.delete_btn)
        
        toolbar_layout.addStretch()
        
        # Pulsante aggiorna
        refresh_btn = QPushButton("🔄 Aggiorna")
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(refresh_btn)
        
        # Pulsante esporta
        export_btn = QPushButton("📊 Esporta")
        export_btn.clicked.connect(self.export_transactions)
        toolbar_layout.addWidget(export_btn)
        
        parent_layout.addWidget(toolbar_frame)
    
    def create_filters(self, parent_layout):
        """Crea i filtri"""
        filters_frame = QFrame()
        filters_frame.setMaximumHeight(60)
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(15, 10, 15, 10)
        
        # Filtro data da
        filters_layout.addWidget(QLabel("Da:"))
        self.date_from_filter = QDateEdit()
        self.date_from_filter.setCalendarPopup(True)
        self.date_from_filter.setDate(QDate.currentDate().addMonths(-3))
        self.date_from_filter.dateChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.date_from_filter)
        
        # Filtro data a
        filters_layout.addWidget(QLabel("A:"))
        self.date_to_filter = QDateEdit()
        self.date_to_filter.setCalendarPopup(True)
        self.date_to_filter.setDate(QDate.currentDate())
        self.date_to_filter.dateChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.date_to_filter)
        
        filters_layout.addSpacing(20)
        
        # Filtro categoria
        filters_layout.addWidget(QLabel("Categoria:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tutte le categorie", None)
        self.load_categories_filter()
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.category_filter)
        
        filters_layout.addSpacing(20)
        
        # Filtro tipo
        filters_layout.addWidget(QLabel("Tipo:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tutti", "Entrate", "Uscite"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.type_filter)
        
        filters_layout.addSpacing(20)
        
        # Filtro ricerca
        filters_layout.addWidget(QLabel("Cerca:"))
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Cerca nella descrizione...")
        self.search_filter.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_filter)
        
        filters_layout.addStretch()
        
        parent_layout.addWidget(filters_frame)
    
    def create_transactions_table(self, parent_layout):
        """Crea la tabella delle transazioni"""
        # Frame contenitore
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        # Titolo
        title = QLabel("Elenco Transazioni")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        table_layout.addWidget(title)
        
        # Tabella
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Data", "Descrizione", "Categoria", "Tipo", "Importo", "Fonte"
        ])
        
        # Configura tabella
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setGridStyle(Qt.NoPen)
        
        # Ridimensiona colonne
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Categoria
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Importo
        
        # Connessioni
        self.transactions_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.transactions_table.itemDoubleClicked.connect(self.edit_transaction)
        
        table_layout.addWidget(self.transactions_table)
        
        parent_layout.addWidget(table_frame, 1)  # Espandibile
    
    def create_stats_panel(self, parent_layout):
        """Crea il pannello delle statistiche"""
        stats_frame = QFrame()
        stats_frame.setMaximumHeight(80)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        
        # Statistiche
        self.total_transactions_label = QLabel("Transazioni: 0")
        self.total_transactions_label.setStyleSheet("font-weight: bold; color: #2C3E50;")
        stats_layout.addWidget(self.total_transactions_label)
        
        stats_layout.addStretch()
        
        self.total_income_label = QLabel("Entrate: €0.00")
        self.total_income_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        stats_layout.addWidget(self.total_income_label)
        
        stats_layout.addStretch()
        
        self.total_expenses_label = QLabel("Uscite: €0.00")
        self.total_expenses_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
        stats_layout.addWidget(self.total_expenses_label)
        
        stats_layout.addStretch()
        
        self.net_amount_label = QLabel("Netto: €0.00")
        self.net_amount_label.setStyleSheet("font-weight: bold; color: #2C3E50;")
        stats_layout.addWidget(self.net_amount_label)
        
        parent_layout.addWidget(stats_frame)
    
    def load_categories_filter(self):
        """Carica le categorie per il filtro"""
        try:
            categories = self.db_manager.get_categories()
            
            for category in categories:
                self.category_filter.addItem(category['name'], category['category_id'])
                
        except Exception as e:
            print(f"Errore nel caricamento categorie: {e}")
    
    def refresh_data(self):
        """Aggiorna i dati delle transazioni"""
        self.apply_filters()
    
    def apply_filters(self):
        """Applica i filtri e aggiorna la tabella"""
        try:
            # Ottieni parametri filtro
            start_date = self.date_from_filter.date().toString("yyyy-MM-dd")
            end_date = self.date_to_filter.date().toString("yyyy-MM-dd")
            
            category_id = self.category_filter.currentData()
            
            # Ottieni transazioni dal database
            transactions = self.db_manager.get_transactions(start_date, end_date, category_id)
            
            # Applica filtri addizionali
            filtered_transactions = []
            
            for transaction in transactions:
                # Filtro tipo
                type_filter = self.type_filter.currentText()
                if type_filter == "Entrate" and not transaction['is_income']:
                    continue
                elif type_filter == "Uscite" and transaction['is_income']:
                    continue
                
                # Filtro ricerca
                search_text = self.search_filter.text().lower()
                if search_text and search_text not in transaction['description'].lower():
                    continue
                
                filtered_transactions.append(transaction)
            
            self.current_transactions = filtered_transactions
            self.update_table()
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'aggiornamento dati: {e}")
    
    def update_table(self):
        """Aggiorna il contenuto della tabella"""
        self.transactions_table.setRowCount(len(self.current_transactions))
        
        for row, transaction in enumerate(self.current_transactions):
            # Data
            date_item = QTableWidgetItem(transaction['transaction_date'])
            date_item.setData(Qt.UserRole, transaction['transaction_id'])
            self.transactions_table.setItem(row, 0, date_item)
            
            # Descrizione
            desc_item = QTableWidgetItem(transaction['description'])
            self.transactions_table.setItem(row, 1, desc_item)
            
            # Categoria
            category_item = QTableWidgetItem(transaction['category_name'])
            self.transactions_table.setItem(row, 2, category_item)
            
            # Tipo
            type_text = "Entrata" if transaction['is_income'] else "Uscita"
            type_item = QTableWidgetItem(type_text)
            
            # Colore basato sul tipo
            if transaction['is_income']:
                type_item.setForeground(QColor("#27AE60"))
            else:
                type_item.setForeground(QColor("#E74C3C"))
            
            self.transactions_table.setItem(row, 3, type_item)
            
            # Importo
            amount_text = f"€{transaction['amount']:,.2f}"
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Colore basato sul tipo
            if transaction['is_income']:
                amount_item.setForeground(QColor("#27AE60"))
            else:
                amount_item.setForeground(QColor("#E74C3C"))
            
            self.transactions_table.setItem(row, 4, amount_item)
            
            # Fonte
            source = transaction.get('source_filename', 'Manuale')
            source_item = QTableWidgetItem(source)
            self.transactions_table.setItem(row, 5, source_item)
    
    def update_stats(self):
        """Aggiorna le statistiche"""
        total_count = len(self.current_transactions)
        total_income = sum(t['amount'] for t in self.current_transactions if t['is_income'])
        total_expenses = sum(t['amount'] for t in self.current_transactions if not t['is_income'])
        net_amount = total_income - total_expenses
        
        self.total_transactions_label.setText(f"Transazioni: {total_count}")
        self.total_income_label.setText(f"Entrate: €{total_income:,.2f}")
        self.total_expenses_label.setText(f"Uscite: €{total_expenses:,.2f}")
        
        # Colore del netto basato sul valore
        if net_amount >= 0:
            color = "#27AE60"
        else:
            color = "#E74C3C"
        
        self.net_amount_label.setText(f"Netto: €{net_amount:,.2f}")
        self.net_amount_label.setStyleSheet(f"font-weight: bold; color: {color};")
    
    def on_selection_changed(self):
        """Gestisce il cambio di selezione nella tabella"""
        has_selection = len(self.transactions_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_transaction(self):
        """Aggiunge una nuova transazione"""
        dialog = TransactionDialog(self.db_manager, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            transaction_data = dialog.get_transaction_data()
            
            if transaction_data:
                try:
                    self.db_manager.add_transactions([transaction_data])
                    QMessageBox.information(self, "Successo", "Transazione aggiunta con successo!")
                    self.refresh_data()
                    self.transaction_changed.emit()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore nell'aggiunta della transazione: {e}")
    
    def edit_transaction(self):
        """Modifica la transazione selezionata"""
        current_row = self.transactions_table.currentRow()
        
        if current_row < 0:
            return
        
        transaction = self.current_transactions[current_row]
        dialog = TransactionDialog(self.db_manager, transaction, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            transaction_data = dialog.get_transaction_data()
            
            if transaction_data:
                try:
                    self.db_manager.update_transaction(
                        transaction['transaction_id'],
                        **transaction_data
                    )
                    QMessageBox.information(self, "Successo", "Transazione modificata con successo!")
                    self.refresh_data()
                    self.transaction_changed.emit()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore nella modifica della transazione: {e}")
    
    def delete_transaction(self):
        """Elimina la transazione selezionata"""
        current_row = self.transactions_table.currentRow()
        
        if current_row < 0:
            return
        
        transaction = self.current_transactions[current_row]
        
        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare la transazione:\n\n"
            f"'{transaction['description']}'\n"
            f"Data: {transaction['transaction_date']}\n"
            f"Importo: €{transaction['amount']:,.2f}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_transaction(transaction['transaction_id'])
                QMessageBox.information(self, "Successo", "Transazione eliminata con successo!")
                self.refresh_data()
                self.transaction_changed.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nell'eliminazione della transazione: {e}")
    
    def export_transactions(self):
        """Esporta le transazioni correnti"""
        if not self.current_transactions:
            QMessageBox.information(self, "Info", "Nessuna transazione da esportare")
            return
        
        try:
            # Ottieni il periodo dai filtri
            start_date = self.date_from_filter.date().toString("yyyy-MM-dd")
            end_date = self.date_to_filter.date().toString("yyyy-MM-dd")
            
            # Crea il report generator se non esiste
            from ..reports.report_generator import ReportGenerator
            report_gen = ReportGenerator(self.db_manager)
            
            # Esporta
            file_path = report_gen.export_to_excel(start_date, end_date, include_transactions=True)
            
            QMessageBox.information(
                self,
                "Export Completato",
                f"Transazioni esportate con successo!\n\n"
                f"File salvato in:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Errore Export", f"Errore durante l'esportazione: {e}")