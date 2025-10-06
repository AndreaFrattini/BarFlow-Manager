"""
Widget per l'analisi dei dati storici dal database.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
import pandas as pd
from .database_manager import DatabaseManager

class HistoricalAnalysisWidget(QWidget):
    """Widget per l'analisi dei dati storici."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente del widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # Layout per i box delle metriche
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.total_gains_label = self._create_metric_box("TOTALE ENTRATE", "0.00 €", "#27AE60")
        self.total_expenses_label = self._create_metric_box("TOTALE USCITE", "0.00 €", "#C0392B")
        self.profit_label = self._create_metric_box("PROFITTO", "0.00 €", "#2980B9")
        
        metrics_layout.addWidget(self.total_gains_label)
        metrics_layout.addWidget(self.total_expenses_label)
        metrics_layout.addWidget(self.profit_label)
        
        # Contenitore per i box per limitarne l'altezza
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_layout)
        metrics_container.setFixedHeight(150)

        main_layout.addWidget(metrics_container)
        
        # Non caricare automaticamente i dati - verranno caricati solo quando necessario

    def _create_metric_box(self, title, value, color):
        """Crea un box per una metrica specifica."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            color: white; 
            font-size: 16px; 
            font-weight: bold;
            margin: 0px;
            padding: 2px;
        """)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("""
            color: white; 
            font-size: 24px; 
            font-weight: bold;
            margin: 0px;
            padding: 2px;
        """)
        # Aggiungi un nome oggetto per identificare facilmente il label del valore
        value_label.setObjectName("value_label")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return frame

    def update_data(self):
        """Aggiorna i dati caricando le transazioni storiche dal database."""
        try:
            # Carica tutti i dati storici dal database
            historical_data = self.db_manager.load_all_transactions()
            
            if not historical_data:
                self._reset_view()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO'] = pd.to_numeric(df['IMPORTO'], errors='coerce')
            df = df.dropna(subset=['IMPORTO'])

            # Calcola le metriche
            total_gains = df[df['IMPORTO'] > 0]['IMPORTO'].sum()
            total_expenses = abs(df[df['IMPORTO'] < 0]['IMPORTO'].sum())
            profit = total_gains - total_expenses

            # Aggiorna i label
            gains_value_label = self.total_gains_label.findChild(QLabel, "value_label")
            expenses_value_label = self.total_expenses_label.findChild(QLabel, "value_label")
            profit_value_label = self.profit_label.findChild(QLabel, "value_label")
            
            if gains_value_label:
                gains_value_label.setText(f"{total_gains:,.2f} €")
            if expenses_value_label:
                expenses_value_label.setText(f"{total_expenses:,.2f} €")
            if profit_value_label:
                profit_value_label.setText(f"{profit:,.2f} €")
                
        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati storici: {e}")
            self._reset_view()

    def _reset_view(self):
        """Resetta la vista quando non ci sono dati."""
        gains_value_label = self.total_gains_label.findChild(QLabel, "value_label")
        expenses_value_label = self.total_expenses_label.findChild(QLabel, "value_label")
        profit_value_label = self.profit_label.findChild(QLabel, "value_label")
        
        if gains_value_label:
            gains_value_label.setText("0.00 €")
        if expenses_value_label:
            expenses_value_label.setText("0.00 €")
        if profit_value_label:
            profit_value_label.setText("0.00 €")