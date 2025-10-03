
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class AnalysisWidget(QWidget):
    """Widget per la sezione di analisi dei dati."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente del widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # Layout per i box delle metriche
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.total_gains_label = self._create_metric_box("TOTALE GUADAGNI", "0.00 €", "#27AE60")
        self.total_expenses_label = self._create_metric_box("TOTALE SPESE", "0.00 €", "#C0392B")
        self.profit_label = self._create_metric_box("UTILE", "0.00 €", "#2980B9")
        
        metrics_layout.addWidget(self.total_gains_label)
        metrics_layout.addWidget(self.total_expenses_label)
        metrics_layout.addWidget(self.profit_label)
        
        # Contenitore per i box per limitarne l'altezza
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_layout)
        metrics_container.setFixedHeight(150)

        main_layout.addWidget(metrics_container)

        # Layout per i grafici
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        self.monthly_chart_canvas = self._create_chart_canvas()
        self.cumulative_profit_canvas = self._create_chart_canvas()

        charts_layout.addWidget(self.monthly_chart_canvas)
        charts_layout.addWidget(self.cumulative_profit_canvas)

        main_layout.addLayout(charts_layout)

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
        layout.setContentsMargins(20, 20, 20, 20)  # Aumentato il padding interno
        layout.setSpacing(10)  # Aumentato lo spazio tra title e value
        layout.setAlignment(Qt.AlignCenter)  # Centra il contenuto verticalmente
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Permette il wrapping del testo se necessario
        title_label.setStyleSheet("""
            color: white; 
            font-size: 16px; 
            font-weight: bold;
            margin: 0px;
            padding: 2px;
        """)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)  # Permette il wrapping del testo se necessario
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

    def _create_chart_canvas(self):
        """Crea un'area di disegno per un grafico Matplotlib."""
        fig, ax = plt.subplots()
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")
        return canvas

    def update_data(self, transactions_data):
        """Aggiorna i dati e ricalcola metriche e grafici."""
        if not transactions_data:
            self._reset_view()
            return

        try:
            df = pd.DataFrame(transactions_data)
            df['IMPORTO'] = pd.to_numeric(df['IMPORTO'], errors='coerce')
            df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')
            
            # Rimuovi righe con valori non validi
            df = df.dropna(subset=['IMPORTO', 'DATA'])

            # 1. Aggiorna le metriche
            total_gains = df[df['IMPORTO'] > 0]['IMPORTO'].sum()
            total_expenses = abs(df[df['IMPORTO'] < 0]['IMPORTO'].sum())  # Valore assoluto per le spese
            profit = total_gains - total_expenses

            # Trova e aggiorna i label dei valori usando l'objectName
            gains_value_label = self.total_gains_label.findChild(QLabel, "value_label")
            expenses_value_label = self.total_expenses_label.findChild(QLabel, "value_label")
            profit_value_label = self.profit_label.findChild(QLabel, "value_label")
            
            if gains_value_label:
                gains_value_label.setText(f"{total_gains:,.2f} €")
            if expenses_value_label:
                expenses_value_label.setText(f"{total_expenses:,.2f} €")
            if profit_value_label:
                profit_value_label.setText(f"{profit:,.2f} €")

            # 2. Aggiorna il grafico mensile
            self._update_monthly_chart(df)

            # 3. Aggiorna il grafico del profitto cumulativo
            self._update_cumulative_profit_chart(df)
            
        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati: {e}")
            self._reset_view()

    def _update_monthly_chart(self, df):
        """Aggiorna il grafico a barre mensile."""
        # Pulisci la figura esistente
        self.monthly_chart_canvas.figure.clear()
        ax = self.monthly_chart_canvas.figure.add_subplot(111)

        df['Mese'] = df['DATA'].dt.to_period('M')
        monthly_summary = df.groupby('Mese')['IMPORTO'].agg(
            entrate=lambda x: x[x > 0].sum(),
            uscite=lambda x: abs(x[x < 0].sum())  # Valore assoluto per le uscite
        ).reset_index()

        monthly_summary['Mese'] = monthly_summary['Mese'].astype(str)

        if len(monthly_summary) == 0:
            ax.text(0.5, 0.5, "Nessun dato mensile da visualizzare", ha='center', va='center', transform=ax.transAxes)
            self.monthly_chart_canvas.draw()
            return

        bar_width = 0.35
        index = range(len(monthly_summary['Mese']))

        ax.bar(index, monthly_summary['entrate'], bar_width, label='Entrate', color='#27AE60')
        ax.bar([i + bar_width for i in index], monthly_summary['uscite'], bar_width, label='Uscite', color='#C0392B')

        ax.set_title('Entrate vs Uscite Mensili', fontsize=12, fontweight='bold')
        ax.set_ylabel('Importo (€)')
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(monthly_summary['Mese'], rotation=45, ha="right")
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        self.monthly_chart_canvas.figure.tight_layout()
        self.monthly_chart_canvas.draw()

    def _update_cumulative_profit_chart(self, df):
        """Aggiorna il grafico a linee del profitto cumulativo."""
        # Pulisci la figura esistente
        self.cumulative_profit_canvas.figure.clear()
        ax = self.cumulative_profit_canvas.figure.add_subplot(111)

        if len(df) == 0:
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", ha='center', va='center', transform=ax.transAxes)
            self.cumulative_profit_canvas.draw()
            return

        df_sorted = df.sort_values('DATA')
        df_sorted['profitto_cumulativo'] = df_sorted['IMPORTO'].cumsum()

        ax.plot(df_sorted['DATA'], df_sorted['profitto_cumulativo'], marker='o', linestyle='-', color='#2980B9', markersize=4)
        
        ax.set_title('Andamento Profitto Cumulativo', fontsize=12, fontweight='bold')
        ax.set_ylabel('Profitto (€)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Formatta le etichette delle date
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        self.cumulative_profit_canvas.figure.tight_layout()
        self.cumulative_profit_canvas.draw()

    def _reset_view(self):
        """Resetta la vista quando non ci sono dati."""
        # Reset delle metriche usando l'objectName
        gains_value_label = self.total_gains_label.findChild(QLabel, "value_label")
        expenses_value_label = self.total_expenses_label.findChild(QLabel, "value_label")
        profit_value_label = self.profit_label.findChild(QLabel, "value_label")
        
        if gains_value_label:
            gains_value_label.setText("0.00 €")
        if expenses_value_label:
            expenses_value_label.setText("0.00 €")
        if profit_value_label:
            profit_value_label.setText("0.00 €")
        
        # Reset dei grafici
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas]:
            canvas.figure.clear()
            ax = canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", ha='center', va='center', transform=ax.transAxes)
            canvas.draw()
