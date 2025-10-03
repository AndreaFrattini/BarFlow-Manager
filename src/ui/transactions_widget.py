"""
Widget per la visualizzazione delle transazioni
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class TransactionsWidget(QWidget):
    """Widget per visualizzare le transazioni importate."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente."""
        # Layout principale con margini ridotti per utilizzare più spazio
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Layout orizzontale per centrare la tabella
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["DATA", "SORGENTE", "PRODOTTO", "FORNITORE", "CATEGORIA", "QUANTITA'", "IMPORTO"])
        
        # Configurazione header per distribuire uniformemente le colonne
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)   # Permette l'espansione per riempire spazio
        header.setSectionsClickable(False)   # Disabilita il click sui header
        
        # Usa Stretch per tutte le colonne per distribuire uniformemente lo spazio
        for col in range(7):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        
        # Imposta dimensione fissa della tabella per occupare la maggior parte dello spazio
        self.table.setFixedWidth(1000)  # Larghezza fissa ridotta
        self.table.setMinimumHeight(500)  # Altezza minima per occupare spazio verticale
        
        # Configurazioni aggiuntive per evitare colonne extra
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Assicurati che la tabella sia esattamente delle dimensioni necessarie
        self.table.resizeColumnsToContents()
        
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
                background-color: grey;
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
        
        # Aggiungi la tabella al layout orizzontale
        h_layout.addWidget(self.table)
        
        # Aggiungi il layout orizzontale al layout principale
        main_layout.addLayout(h_layout)

    def update_table(self, transactions_data):
        """Aggiorna la tabella con i dati delle transazioni."""
        self.table.setRowCount(len(transactions_data))

        for row, transaction in enumerate(transactions_data):
            # Crea gli item e imposta allineamento centrato per tutti
            data_item = QTableWidgetItem(transaction.get('DATA', ''))
            data_item.setTextAlignment(Qt.AlignCenter)
            
            sorgente_item = QTableWidgetItem(transaction.get('SORGENTE', ''))
            sorgente_item.setTextAlignment(Qt.AlignCenter)
            
            prodotto_item = QTableWidgetItem(transaction.get('PRODOTTO', ''))
            prodotto_item.setTextAlignment(Qt.AlignCenter)
            
            fornitore_item = QTableWidgetItem(transaction.get('FORNITORE', ''))
            fornitore_item.setTextAlignment(Qt.AlignCenter)
            
            categoria_item = QTableWidgetItem(transaction.get('CATEGORIA', ''))
            categoria_item.setTextAlignment(Qt.AlignCenter)
            
            quantita_item = QTableWidgetItem(str(transaction.get('QUANTITA\'', '')))
            quantita_item.setTextAlignment(Qt.AlignCenter)
            
            importo_str = transaction.get('IMPORTO', '0.0')
            importo_val = float(importo_str)
            importo_item = QTableWidgetItem(f"{importo_val:.2f} €")
            importo_item.setTextAlignment(Qt.AlignCenter)  # Centra anche l'importo per uniformità

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