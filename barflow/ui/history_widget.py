from PySide6.QtWidgets import *
from PySide6.QtCore import QDate

class HistoryWidget(QWidget):
    """Widget per gestire lo storico delle transazioni."""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Statistiche database
        stats_group = QGroupBox("Statistiche Storico")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel()
        self.update_stats()
        stats_layout.addWidget(self.stats_label)
        
        # Filtri per periodo
        filter_group = QGroupBox("Filtri Periodo")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Da:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-3))
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("A:"))
        self.end_date = QDateEdit(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        
        load_period_btn = QPushButton("Carica Periodo")
        load_period_btn.clicked.connect(self.load_period)
        filter_layout.addWidget(load_period_btn)
        
        layout.addWidget(stats_group)
        layout.addWidget(filter_group)
    
    def update_stats(self):
        stats = self.db_manager.get_database_stats()
        text = f"""
        Transazioni totali: {stats['total_records']:,}
        Periodo: {stats['date_range'][0] or 'N/A'} - {stats['date_range'][1] or 'N/A'}
        Dimensione database: {stats['db_size_mb']} MB
        """
        self.stats_label.setText(text)
    
    def load_period(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        transactions = self.db_manager.load_transactions_by_period(start, end)
        
        # Emetti segnale per aggiornare le viste principali
        # (implementa Signal se necessario)
        QMessageBox.information(self, "Periodo caricato", 
                              f"Caricate {len(transactions)} transazioni per il periodo selezionato.")