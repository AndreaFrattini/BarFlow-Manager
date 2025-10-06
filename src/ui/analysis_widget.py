from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib import patheffects
import seaborn as sns
from .historical_analysis_widget import HistoricalAnalysisWidget

class AnalysisWidget(QWidget):
    """Widget per la sezione di analisi dei dati con tab per analisi attuale e storica."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente del widget con tab."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Crea il widget con i tab
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C0C0C0;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border: 1px solid #C0C0C0;
                border-bottom-color: #C0C0C0;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                color: #2C3E50;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
                border-top: 2px solid #3498DB;
                color: #2C3E50;
            }
            QTabBar::tab:hover {
                background-color: #F0F0F0;
                color: #2C3E50;
            }
        """)

        # Crea il widget per l'analisi attuale (quello esistente)
        self.current_analysis_widget = self._create_current_analysis_widget()
        
        # Crea il widget per l'analisi storica
        self.historical_analysis_widget = HistoricalAnalysisWidget()
        
        # Aggiungi i tab
        self.tab_widget.addTab(self.current_analysis_widget, "📊 Analisi Attuale")
        self.tab_widget.addTab(self.historical_analysis_widget, "📈 Analisi Storico")
        
        # Connetti il cambio di tab per aggiornare dinamicamente l'analisi storica
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        main_layout.addWidget(self.tab_widget)

    def _create_current_analysis_widget(self):
        """Crea il widget per l'analisi attuale (contenuto originale)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

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

        layout.addWidget(metrics_container)

        # Layout per i grafici
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        self.monthly_chart_canvas = self._create_chart_canvas()
        self.cumulative_profit_canvas = self._create_chart_canvas()

        charts_layout.addWidget(self.monthly_chart_canvas)
        charts_layout.addWidget(self.cumulative_profit_canvas)

        layout.addLayout(charts_layout)
        
        return widget

    def _on_tab_changed(self, index):
        """Gestisce il cambio di tab per aggiornare dinamicamente i dati storici."""
        # Se viene selezionato il tab "Analisi Storico" (indice 1)
        if index == 1:
            # Aggiorna i dati storici caricandoli dal database al momento
            self.historical_analysis_widget.update_data()

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
        """Crea un'area di disegno per un grafico Matplotlib con stile moderno."""
        # Imposta lo stile moderno per matplotlib
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            try:
                plt.style.use('seaborn-whitegrid')
            except:
                plt.style.use('default')
        
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')
        
        # Rimuovi i bordi superiore e destro per un look più pulito
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CCCCCC')
        ax.spines['bottom'].set_color('#CCCCCC')
        
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("""
            background-color: #FAFAFA; 
            border-radius: 15px;
            border: 1px solid #E0E0E0;
        """)
        return canvas

    def update_data(self, transactions_data):
        """Aggiorna i dati e ricalcola metriche e grafici per l'analisi attuale."""
        if not transactions_data:
            self._reset_view()
            return

        try:
            df = pd.DataFrame(transactions_data)
            df['IMPORTO'] = pd.to_numeric(df['IMPORTO'], errors='coerce')
            df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m-%d', errors='coerce')
            
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
        """Aggiorna il grafico a barre mensile con stile moderno ed elegante."""
        # Pulisci la figura esistente
        self.monthly_chart_canvas.figure.clear()
        ax = self.monthly_chart_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.monthly_chart_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        df['Mese'] = df['DATA'].dt.to_period('M')
        monthly_summary = df.groupby('Mese')['IMPORTO'].agg(
            entrate=lambda x: x[x > 0].sum(),
            uscite=lambda x: abs(x[x < 0].sum())  # Valore assoluto per le uscite
        ).reset_index()

        # Converti il periodo in datetime per formattazione consistente
        monthly_summary['Mese_dt'] = monthly_summary['Mese'].dt.to_timestamp()
        monthly_summary['Mese_label'] = monthly_summary['Mese_dt'].dt.strftime('%b %Y')

        if len(monthly_summary) == 0:
            ax.text(0.5, 0.5, "Nessun dato mensile da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            self.monthly_chart_canvas.draw()
            return

        # Colori moderni e gradienti
        colors_entrate = ['#27AE60', '#2ECC71', '#58D68D']  # Verde sfumato
        colors_uscite = ['#E74C3C', '#EC7063', '#F1948A']   # Rosso sfumato
        
        bar_width = 0.35
        index = np.arange(len(monthly_summary['Mese_label']))

        # Barre con effetti ombra e gradiente
        bars1 = ax.bar(index - bar_width/2, monthly_summary['entrate'], bar_width, 
                      label='Entrate', color=colors_entrate[0], alpha=0.9,
                      edgecolor='white', linewidth=2)
        bars2 = ax.bar(index + bar_width/2, monthly_summary['uscite'], bar_width, 
                      label='Uscite', color=colors_uscite[0], alpha=0.9,
                      edgecolor='white', linewidth=2)

        # Aggiungi valori sopra le barre
        def add_value_labels(bars, values):
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.annotate(f'€{value:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 5),  # 5 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=10, fontweight='bold', color='#333333')
        
        add_value_labels(bars1, monthly_summary['entrate'])
        add_value_labels(bars2, monthly_summary['uscite'])

        # Styling moderno
        ax.set_title('Entrate vs Uscite Mensili', fontsize=16, fontweight='bold', 
                    color='#2C3E50', pad=20)
        ax.set_ylabel('Importo (€)', fontsize=12, color='#34495E', fontweight='bold')
        ax.set_xlabel('Mese', fontsize=12, color='#34495E', fontweight='bold')
        
        ax.set_xticks(index)
        ax.set_xticklabels(monthly_summary['Mese_label'], rotation=45, ha="right", 
                          fontsize=11, color='#2C3E50')
        
        # Aumenta il margine inferiore per le etichette inclinate
        plt.subplots_adjust(bottom=0.15)
        
        # Legenda in alto a sinistra con dimensioni ulteriormente ridotte
        legend = ax.legend(loc='upper left', 
                          frameon=True, fancybox=True, shadow=True, 
                          fontsize=7, borderpad=0.1, handlelength=0.8, 
                          handletextpad=0.2, columnspacing=0.3)
        legend.get_frame().set_facecolor('#F8F9FA')
        legend.get_frame().set_edgecolor('#BDC3C7')
        legend.get_frame().set_linewidth(0.5)
        legend.get_frame().set_alpha(0.9)
        
        # Griglia elegante
        ax.grid(axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
        ax.set_axisbelow(True)
        
        # Rimuovi bordi superiore e destro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Formattazione assi
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.tick_params(colors='#2C3E50', which='both')
        
        # Aggiusta il layout (rimuove la regolazione per legenda esterna)
        self.monthly_chart_canvas.figure.subplots_adjust(bottom=0.15)
        self.monthly_chart_canvas.figure.tight_layout(pad=2.0)
        self.monthly_chart_canvas.draw()

    def _update_cumulative_profit_chart(self, df):
        """Aggiorna il grafico a linee del profitto cumulativo con stile moderno ed elegante."""
        # Pulisci la figura esistente
        self.cumulative_profit_canvas.figure.clear()
        ax = self.cumulative_profit_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.cumulative_profit_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        if len(df) == 0:
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            self.cumulative_profit_canvas.draw()
            return

        df_sorted = df.sort_values('DATA')
        df_sorted['profitto_cumulativo'] = df_sorted['IMPORTO'].cumsum()

        # Linea principale con gradiente
        line = ax.plot(df_sorted['DATA'], df_sorted['profitto_cumulativo'], 
                      linewidth=3, color='#3498DB', alpha=0.9, 
                      marker='o', markersize=5, markerfacecolor='#2980B9',
                      markeredgecolor='white', markeredgewidth=1.5,
                      label='Profitto Cumulativo')
        
        # Area sotto la curva per effetto visivo con colore dinamico
        # Usa verde se il valore finale è positivo, rosso se negativo
        final_value = df_sorted['profitto_cumulativo'].iloc[-1]
        area_color = '#27AE60' if final_value >= 0 else '#E74C3C'
        ax.fill_between(df_sorted['DATA'], df_sorted['profitto_cumulativo'], 0, 
                       alpha=0.2, color=area_color)
        
        # Linea dello zero per riferimento
        ax.axhline(y=0, color='#95A5A6', linestyle='--', linewidth=2, alpha=0.7)
        
        # Aggiungi valori lungo la linea (ogni N punti per evitare sovraffollamento)
        total_points = len(df_sorted)
        step = max(1, total_points // 8)  # Mostra circa 8 etichette massimo
        
        for i in range(0, total_points, step):
            row = df_sorted.iloc[i]
            value = row['profitto_cumulativo']
            date = row['DATA']
            
            # Posizione dell'etichetta alternata sopra/sotto la linea
            offset_y = 15 if i % 2 == 0 else -25
            va = 'bottom' if i % 2 == 0 else 'top'
            
            ax.annotate(f'€{value:,.0f}', 
                       xy=(date, value),
                       xytext=(0, offset_y), textcoords='offset points',
                       ha='center', va=va,
                       fontsize=8, fontweight='bold', color='#34495E',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                alpha=0.8, edgecolor='#BDC3C7', linewidth=0.5))
        
        # Styling moderno
        ax.set_title('Andamento Profitto Cumulativo', fontsize=16, fontweight='bold', 
                    color='#2C3E50', pad=20)
        ax.set_ylabel('Profitto (€)', fontsize=12, color='#34495E', fontweight='bold')
        ax.set_xlabel('Data', fontsize=12, color='#34495E', fontweight='bold')
        
        # Griglia elegante
        ax.grid(True, linestyle='--', alpha=0.3, color='#BDC3C7')
        ax.set_axisbelow(True)
        
        # Rimuovi bordi superiore e destro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Migliora i tick delle date per formato uniforme Gen 2025, Feb 2025, etc.
        total_days = (df_sorted['DATA'].max() - df_sorted['DATA'].min()).days
        
        if total_days <= 31:
            # Meno di un mese: mostra ogni settimana con formato breve
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        elif total_days <= 90:
            # Meno di 3 mesi: mostra ogni 2 settimane
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        else:
            # Più di 3 mesi: mostra mensilmente con formato uniforme
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        
        # Inclina le etichette per migliore leggibilità
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", color='#2C3E50')
        
        # Formattazione asse Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.tick_params(colors='#2C3E50', which='both')
        
        # Aumenta il margine inferiore per le etichette inclinate
        self.cumulative_profit_canvas.figure.subplots_adjust(bottom=0.15)
        self.cumulative_profit_canvas.figure.tight_layout(pad=2.0)
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
        
        # Reset dei grafici con stile moderno
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            canvas.draw()
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
        
        # Reset dei grafici con stile moderno
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            canvas.draw()
            self._style_empty_chart(ax)
            canvas.draw()
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
        
        # Reset dei grafici con stile moderno
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            canvas.draw()

    def _style_empty_chart(self, ax):
        """Applica stile moderno ai grafici vuoti."""
        # Rimuovi i bordi superiore e destro per un look più pulito
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CCCCCC')
        ax.spines['bottom'].set_color('#CCCCCC')
        
        # Rimuovi tick e etichette
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
