"""
Widget per la gestione dei dati storici dal database.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                              QLineEdit, QFormLayout, QGroupBox, QMessageBox,
                              QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import sqlite3
from pathlib import Path
from barflow.data.db_manager import DatabaseManager

class HistoryManagementWidget(QWidget):
    """Widget per visualizzare e gestire le transazioni storiche."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.historical_data = []
        self.data_loaded = False  # Flag per tracciare se i dati sono stati caricati
        self.init_ui()
        # Non caricare i dati automaticamente - solo quando l'utente accede alla sezione

    def init_ui(self):
        """Inizializza l'interfaccia utente."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # Ridotto da 20 a 15

        # Sezione filtri per eliminazione (spostata più in alto)
        self.create_filter_section(main_layout)

        # Tabella dati storici
        self.create_table_section(main_layout)

        # Bottoni di azione
        self.create_action_buttons(main_layout)

    def create_filter_section(self, parent_layout):
        """Crea la sezione filtri per l'eliminazione selettiva."""
        filter_group = QGroupBox("🔍 Filtri per Eliminazione Selettiva")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
                font-weight: normal;
            }
        """)
        
        filter_layout = QFormLayout(filter_group)
        filter_layout.setSpacing(10)

        # Filtro per data (formato: YYYY-MM-DD)
        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("es. 2025-03 o 2025-03-15")
        self.date_filter.setStyleSheet(self._get_input_style())
        filter_layout.addRow("📅 Data:", self.date_filter)

        # Filtro per sorgente
        self.source_filter = QComboBox()
        self.source_filter.addItems(["", "fornitore", "pos", "manuale"])
        self.source_filter.setStyleSheet(self._get_input_style())
        filter_layout.addRow("📊 Sorgente:", self.source_filter)

        # Filtro per prodotto
        self.product_filter = QLineEdit()
        self.product_filter.setPlaceholderText("Nome prodotto...")
        self.product_filter.setStyleSheet(self._get_input_style())
        filter_layout.addRow("🛍️ Prodotto:", self.product_filter)

        # Filtro per fornitore
        self.supplier_filter = QLineEdit()
        self.supplier_filter.setPlaceholderText("Nome fornitore...")
        self.supplier_filter.setStyleSheet(self._get_input_style())
        filter_layout.addRow("🏪 Fornitore:", self.supplier_filter)

        # Filtro per categoria
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("Nome categoria...")
        self.category_filter.setStyleSheet(self._get_input_style())
        filter_layout.addRow("📋 Categoria:", self.category_filter)

        # Filtro per importo (range)
        importo_layout = QHBoxLayout()
        self.importo_min = QLineEdit()
        self.importo_min.setPlaceholderText("Min")
        self.importo_min.setStyleSheet(self._get_input_style())
        self.importo_max = QLineEdit()
        self.importo_max.setPlaceholderText("Max")
        self.importo_max.setStyleSheet(self._get_input_style())
        importo_layout.addWidget(self.importo_min)
        importo_layout.addWidget(QLabel(" - "))
        importo_layout.addWidget(self.importo_max)
        filter_layout.addRow("💰 Importo (€):", importo_layout)

        parent_layout.addWidget(filter_group)

    def create_table_section(self, parent_layout):
        """Crea la sezione della tabella."""
        table_label = QLabel("📊 Dati Storici Salvati")
        table_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                padding: 5px;
            }
        """)
        parent_layout.addWidget(table_label)

        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["DATA", "SORGENTE", "PRODOTTO", "FORNITORE", "CATEGORIA", "QUANTITA'", "IMPORTO"])
        
        # Configurazione header
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionsClickable(False)
        
        for col in range(7):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        
        self.table.setMinimumHeight(400)
        self.table.setAlternatingRowColors(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #BDC3C7;
                border-radius: 8px;
                gridline-color: #E8E8E8;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: white;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #2C3E50;
                font-weight: bold;
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
        """)
        
        parent_layout.addWidget(self.table)

    def create_action_buttons(self, parent_layout):
        """Crea i bottoni di azione."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)

        # Bottone ricarica
        self.reload_button = QPushButton("🔄 Ricarica Dati")
        self.reload_button.setFixedSize(180, 45)
        self.reload_button.setStyleSheet(self._get_button_style("#3498DB"))
        self.reload_button.clicked.connect(self.load_historical_data)

        # Bottone elimina filtrate
        self.delete_filtered_button = QPushButton("🗑️ Elimina Filtrate")
        self.delete_filtered_button.setFixedSize(180, 45)
        self.delete_filtered_button.setStyleSheet(self._get_button_style("#E74C3C"))
        self.delete_filtered_button.clicked.connect(self.delete_filtered_records)

        # Bottone svuota tutto (con conferma)
        self.clear_all_button = QPushButton("⚠️ Svuota Tutto")
        self.clear_all_button.setFixedSize(180, 45)
        self.clear_all_button.setStyleSheet(self._get_button_style("#8E44AD"))
        self.clear_all_button.clicked.connect(self.clear_all_records)

        buttons_layout.addWidget(self.reload_button)
        buttons_layout.addWidget(self.delete_filtered_button)
        buttons_layout.addWidget(self.clear_all_button)

        parent_layout.addLayout(buttons_layout)

    def _get_input_style(self):
        """Restituisce lo stile per gli input con i colori della tabella."""
        return """
            QLineEdit, QComboBox {
                padding: 10px;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                font-size: 10px;
                background-color: #FFFFFF;
                color: #333333;
                min-height: 10px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498DB;
                background-color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #7F8C8D;
                font-size: 8px;
            }
            QComboBox::drop-down {
                border: 1px solid #BDC3C7;
                background-color: #FFFFFF;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7F8C8D;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #BDC3C7;
                selection-background-color: #3498DB;
                selection-color: white;
            }
        """

    def _get_button_style(self, color):
        """Restituisce lo stile per i bottoni."""
        hover_color = {
            "#3498DB": "#2980B9",
            "#E74C3C": "#C0392B", 
            "#8E44AD": "#7D3C98"
        }.get(color, color)
        
        pressed_color = {
            "#3498DB": "#21618C",
            "#E74C3C": "#A93226",
            "#8E44AD": "#6C3483"
        }.get(color, color)

        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

    def load_historical_data(self, show_popup=True):
        """Carica i dati storici dal database."""
        try:
            self.historical_data = self.db_manager.load_all_transactions()
            self.update_table(self.historical_data)
            self.data_loaded = True
            
            # Mostra statistiche solo se richiesto (non al primo caricamento automatico)
            if show_popup:
                stats = self.db_manager.get_database_stats()
                QMessageBox.information(self, "Dati caricati", 
                    f"Caricati {len(self.historical_data)} record dal database storico.\n"
                    f"Periodo: {stats['date_range'][0]} - {stats['date_range'][1]}")
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dei dati: {e}")

    def load_data_if_needed(self):
        """Carica i dati solo se non sono ancora stati caricati."""
        if not self.data_loaded:
            self.load_historical_data(show_popup=False)

    def update_table(self, data):
        """Aggiorna la tabella con i dati forniti."""
        self.table.setRowCount(len(data))

        for row, record in enumerate(data):
            # Data
            data_item = QTableWidgetItem(record.get('DATA', ''))
            data_item.setTextAlignment(Qt.AlignCenter)
            
            # Sorgente
            sorgente_item = QTableWidgetItem(record.get('SORGENTE', ''))
            sorgente_item.setTextAlignment(Qt.AlignCenter)
            
            # Prodotto
            prodotto_item = QTableWidgetItem(record.get('PRODOTTO', ''))
            prodotto_item.setTextAlignment(Qt.AlignCenter)
            
            # Fornitore
            fornitore_item = QTableWidgetItem(record.get('FORNITORE', ''))
            fornitore_item.setTextAlignment(Qt.AlignCenter)
            
            # Categoria
            categoria_item = QTableWidgetItem(record.get('CATEGORIA', ''))
            categoria_item.setTextAlignment(Qt.AlignCenter)
            
            # Quantità
            quantita_item = QTableWidgetItem(str(record.get('QUANTITA\'', '')))
            quantita_item.setTextAlignment(Qt.AlignCenter)
            
            # Importo
            importo_val = float(record.get('IMPORTO', 0))
            importo_item = QTableWidgetItem(f"{importo_val:.2f} €")
            importo_item.setTextAlignment(Qt.AlignCenter)
            
            if importo_val < 0:
                importo_item.setForeground(QColor("red"))
            else:
                importo_item.setForeground(QColor("green"))

            self.table.setItem(row, 0, data_item)
            self.table.setItem(row, 1, sorgente_item)
            self.table.setItem(row, 2, prodotto_item)
            self.table.setItem(row, 3, fornitore_item)
            self.table.setItem(row, 4, categoria_item)
            self.table.setItem(row, 5, quantita_item)
            self.table.setItem(row, 6, importo_item)

    def get_filter_conditions(self):
        """Costruisce le condizioni SQL per i filtri."""
        conditions = []
        params = []

        # Filtro data
        date_text = self.date_filter.text().strip()
        if date_text:
            if len(date_text) == 7:  # YYYY-MM
                conditions.append("data LIKE ?")
                params.append(f"{date_text}%")
            else:  # Data completa
                conditions.append("data = ?")
                params.append(date_text)

        # Filtro sorgente
        if self.source_filter.currentText():
            conditions.append("sorgente = ?")
            params.append(self.source_filter.currentText())

        # Filtro prodotto
        product_text = self.product_filter.text().strip()
        if product_text:
            conditions.append("prodotto LIKE ?")
            params.append(f"%{product_text}%")

        # Filtro fornitore
        supplier_text = self.supplier_filter.text().strip()
        if supplier_text:
            conditions.append("fornitore LIKE ?")
            params.append(f"%{supplier_text}%")

        # Filtro categoria
        category_text = self.category_filter.text().strip()
        if category_text:
            conditions.append("categoria LIKE ?")
            params.append(f"%{category_text}%")

        # Filtro importo
        min_amount = self.importo_min.text().strip()
        max_amount = self.importo_max.text().strip()
        
        if min_amount:
            try:
                conditions.append("importo >= ?")
                params.append(float(min_amount))
            except ValueError:
                pass
                
        if max_amount:
            try:
                conditions.append("importo <= ?")
                params.append(float(max_amount))
            except ValueError:
                pass

        return conditions, params

    def delete_filtered_records(self):
        """Elimina i record che corrispondono ai filtri."""
        conditions, params = self.get_filter_conditions()
        
        if not conditions:
            QMessageBox.warning(self, "Nessun filtro", 
                              "Imposta almeno un filtro per procedere con l'eliminazione.")
            return

        try:
            # Conta i record da eliminare
            db_path = Path("historical_data/barflow_history.db")
            with sqlite3.connect(db_path) as conn:
                where_clause = " AND ".join(conditions)
                count_query = f"SELECT COUNT(*) FROM transactions WHERE {where_clause}"
                count = conn.execute(count_query, params).fetchone()[0]

                if count == 0:
                    QMessageBox.information(self, "Nessun record", 
                                          "Nessun record corrisponde ai filtri specificati.")
                    return

                # Conferma eliminazione
                reply = QMessageBox.question(self, "Conferma eliminazione", 
                    f"Sei sicuro di voler eliminare {count} record che corrispondono ai filtri?\n\n"
                    "⚠️ Questa operazione non può essere annullata!",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # Elimina i record
                    delete_query = f"DELETE FROM transactions WHERE {where_clause}"
                    conn.execute(delete_query, params)
                    conn.commit()

                    QMessageBox.information(self, "Eliminazione completata", 
                                          f"Eliminati {count} record dal database.")
                    
                    # Ricarica i dati
                    self.load_historical_data()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {e}")

    def clear_all_records(self):
        """Elimina tutti i record dal database (con doppia conferma)."""
        # Prima conferma
        reply1 = QMessageBox.question(self, "⚠️ ATTENZIONE - Eliminazione totale", 
            "Stai per eliminare TUTTI i dati storici dal database.\n\n"
            "⚠️ Questa operazione cancellerà permanentemente tutti i record salvati!\n\n"
            "Sei sicuro di voler continuare?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply1 != QMessageBox.Yes:
            return

        # Seconda conferma
        reply2 = QMessageBox.question(self, "🚨 CONFERMA FINALE", 
            "ULTIMA CONFERMA:\n\n"
            "Eliminare TUTTI i dati storici?\n\n"
            "💥 Non sarà possibile recuperare i dati!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply2 == QMessageBox.Yes:
            try:
                db_path = Path("historical_data/barflow_history.db")
                with sqlite3.connect(db_path) as conn:
                    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
                    conn.execute("DELETE FROM transactions")
                    conn.commit()

                QMessageBox.information(self, "Database svuotato", 
                                      f"Eliminati tutti i {count} record dal database storico.")
                
                # Ricarica i dati (ora vuoti)
                self.load_historical_data()

            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {e}")