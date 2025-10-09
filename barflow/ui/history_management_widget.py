"""
Widget per la gestione dei dati storici dal database.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QPushButton, QLabel,
                              QLineEdit, QFormLayout, QGroupBox, QMessageBox,
                              QComboBox, QSizePolicy, QGridLayout)
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
        # Layout principale con margini ridotti per utilizzare più spazio
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Sezione filtri per eliminazione
        self.create_filter_section(main_layout)

        # Sezione tabella con bottoni integrati nel titolo
        self.create_table_section(main_layout)

    def create_filter_section(self, parent_layout):
        """Crea la sezione filtri per l'eliminazione selettiva con layout responsive."""
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
        
        # Layout principale del gruppo filtri
        group_layout = QVBoxLayout(filter_group)
        group_layout.setSpacing(10)
        
        # Layout griglia responsive per i filtri - ottimizzato su 2 righe
        filter_grid = QGridLayout()
        filter_grid.setSpacing(15)  # Spaziatura aumentata per migliore leggibilità
        filter_grid.setContentsMargins(15, 15, 15, 15)

        # === PRIMA RIGA: Data, Sorgente, Descrizione, Fornitore ===
        
        # Data
        data_label = QLabel("📅 Data:")
        data_label.setMinimumWidth(120)  # Larghezza minima per allineamento
        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("es. 2025-03 o 2025-03-15")
        self.date_filter.setStyleSheet(self._get_input_style())
        
        # Sorgente
        source_label = QLabel("📊 Sorgente:")
        source_label.setMinimumWidth(120)
        self.source_filter = QComboBox()
        self.source_filter.addItems(["", "fornitore", "pos", "manuale"])
        self.source_filter.setStyleSheet(self._get_input_style())

        # Descrizione
        descrizione_label = QLabel("📝 Descrizione:")
        descrizione_label.setMinimumWidth(120)
        self.descrizione_filter = QLineEdit()
        self.descrizione_filter.setPlaceholderText("Descrizione...")
        self.descrizione_filter.setStyleSheet(self._get_input_style())

        # Fornitore
        supplier_label = QLabel("🏪 Fornitore:")
        supplier_label.setMinimumWidth(120)
        self.supplier_filter = QLineEdit()
        self.supplier_filter.setPlaceholderText("Nome fornitore...")
        self.supplier_filter.setStyleSheet(self._get_input_style())

        # Aggiungi prima riga alla griglia con distribuzione 1:2 (label:campo)
        filter_grid.addWidget(data_label, 0, 0)
        filter_grid.addWidget(self.date_filter, 0, 1)
        filter_grid.addWidget(source_label, 0, 2)
        filter_grid.addWidget(self.source_filter, 0, 3)
        filter_grid.addWidget(descrizione_label, 0, 4)
        filter_grid.addWidget(self.descrizione_filter, 0, 5)
        filter_grid.addWidget(supplier_label, 0, 6)
        filter_grid.addWidget(self.supplier_filter, 0, 7)

        # === SECONDA RIGA: Numero Fornitore, Numero Operazione POS, Importo Netto ===
        
        # Numero fornitore
        numero_fornitore_label = QLabel("🔢 Numero Fornitore:")
        numero_fornitore_label.setMinimumWidth(120)
        self.numero_fornitore_filter = QLineEdit()
        self.numero_fornitore_filter.setPlaceholderText("Numero fornitore...")
        self.numero_fornitore_filter.setStyleSheet(self._get_input_style())

        # Numero operazione POS
        numero_pos_label = QLabel("🏧 Numero Operazione POS:")
        numero_pos_label.setMinimumWidth(120)
        self.numero_pos_filter = QLineEdit()
        self.numero_pos_filter.setPlaceholderText("Numero operazione POS...")
        self.numero_pos_filter.setStyleSheet(self._get_input_style())

        # Importo netto (range) - layout ottimizzato
        importo_label = QLabel("💰 Importo Netto (€):")
        importo_label.setMinimumWidth(120)
        
        # Widget container per i campi importo con layout orizzontale ottimizzato
        importo_widget = QWidget()
        importo_layout = QHBoxLayout(importo_widget)
        importo_layout.setContentsMargins(0, 0, 0, 0)
        importo_layout.setSpacing(8)
        
        self.importo_min = QLineEdit()
        self.importo_min.setPlaceholderText("Min")
        self.importo_min.setStyleSheet(self._get_input_style())
        
        dash_label = QLabel(" - ")
        dash_label.setAlignment(Qt.AlignCenter)
        dash_label.setStyleSheet("color: #7F8C8D; font-weight: bold;")
        
        self.importo_max = QLineEdit()
        self.importo_max.setPlaceholderText("Max")
        self.importo_max.setStyleSheet(self._get_input_style())
        
        importo_layout.addWidget(self.importo_min)
        importo_layout.addWidget(dash_label)
        importo_layout.addWidget(self.importo_max)

        # Aggiungi seconda riga alla griglia
        filter_grid.addWidget(numero_fornitore_label, 1, 0)
        filter_grid.addWidget(self.numero_fornitore_filter, 1, 1)
        filter_grid.addWidget(numero_pos_label, 1, 2)
        filter_grid.addWidget(self.numero_pos_filter, 1, 3)
        filter_grid.addWidget(importo_label, 1, 4)
        filter_grid.addWidget(importo_widget, 1, 5, 1, 3)  # Span su 3 colonne per l'importo

        # Imposta stretch ottimizzato per sfruttare tutto lo spazio orizzontale
        # Colonne dispari (0,2,4,6) = etichette con larghezza fissa
        # Colonne pari (1,3,5,7) = campi input che si espandono
        filter_grid.setColumnStretch(0, 0)  # Etichetta Data - fissa
        filter_grid.setColumnStretch(1, 2)  # Campo Data - espandibile
        filter_grid.setColumnStretch(2, 0)  # Etichetta Sorgente - fissa  
        filter_grid.setColumnStretch(3, 2)  # Campo Sorgente - espandibile
        filter_grid.setColumnStretch(4, 0)  # Etichetta Descrizione - fissa
        filter_grid.setColumnStretch(5, 2)  # Campo Descrizione - espandibile
        filter_grid.setColumnStretch(6, 0)  # Etichetta Fornitore - fissa
        filter_grid.setColumnStretch(7, 2)  # Campo Fornitore - espandibile

        group_layout.addLayout(filter_grid)
        parent_layout.addWidget(filter_group)

    def create_table_section(self, parent_layout):
        """Crea la sezione della tabella con bottoni integrati nel titolo."""
        # Layout orizzontale per titolo e bottoni
        title_layout = QHBoxLayout()
        title_layout.setSpacing(20)
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        # Titolo della tabella
        table_label = QLabel("📊 Dati Storici Salvati")
        table_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                padding: 5px;
            }
        """)
        title_layout.addWidget(table_label)
        
        # Spacer per spingere i bottoni a destra
        title_layout.addStretch()
        
        # Crea i bottoni di azione integrati
        self.create_action_buttons_inline(title_layout)
        
        parent_layout.addLayout(title_layout)

        # Tabella
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "DATA", "SORGENTE", "DESCRIZIONE", "FORNITORE", "NUMERO FORNITORE", 
            "NUMERO OPERAZIONE POS", "IMPORTO LORDO POS", "COMMISSIONE POS", "IMPORTO NETTO"
        ])
        
        # Configurazione header responsive (identica a TransactionsWidget)
        header = self.table.horizontalHeader()
        header.setSectionsClickable(False)
        
        # Imposta dimensioni responsive per le colonne (come TransactionsWidget)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # DATA - contenuto fisso
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # SORGENTE - contenuto limitato
        header.setSectionResizeMode(2, QHeaderView.Interactive)       # DESCRIZIONE - può essere lungo, ridimensionabile
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # FORNITORE - può essere lungo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # NUMERO FORNITORE - contenuto numerico
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # NUMERO OPERAZIONE POS - contenuto numerico
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # IMPORTO LORDO POS - contenuto numerico
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # COMMISSIONE POS - contenuto numerico
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # IMPORTO NETTO - contenuto numerico
        
        # Imposta larghezza minima per la colonna DESCRIZIONE
        self.table.setColumnWidth(2, 120)  # Larghezza minima per DESCRIZIONE
        header.setMinimumSectionSize(120)  # Larghezza minima globale
        
        # Rimuovi dimensioni fisse - ora la tabella si adatta al contenitore
        self.table.setMinimumHeight(400)  # Altezza minima ragionevole
        
        # Imposta policy di ridimensionamento per rendere la tabella espandibile
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configurazioni scrolling per gestire contenuto che eccede
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setAlternatingRowColors(True)
        self.table.setGridStyle(Qt.SolidLine)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #E8E8E8;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: white;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
                font-size: 10pt;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E6F2FF;
                color: #333333;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
        """)
        
        parent_layout.addWidget(self.table)

    def create_action_buttons_inline(self, parent_layout):
        """Crea i bottoni di azione integrati nel titolo della tabella."""
        # Bottone ricarica (compatto)
        self.reload_button = QPushButton("🔄 Ricarica")
        self.reload_button.setFixedWidth(120)  # Più compatto per stare accanto al titolo
        self.reload_button.setFixedHeight(35)   # Altezza ridotta
        self.reload_button.setStyleSheet(self._get_compact_button_style("#3498DB"))
        self.reload_button.clicked.connect(self.load_historical_data)

        # Bottone elimina filtrate (compatto)
        self.delete_filtered_button = QPushButton("🗑️ Elimina")
        self.delete_filtered_button.setFixedWidth(120)
        self.delete_filtered_button.setFixedHeight(35)
        self.delete_filtered_button.setStyleSheet(self._get_compact_button_style("#E74C3C"))
        self.delete_filtered_button.clicked.connect(self.delete_filtered_records)

        # Bottone svuota tutto (compatto)
        self.clear_all_button = QPushButton("⚠️ Svuota")
        self.clear_all_button.setFixedWidth(120)
        self.clear_all_button.setFixedHeight(35)
        self.clear_all_button.setStyleSheet(self._get_compact_button_style("#8E44AD"))
        self.clear_all_button.clicked.connect(self.clear_all_records)

        parent_layout.addWidget(self.reload_button)
        parent_layout.addWidget(self.delete_filtered_button)
        parent_layout.addWidget(self.clear_all_button)

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

    def _get_compact_button_style(self, color):
        """Restituisce lo stile per i bottoni compatti integrati nel titolo."""
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
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
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
            try:
                # Data
                data_item = QTableWidgetItem(str(record.get('DATA', '')))
                data_item.setTextAlignment(Qt.AlignCenter)
                
                # Sorgente
                sorgente_item = QTableWidgetItem(str(record.get('SORGENTE', '')))
                sorgente_item.setTextAlignment(Qt.AlignCenter)
                
                # Descrizione
                descrizione_text = str(record.get('DESCRIZIONE', '') or '')
                if len(descrizione_text) > 25:
                    descrizione_text = descrizione_text[:22] + "..."
                descrizione_item = QTableWidgetItem(descrizione_text)
                descrizione_item.setTextAlignment(Qt.AlignCenter)
                descrizione_item.setToolTip(str(record.get('DESCRIZIONE', '') or ''))
                
                # Fornitore
                fornitore_text = str(record.get('FORNITORE', '') or '')
                if len(fornitore_text) > 20:
                    fornitore_text = fornitore_text[:17] + "..."
                fornitore_item = QTableWidgetItem(fornitore_text)
                fornitore_item.setTextAlignment(Qt.AlignCenter)
                fornitore_item.setToolTip(str(record.get('FORNITORE', '') or ''))
                
                # Numero fornitore
                numero_fornitore_item = QTableWidgetItem(str(record.get('NUMERO FORNITORE', '') or ''))
                numero_fornitore_item.setTextAlignment(Qt.AlignCenter)
                
                # Numero operazione POS
                numero_pos_value = record.get('NUMERO OPERAZIONE POS', '')
                if numero_pos_value is not None and numero_pos_value != '':
                    numero_pos_str = str(numero_pos_value)
                else:
                    numero_pos_str = ''
                numero_pos_item = QTableWidgetItem(numero_pos_str)
                numero_pos_item.setTextAlignment(Qt.AlignCenter)
                
                # Importo lordo POS
                importo_lordo = record.get('IMPORTO LORDO POS')
                if importo_lordo is not None:
                    try:
                        importo_lordo_str = f"{float(importo_lordo):.2f} €"
                    except (ValueError, TypeError):
                        importo_lordo_str = str(importo_lordo) if importo_lordo != '' else ""
                else:
                    importo_lordo_str = ""
                importo_lordo_item = QTableWidgetItem(importo_lordo_str)
                importo_lordo_item.setTextAlignment(Qt.AlignCenter)
                
                # Commissione POS
                commissione = record.get('COMMISSIONE POS')
                if commissione is not None:
                    try:
                        commissione_str = f"{float(commissione):.2f} €"
                    except (ValueError, TypeError):
                        commissione_str = str(commissione) if commissione != '' else ""
                else:
                    commissione_str = ""
                commissione_item = QTableWidgetItem(commissione_str)
                commissione_item.setTextAlignment(Qt.AlignCenter)
                
                # Importo netto
                importo_netto_str = record.get('IMPORTO NETTO', '0.0')
                try:
                    importo_netto_val = float(importo_netto_str)
                    importo_netto_item = QTableWidgetItem(f"{importo_netto_val:.2f} €")
                    importo_netto_item.setTextAlignment(Qt.AlignCenter)

                    if importo_netto_val < 0:
                        importo_netto_item.setForeground(QColor("red"))
                    else:
                        importo_netto_item.setForeground(QColor("green"))
                except (ValueError, TypeError):
                    importo_netto_item = QTableWidgetItem(str(importo_netto_str))
                    importo_netto_item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row, 0, data_item)
                self.table.setItem(row, 1, sorgente_item)
                self.table.setItem(row, 2, descrizione_item)
                self.table.setItem(row, 3, fornitore_item)
                self.table.setItem(row, 4, numero_fornitore_item)
                self.table.setItem(row, 5, numero_pos_item)
                self.table.setItem(row, 6, importo_lordo_item)
                self.table.setItem(row, 7, commissione_item)
                self.table.setItem(row, 8, importo_netto_item)
                
            except Exception as e:
                # Log dell'errore e crea una riga vuota piuttosto che crashare
                print(f"Errore nella creazione della riga {row}: {e}")
                # Crea celle vuote per evitare il crash
                for col in range(9):  # Aggiornato a 9 colonne
                    empty_item = QTableWidgetItem("")
                    empty_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, empty_item)
        
        # Dopo aver popolato la tabella, ottimizza le dimensioni delle colonne
        self._optimize_column_widths()

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

        # Filtro descrizione
        descrizione_text = self.descrizione_filter.text().strip()
        if descrizione_text:
            conditions.append("descrizione LIKE ?")
            params.append(f"%{descrizione_text}%")

        # Filtro fornitore
        supplier_text = self.supplier_filter.text().strip()
        if supplier_text:
            conditions.append("fornitore LIKE ?")
            params.append(f"%{supplier_text}%")

        # Filtro numero fornitore
        numero_fornitore_text = self.numero_fornitore_filter.text().strip()
        if numero_fornitore_text:
            conditions.append("numero_fornitore LIKE ?")
            params.append(f"%{numero_fornitore_text}%")

        # Filtro numero operazione POS
        numero_pos_text = self.numero_pos_filter.text().strip()
        if numero_pos_text:
            conditions.append("numero_operazione_pos LIKE ?")
            params.append(f"%{numero_pos_text}%")

        # Filtro importo netto
        min_amount = self.importo_min.text().strip()
        max_amount = self.importo_max.text().strip()
        
        if min_amount:
            try:
                conditions.append("importo_netto >= ?")
                params.append(float(min_amount))
            except ValueError:
                pass
                
        if max_amount:
            try:
                conditions.append("importo_netto <= ?")
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
            # Usa lo stesso database del DatabaseManager
            from barflow.data.db_manager import get_db_path
            db_path = get_db_path()
            
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
                # Usa lo stesso database del DatabaseManager
                from barflow.data.db_manager import get_db_path
                db_path = get_db_path()
                
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

    def resizeEvent(self, event):
        """Gestisce il ridimensionamento del widget per ottimizzare la tabella."""
        super().resizeEvent(event)
        # Forza l'aggiornamento delle dimensioni delle colonne dopo il ridimensionamento
        if hasattr(self, 'table') and self.table.rowCount() > 0:
            # Aggiorna le dimensioni delle colonne che usano ResizeToContents
            for col in [0, 1, 3, 4, 5, 6, 7]:  # Colonne con ResizeToContents
                self.table.resizeColumnToContents(col)
    
    def _optimize_column_widths(self):
        """Ottimizza la larghezza delle colonne in base al contenuto."""
        # Ridimensiona le colonne con contenuto fisso
        for col in [0, 1, 3, 4, 5, 6, 7]:  # Escludi colonna 2 (FORNITORE) che usa Stretch
            self.table.resizeColumnToContents(col)
        
        # Imposta larghezze minime e massime per alcune colonne critiche
        header = self.table.horizontalHeader()
        
        # DATA: larghezza minima per le date
        if self.table.columnWidth(0) < 100:
            self.table.setColumnWidth(0, 100)
        
        # SORGENTE: larghezza massima ragionevole
        if self.table.columnWidth(1) > 100:
            self.table.setColumnWidth(1, 100)
        
        # Colonne numeriche: larghezza minima per leggibilità
        for col in [3, 4, 5, 6, 7]:
            if self.table.columnWidth(col) < 80:
                self.table.setColumnWidth(col, 80)