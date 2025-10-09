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
    clear_temp_requested = Signal()  # Segnale emesso quando si clicca il tasto Elimina Tabella Temporanea

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
        self.clear_button = QPushButton("🗑️ Pulisci Tabella Temporanea")
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
        self.clear_button.clicked.connect(self.clear_temp_requested.emit)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

    def update_table(self, transactions_data):
        """Aggiorna la tabella con i dati delle transazioni in modo ottimizzato."""
        print(f"🔄 Aggiornamento tabella con {len(transactions_data)} transazioni...")
        
        # OTTIMIZZAZIONE 1: Disabilita temporaneamente il rendering per migliorare performance
        self.table.setUpdatesEnabled(False)
        
        try:
            # OTTIMIZZAZIONE 2: Pulisci completamente la tabella esistente
            self.table.clearContents()
            self.table.setRowCount(0)
            
            # Se non ci sono dati, esci subito
            if not transactions_data:
                print("✓ Tabella vuota")
                return
            
            # OTTIMIZZAZIONE 3: Ordina i dati (limitiamo a max 1000 record per performance)
            sorted_data = sorted(transactions_data, 
                               key=lambda x: x.get('_IMPORT_TIMESTAMP', 0), 
                               reverse=True)
            
            # Limita a 1000 record per evitare freeze dell'interfaccia
            if len(sorted_data) > 1000:
                sorted_data = sorted_data[:1000]
                print(f"⚠️ Mostrati solo i primi 1000 record di {len(transactions_data)} per performance")
            
            # OTTIMIZZAZIONE 4: Imposta la dimensione della tabella una sola volta
            self.table.setRowCount(len(sorted_data))

            # OTTIMIZZAZIONE 5: Disabilita il ridimensionamento automatico durante il popolamento
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Fixed)

            for row, transaction in enumerate(sorted_data):
                # Mostra progresso ogni 100 righe per debug
                if row % 100 == 0 and row > 0:
                    print(f"  Elaborando riga {row}/{len(sorted_data)}...")
                
                try:
                    # OTTIMIZZAZIONE 6: Creazione item più diretta, meno formattazione
                    items = []
                    
                    # DATA
                    items.append(QTableWidgetItem(str(transaction.get('DATA', ''))))
                    
                    # SORGENTE  
                    items.append(QTableWidgetItem(str(transaction.get('SORGENTE', ''))))
                    
                    # DESCRIZIONE (truncata)
                    desc_text = str(transaction.get('DESCRIZIONE', '') or '')
                    if len(desc_text) > 25:
                        desc_text = desc_text[:22] + "..."
                    desc_item = QTableWidgetItem(desc_text)
                    if transaction.get('DESCRIZIONE'):
                        desc_item.setToolTip(str(transaction.get('DESCRIZIONE', '')))
                    items.append(desc_item)
                    
                    # FORNITORE (truncato)
                    forn_text = str(transaction.get('FORNITORE', '') or '')
                    if len(forn_text) > 20:
                        forn_text = forn_text[:17] + "..."
                    forn_item = QTableWidgetItem(forn_text)
                    if transaction.get('FORNITORE'):
                        forn_item.setToolTip(str(transaction.get('FORNITORE', '')))
                    items.append(forn_item)
                    
                    # NUMERO FORNITORE
                    items.append(QTableWidgetItem(str(transaction.get('NUMERO FORNITORE', '') or '')))
                    
                    # NUMERO OPERAZIONE POS
                    pos_num = transaction.get('NUMERO OPERAZIONE POS', '')
                    items.append(QTableWidgetItem(str(pos_num) if pos_num else ''))
                    
                    # IMPORTO LORDO POS
                    lordo = transaction.get('IMPORTO LORDO POS')
                    lordo_str = f"{float(lordo):.2f} €" if lordo is not None else ""
                    items.append(QTableWidgetItem(lordo_str))
                    
                    # COMMISSIONE POS
                    comm = transaction.get('COMMISSIONE POS')
                    comm_str = f"{float(comm):.2f} €" if comm is not None else ""
                    items.append(QTableWidgetItem(comm_str))
                    
                    # IMPORTO NETTO
                    try:
                        netto_val = float(transaction.get('IMPORTO NETTO', 0))
                        netto_item = QTableWidgetItem(f"{netto_val:.2f} €")
                        # Colore solo per importo netto
                        if netto_val < 0:
                            netto_item.setForeground(QColor("red"))
                        else:
                            netto_item.setForeground(QColor("green"))
                        items.append(netto_item)
                    except (ValueError, TypeError):
                        items.append(QTableWidgetItem(str(transaction.get('IMPORTO NETTO', '0.00'))))
                    
                    # OTTIMIZZAZIONE 7: Imposta tutti gli item in una volta e allineamento minimo
                    for col, item in enumerate(items):
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, col, item)
                        
                except Exception as e:
                    print(f"Errore nella creazione della riga {row}: {e}")
                    # Crea celle vuote per evitare il crash
                    for col in range(9):
                        empty_item = QTableWidgetItem("")
                        empty_item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, col, empty_item)
            
            print(f"✓ Tabella popolata con {len(sorted_data)} righe")
            
        finally:
            # OTTIMIZZAZIONE 8: Riabilita il ridimensionamento solo alla fine
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # DATA
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # SORGENTE  
            header.setSectionResizeMode(2, QHeaderView.Interactive)  # DESCRIZIONE
            header.setSectionResizeMode(3, QHeaderView.Interactive)  # FORNITORE
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # NUMERO FORNITORE
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # NUMERO POS
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # LORDO
            header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # COMMISSIONE
            header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # NETTO
            
            # OTTIMIZZAZIONE 9: Riabilita gli aggiornamenti alla fine
            self.table.setUpdatesEnabled(True)
            
            print("✓ Aggiornamento tabella completato")

    def clear_table(self):
        """Pulisce la tabella riportandola allo stato iniziale vuoto."""
        print("🔄 Pulizia tabella...")
        self.table.setUpdatesEnabled(False)
        try:
            self.table.clearContents()
            self.table.setRowCount(0)
            print("✓ Tabella pulita")
        finally:
            self.table.setUpdatesEnabled(True)
    
    def resizeEvent(self, event):
        """Gestisce il ridimensionamento del widget per ottimizzare la tabella."""
        super().resizeEvent(event)
        # OTTIMIZZAZIONE: Rimosso il resize automatico per migliorare performance
        # Il ridimensionamento è ora gestito direttamente in update_table()
        pass
        pass
    
    # RIMOSSO: _optimize_column_widths() per migliorare performance
    # Il ridimensionamento è ora gestito direttamente nel metodo update_table()