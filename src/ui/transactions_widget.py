"""
Widget per la visualizzazione delle transazioni
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Data", "Descrizione", "Importo", "Fonte"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setGridStyle(Qt.NoPen)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)

    def update_table(self, transactions_data):
        """Aggiorna la tabella con i dati delle transazioni."""
        self.table.setRowCount(len(transactions_data))

        for row, transaction in enumerate(transactions_data):
            date_item = QTableWidgetItem(transaction.get('transaction_date', ''))
            desc_item = QTableWidgetItem(transaction.get('description', ''))
            
            amount_str = transaction.get('amount', '0.0')
            amount_val = float(amount_str)
            amount_item = QTableWidgetItem(f"{amount_val:.2f} €")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if amount_val < 0:
                amount_item.setForeground(QColor("red"))
            else:
                amount_item.setForeground(QColor("green"))

            source_item = QTableWidgetItem(transaction.get('Fonte', ''))

            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, desc_item)
            self.table.setItem(row, 2, amount_item)
            self.table.setItem(row, 3, source_item)