"""
Widget per la visualizzazione delle transazioni
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QPushButton, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class TransactionsWidget(QWidget):
    """Widget per visualizzare le transazioni importate."""
    
    save_requested = Signal()  # Segnale emesso quando si clicca il tasto Salva

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente."""
        # Layout principale con margini ridotti per utilizzare più spazio
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "DATA", "SORGENTE", "DESCRIZIONE", "FORNITORE", "NUMERO FORNITORE", 
            "NUMERO OPERAZIONE POS", "IMPORTO LORDO POS", "COMMISSIONE POS", "IMPORTO NETTO"
        ])
        
        # Configurazione header responsive
        header = self.table.horizontalHeader()
        header.setSectionsClickable(False)   # Disabilita il click sui header
        
        # Imposta dimensioni responsive per le colonne
        # Alcune colonne hanno contenuto più importante e necessitano più spazio
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # DATA - contenuto fisso
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # SORGENTE - contenuto limitato
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # DESCRIZIONE - può essere lungo
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # FORNITORE - può essere lungo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # NUMERO FORNITORE - contenuto numerico
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # NUMERO OPERAZIONE POS - contenuto numerico
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # IMPORTO LORDO POS - contenuto numerico
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # COMMISSIONE POS - contenuto numerico
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # IMPORTO NETTO - contenuto numerico
        
        # Imposta larghezza minima per la colonna DESCRIZIONE per evitare che l'intestazione sia tagliata
        self.table.setColumnWidth(2, 120)  # Larghezza minima per DESCRIZIONE
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Permette ridimensionamento manuale
        header.setMinimumSectionSize(120)  # Larghezza minima globale per evitare compressione eccessiva
        
        # Rimuovi dimensioni fisse - ora la tabella si adatta al contenitore
        self.table.setMinimumHeight(400)  # Altezza minima ridotta ma ragionevole
        
        # Imposta policy di ridimensionamento per rendere la tabella espandibile
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configurazioni scrolling per gestire contenuto che eccede
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.table.setAlternatingRowColors(False)
        self.table.setGridStyle(Qt.NoPen)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
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
        """)
        
        # Aggiungi la tabella direttamente al layout principale
        main_layout.addWidget(self.table)
        
        # Layout per i pulsanti
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)  # Spazio tra i bottoni
        
        # Tasto Salva
        self.save_button = QPushButton("💾 Salva nello Storico")
        self.save_button.setFixedWidth(200)
        self.save_button.setFixedHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.save_button.clicked.connect(self.save_requested.emit)
        
        # Tasto Elimina tabella
        self.clear_button = QPushButton("🗑️ Elimina Tabella")
        self.clear_button.setFixedWidth(200)
        self.clear_button.setFixedHeight(40)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #EC7063;
            }
            QPushButton:pressed {
                background-color: #CB4335;
            }
        """)
        self.clear_button.clicked.connect(self.clear_table)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

    def update_table(self, transactions_data):
        """Aggiorna la tabella con i dati delle transazioni."""
        # Ordina i dati per timestamp di importazione decrescente (più recenti per primi)
        sorted_data = sorted(transactions_data, 
                           key=lambda x: x.get('_IMPORT_TIMESTAMP', 0), 
                           reverse=True)
        
        self.table.setRowCount(len(sorted_data))

        for row, transaction in enumerate(sorted_data):
            try:
                # Crea gli item e imposta allineamento centrato per tutti
                data_item = QTableWidgetItem(str(transaction.get('DATA', '')))
                data_item.setTextAlignment(Qt.AlignCenter)
                
                sorgente_item = QTableWidgetItem(str(transaction.get('SORGENTE', '')))
                sorgente_item.setTextAlignment(Qt.AlignCenter)
                
                # Per la descrizione, trunca il testo se troppo lungo per migliore visualizzazione
                descrizione_text = str(transaction.get('DESCRIZIONE', '') or '')
                if len(descrizione_text) > 25:
                    descrizione_text = descrizione_text[:22] + "..."
                descrizione_item = QTableWidgetItem(descrizione_text)
                descrizione_item.setTextAlignment(Qt.AlignCenter)
                # Imposta il tooltip con il testo completo
                descrizione_item.setToolTip(str(transaction.get('DESCRIZIONE', '') or ''))
                
                # Per il fornitore, trunca il testo se troppo lungo per migliore visualizzazione
                fornitore_text = str(transaction.get('FORNITORE', '') or '')
                if len(fornitore_text) > 20:
                    fornitore_text = fornitore_text[:17] + "..."
                fornitore_item = QTableWidgetItem(fornitore_text)
                fornitore_item.setTextAlignment(Qt.AlignCenter)
                # Imposta il tooltip con il testo completo
                fornitore_item.setToolTip(str(transaction.get('FORNITORE', '') or ''))
                
                numero_fornitore_item = QTableWidgetItem(str(transaction.get('NUMERO FORNITORE', '') or ''))
                numero_fornitore_item.setTextAlignment(Qt.AlignCenter)
                
                # Gestisci numeri molto grandi per NUMERO OPERAZIONE POS convertendo sempre in stringa
                numero_pos_value = transaction.get('NUMERO OPERAZIONE POS', '')
                if numero_pos_value is not None and numero_pos_value != '':
                    numero_pos_str = str(numero_pos_value)
                else:
                    numero_pos_str = ''
                numero_pos_item = QTableWidgetItem(numero_pos_str)
                numero_pos_item.setTextAlignment(Qt.AlignCenter)
                
                # Gestione importo lordo POS (può essere None)
                importo_lordo = transaction.get('IMPORTO LORDO POS')
                if importo_lordo is not None:
                    try:
                        importo_lordo_str = f"{float(importo_lordo):.2f} €"
                    except (ValueError, TypeError):
                        importo_lordo_str = str(importo_lordo) if importo_lordo != '' else ""
                else:
                    importo_lordo_str = ""
                importo_lordo_item = QTableWidgetItem(importo_lordo_str)
                importo_lordo_item.setTextAlignment(Qt.AlignCenter)
                
                # Gestione commissione POS (può essere None)
                commissione = transaction.get('COMMISSIONE POS')
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
                importo_netto_str = transaction.get('IMPORTO NETTO', '0.0')
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
                for col in range(9):
                    empty_item = QTableWidgetItem("")
                    empty_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, empty_item)
        
        # Dopo aver popolato la tabella, ottimizza le dimensioni delle colonne
        self._optimize_column_widths()

    def clear_table(self):
        """Pulisce la tabella riportandola allo stato iniziale vuoto."""
        self.table.setRowCount(0)
        self.table.clearContents()
    
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