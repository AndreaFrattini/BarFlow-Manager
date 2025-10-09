"""
Widget per l'analisi dei dati storici dal database.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget
from PySide6.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from barflow.data.db_manager import DatabaseManager
from .analysis_utils import (
    create_metric_box, 
    create_chart_canvas, 
    style_empty_chart, 
    parse_date_robust,
    update_metric_box_value,
    create_info_button
)

class HistoricalAnalysisWidget(QWidget):
    """Widget per l'analisi dei dati storici."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente del widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(3)

        # Layout per i box delle metriche (rimpiccioliti)
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        self.total_gains_label = create_metric_box("TOTALE ENTRATE", "0.00 €", "#27AE60")
        self.total_expenses_label = create_metric_box("TOTALE USCITE", "0.00 €", "#C0392B")
        self.profit_label = create_metric_box("PROFITTO", "0.00 €", "#2980B9")
        
        metrics_layout.addWidget(self.total_gains_label)
        metrics_layout.addWidget(self.total_expenses_label)
        metrics_layout.addWidget(self.profit_label)
        
        # Contenitore per i box con altezza ridotta
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_layout)
        metrics_container.setFixedHeight(60)

        main_layout.addWidget(metrics_container)
        
        # Crea il widget con tab
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C0C0C0;
                background-color: #FAFAFA;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border: 1px solid #C0C0C0;
                padding: 4px 12px;
                margin-right: 2px;
                border-radius: 5px 5px 0px 0px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #FAFAFA;
                border-bottom-color: #FAFAFA;
            }
            QTabBar::tab:hover {
                background-color: #F0F0F0;
            }
        """)
        
        # Tab "Entrate vs Uscite"
        self.historical_tab = QWidget()
        self._setup_historical_tab()
        self.tab_widget.addTab(self.historical_tab, "Entrate vs Uscite")
        
        # Tab "Andamento Temporale"
        self.performance_tab = QWidget()
        self._setup_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "Andamento Temporale")
        
        # Tab "Analisi per Fornitore"
        self.supplier_tab = QWidget()
        self._setup_supplier_tab()
        self.tab_widget.addTab(self.supplier_tab, "Analisi per Fornitore")
        
        main_layout.addWidget(self.tab_widget)
        
        # Non caricare automaticamente i dati - verranno caricati solo quando necessario

    def _setup_historical_tab(self):
        """Configura la tab 'Entrate vs Uscite'."""
        layout = QHBoxLayout(self.historical_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Container per il primo grafico con titolo e bottone info
        monthly_chart_container = QWidget()
        monthly_container_layout = QVBoxLayout(monthly_chart_container)
        monthly_container_layout.setContentsMargins(0, 0, 0, 0)
        monthly_container_layout.setSpacing(5)
        
        # Layout per titolo + bottone info
        monthly_title_layout = QHBoxLayout()
        monthly_title_layout.setContentsMargins(10, 5, 10, 0)
        monthly_title_layout.setSpacing(8)
        
        monthly_title_label = QLabel("Entrate vs Uscite Mensili")
        monthly_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 20px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        monthly_info_btn = create_info_button(
            "Questo grafico mostra la somma delle entrate (in verde) e delle uscite (in rosso) per il periodo di riferimento mostrato sull'asse delle x (asse orizzontale)."
        )
        
        # Centra il gruppo titolo + bottone
        monthly_title_layout.addStretch()
        monthly_title_layout.addWidget(monthly_title_label)
        monthly_title_layout.addWidget(monthly_info_btn)
        monthly_title_layout.addStretch()
        
        # Grafico Entrate vs Uscite Mensili
        self.monthly_chart_canvas = create_chart_canvas()
        
        monthly_container_layout.addLayout(monthly_title_layout)
        monthly_container_layout.addWidget(self.monthly_chart_canvas)
        
        layout.addWidget(monthly_chart_container)

        # Container per il secondo grafico con titolo e bottone info
        performance_chart_container = QWidget()
        performance_container_layout = QVBoxLayout(performance_chart_container)
        performance_container_layout.setContentsMargins(0, 0, 0, 0)
        performance_container_layout.setSpacing(5)
        
        # Layout per titolo + bottone info del secondo grafico
        performance_title_layout = QHBoxLayout()
        performance_title_layout.setContentsMargins(10, 5, 10, 0)
        performance_title_layout.setSpacing(8)
        
        performance_title_label = QLabel("Performance Media Giornaliera")
        performance_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 20px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        performance_info_btn = create_info_button(
            """Questo grafico mostra le entrate medie per ogni giorno della settimana (barre verdi) nel periodo di tempo mostrato sull'asse orizzontale del grafico a sinistra 'Entrate vs Uscite Mensili'. La linea tratteggiata rossa orizzontale invece è la media delle spese giornaliere.

Come si legge questo grafico? Come dice la legenda in alto a sinistra, la linea rossa, detta 'Obiettivo Pareggio' è l'obiettivo da raggiungere o superare per andare in guadagno ogni singolo giorno della settimana. In poche parole, ogni volta che apri la serranda spendi la cifra indicata dalla linea rossa e per andare in positivo devi superarla ogni giorno della settimana.

Questo grafico risulta estremamente utile per capire quali sono i giorni della settimana in cui vi sono più e meno incassi, identificando così punti forti e deboli dell'attività."""
        )
        
        # Centra il gruppo titolo + bottone
        performance_title_layout.addStretch()
        performance_title_layout.addWidget(performance_title_label)
        performance_title_layout.addWidget(performance_info_btn)
        performance_title_layout.addStretch()
        
        # Grafico Performance Media Giornaliera
        self.daily_performance_canvas = create_chart_canvas()
        
        performance_container_layout.addLayout(performance_title_layout)
        performance_container_layout.addWidget(self.daily_performance_canvas)
        
        layout.addWidget(performance_chart_container)

    def _setup_performance_tab(self):
        """Configura la tab 'Andamento Temporale'."""
        layout = QVBoxLayout(self.performance_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Container per il primo grafico con titolo e bottone info
        cumulative_chart_container = QWidget()
        cumulative_container_layout = QVBoxLayout(cumulative_chart_container)
        cumulative_container_layout.setContentsMargins(0, 0, 0, 0)
        cumulative_container_layout.setSpacing(0.1)
        
        # Layout per titolo + bottone info
        cumulative_title_layout = QHBoxLayout()
        cumulative_title_layout.setContentsMargins(10, 0.3, 10, 0)
        cumulative_title_layout.setSpacing(8)
        
        cumulative_title_label = QLabel("Andamento Profitto Cumulativo")
        cumulative_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        cumulative_info_btn = create_info_button(
            "Questo grafico mostra quanto profitto è stato fatto ogni giorno. Se sotto lo zero significa che la giornata è stata chiusa in perdita, altrimenti se sopra lo zero, in guadagno."
        )
        
        # Centra il gruppo titolo + bottone
        cumulative_title_layout.addStretch()
        cumulative_title_layout.addWidget(cumulative_title_label)
        cumulative_title_layout.addWidget(cumulative_info_btn)
        cumulative_title_layout.addStretch()
        
        # Grafico Andamento Profitto Cumulativo (in alto)
        self.cumulative_profit_canvas = create_chart_canvas()
        
        cumulative_container_layout.addLayout(cumulative_title_layout)
        cumulative_container_layout.addWidget(self.cumulative_profit_canvas)
        
        layout.addWidget(cumulative_chart_container)

        # Container per il secondo grafico con titolo e bottone info
        average_chart_container = QWidget()
        average_container_layout = QVBoxLayout(average_chart_container)
        average_container_layout.setContentsMargins(0, 0, 0, 0)
        average_container_layout.setSpacing(0.1)
        
        # Layout per titolo + bottone info del secondo grafico
        average_title_layout = QHBoxLayout()
        average_title_layout.setContentsMargins(10, 0.3, 10, 0)
        average_title_layout.setSpacing(8)
        
        average_title_label = QLabel("Performance Medie 2025")
        average_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        average_info_btn = create_info_button(
            """Questo grafico mostra la media delle entrate e delle uscite nel tempo e quindi evidenzia il 'trend' che la tua attività sta avendo: se le linee verde o blu stanno salendo vuol dire che in media le entrate e i profitti stanno aumentando nel tempo (viceversa se stanno scendendo) e stesso discorso per le uscite, quando la linea va verso l'alto vuol dire che le uscite stanno aumentando nel tempo (viceversa diminuiscono se la linea va verso il basso).

Risulta dunque un grafico molto interessante per capire se il piano di business che si sta attuando è sostenibile nel tempo o se poterà alla bancarotta."""
        )
        
        # Centra il gruppo titolo + bottone
        average_title_layout.addStretch()
        average_title_layout.addWidget(average_title_label)
        average_title_layout.addWidget(average_info_btn)
        average_title_layout.addStretch()
        
        # Grafico Performance Medie (in basso)
        self.average_performance_canvas = create_chart_canvas()
        
        average_container_layout.addLayout(average_title_layout)
        average_container_layout.addWidget(self.average_performance_canvas)
        
        layout.addWidget(average_chart_container)

    def _setup_supplier_tab(self):
        """Configura la tab 'Analisi per Fornitore'."""
        layout = QHBoxLayout(self.supplier_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Container per il primo grafico con titolo e bottone info - Top Fornitori per Spesa
        top_suppliers_container = QWidget()
        top_suppliers_layout = QVBoxLayout(top_suppliers_container)
        top_suppliers_layout.setContentsMargins(0, 0, 0, 0)
        top_suppliers_layout.setSpacing(2)
        
        # Layout per titolo + bottone info
        top_suppliers_title_layout = QHBoxLayout()
        top_suppliers_title_layout.setContentsMargins(10, 3, 10, 0)
        top_suppliers_title_layout.setSpacing(8)
        
        top_suppliers_title_label = QLabel("Top Fornitori per Spesa")
        top_suppliers_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 20px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        top_suppliers_info_btn = create_info_button(
            "Questo grafico mostra i fornitori che costano di più in termini di spesa totale nel periodo analizzato. Ti aiuta a identificare i fornitori che hanno il maggiore impatto sui costi dell'attività e a valutare possibili ottimizzazioni o negoziazioni."
        )
        
        # Centra il gruppo titolo + bottone
        top_suppliers_title_layout.addStretch()
        top_suppliers_title_layout.addWidget(top_suppliers_title_label)
        top_suppliers_title_layout.addWidget(top_suppliers_info_btn)
        top_suppliers_title_layout.addStretch()
        
        # Grafico Top Fornitori per Spesa
        self.top_suppliers_canvas = create_chart_canvas()
        
        top_suppliers_layout.addLayout(top_suppliers_title_layout)
        top_suppliers_layout.addWidget(self.top_suppliers_canvas)
        
        # Container per il secondo grafico con titolo e bottone info - Frequenza Ordini per Fornitore
        supplier_frequency_container = QWidget()
        supplier_frequency_layout = QVBoxLayout(supplier_frequency_container)
        supplier_frequency_layout.setContentsMargins(0, 0, 0, 0)
        supplier_frequency_layout.setSpacing(2)
        
        # Layout per titolo + bottone info del secondo grafico
        frequency_title_layout = QHBoxLayout()
        frequency_title_layout.setContentsMargins(10, 3, 10, 0)
        frequency_title_layout.setSpacing(8)
        
        frequency_title_label = QLabel("Frequenza Ordini per Fornitore")
        frequency_title_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 20px;
            font-weight: bold;
            margin: 0px;
            padding: 0px;
        """)
        
        frequency_info_btn = create_info_button(
            "Questo grafico mostra da quali fornitori ci si rifornisce più spesso, contando il numero di transazioni/ordini effettuati. Ti aiuta a identificare i partner commerciali più frequenti e a valutare la diversificazione dei fornitori per ridurre i rischi di dipendenza."
        )
        
        # Centra il gruppo titolo + bottone
        frequency_title_layout.addStretch()
        frequency_title_layout.addWidget(frequency_title_label)
        frequency_title_layout.addWidget(frequency_info_btn)
        frequency_title_layout.addStretch()
        
        # Grafico Frequenza Ordini per Fornitore
        self.supplier_frequency_canvas = create_chart_canvas()
        
        supplier_frequency_layout.addLayout(frequency_title_layout)
        supplier_frequency_layout.addWidget(self.supplier_frequency_canvas)
        
        layout.addWidget(top_suppliers_container)
        layout.addWidget(supplier_frequency_container)

    def update_data(self):
        """Aggiorna i dati caricando le transazioni storiche dal database."""
        try:
            # Carica tutti i dati storici dal database
            historical_data = self.db_manager.load_all_transactions()
            
            if not historical_data:
                self._reset_view()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
            
            # Applica parsing robusto delle date usando la utility function
            df['DATA'] = df['DATA'].apply(parse_date_robust)
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            if len(df) == 0:
                self._reset_view()
                return

            # Calcola le metriche
            total_gains = df[df['IMPORTO NETTO'] > 0]['IMPORTO NETTO'].sum()
            total_expenses = abs(df[df['IMPORTO NETTO'] < 0]['IMPORTO NETTO'].sum())
            profit = total_gains - total_expenses

            # Aggiorna i label utilizzando le utility functions
            update_metric_box_value(self.total_gains_label, f"{total_gains:,.2f} €")
            update_metric_box_value(self.total_expenses_label, f"{total_expenses:,.2f} €")
            update_metric_box_value(self.profit_label, f"{profit:,.2f} €")

            # Aggiorna i grafici
            self._update_monthly_chart(df)
            self._update_cumulative_profit_chart(df)
            self._update_daily_performance_chart()
            self._update_average_performance_chart()
            self._update_supplier_charts(df)
                
        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati storici: {e}")
            import traceback
            traceback.print_exc()
            # Non fare crash dell'app, solo resetta la vista
            self._reset_view()
            
            # Opzionalmente, mostra un messaggio di errore negli stessi grafici
            self._show_error_in_charts("Errore nel caricamento dati storici")

    def _update_monthly_chart(self, df):
        """Aggiorna il grafico a barre mensile storico."""
        # Pulisci la figura esistente
        self.monthly_chart_canvas.figure.clear()
        ax = self.monthly_chart_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.monthly_chart_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        df['Mese'] = df['DATA'].dt.to_period('M')
        monthly_summary = df.groupby('Mese')['IMPORTO NETTO'].agg(
            entrate=lambda x: x[x > 0].sum(),
            uscite=lambda x: abs(x[x < 0].sum())
        ).reset_index()

        # Converti il periodo in datetime per formattazione consistente
        monthly_summary['Mese_dt'] = monthly_summary['Mese'].dt.to_timestamp()
        monthly_summary['Mese_label'] = monthly_summary['Mese_dt'].dt.strftime('%b %Y')

        if len(monthly_summary) == 0:
            ax.text(0.5, 0.5, "Nessun dato mensile storico da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.monthly_chart_canvas.draw()
            return

        # Colori moderni
        colors_entrate = '#27AE60'
        colors_uscite = '#E74C3C'
        
        bar_width = 0.35
        index = np.arange(len(monthly_summary['Mese_label']))

        # Barre con effetti ombra
        bars1 = ax.bar(index - bar_width/2, monthly_summary['entrate'], bar_width, 
                      label='Entrate', color=colors_entrate, alpha=0.9,
                      edgecolor='white', linewidth=1)
        bars2 = ax.bar(index + bar_width/2, monthly_summary['uscite'], bar_width, 
                      label='Uscite', color=colors_uscite, alpha=0.9,
                      edgecolor='white', linewidth=1)

        # Aggiungi valori sopra le barre
        for bar, value in zip(bars1, monthly_summary['entrate']):
            height = bar.get_height()
            ax.annotate(f'€{value:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=8, fontweight='bold', color='#333333')
        
        for bar, value in zip(bars2, monthly_summary['uscite']):
            height = bar.get_height()
            ax.annotate(f'€{value:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=8, fontweight='bold', color='#333333')

        # Styling moderno
        ax.set_ylabel('IMPORTO NETTO (€)', fontsize=10, color='#34495E', fontweight='bold')
        ax.set_xlabel('Mese', fontsize=10, color='#34495E', fontweight='bold')
        
        ax.set_xticks(index)
        ax.set_xticklabels(monthly_summary['Mese_label'], rotation=45, ha="right", 
                          fontsize=9, color='#2C3E50')
        
        # Legenda compatta
        legend = ax.legend(loc='upper left', 
                          frameon=True, fancybox=True, shadow=True, 
                          fontsize=8, borderpad=0.1, handlelength=0.8)
        legend.get_frame().set_facecolor('#F8F9FA')
        legend.get_frame().set_edgecolor('#BDC3C7')
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
        
        self.monthly_chart_canvas.figure.tight_layout(pad=1.5)
        self.monthly_chart_canvas.draw()

    def _update_cumulative_profit_chart(self, df):
        """Aggiorna il grafico a linee del profitto cumulativo storico."""
        # Pulisci la figura esistente
        self.cumulative_profit_canvas.figure.clear()
        ax = self.cumulative_profit_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.cumulative_profit_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        if len(df) == 0:
            ax.text(0.5, 0.5, "Nessun dato storico da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.cumulative_profit_canvas.draw()
            return

        df_sorted = df.sort_values('DATA')
        df_sorted['profitto_cumulativo'] = df_sorted['IMPORTO NETTO'].cumsum()

        # Linea principale
        line = ax.plot(df_sorted['DATA'], df_sorted['profitto_cumulativo'], 
                      linewidth=2.5, color='#3498DB', alpha=0.9, 
                      marker='o', markersize=4, markerfacecolor='#2980B9',
                      markeredgecolor='white', markeredgewidth=1,
                      label='Profitto Cumulativo Storico')
        
        # Aggiungi valori sui punti ogni 5 punti per evitare sovrapposizioni
        step = max(1, len(df_sorted) // 10)  # Mostra circa 10 valori
        for i in range(0, len(df_sorted), step):
            value = df_sorted['profitto_cumulativo'].iloc[i]
            date = df_sorted['DATA'].iloc[i]
            ax.annotate(f'€{value:,.0f}',
                       xy=(date, value),
                       xytext=(0, 8),  # 8 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=7, fontweight='bold', color='#333333',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
        
        # Area sotto la curva
        final_value = df_sorted['profitto_cumulativo'].iloc[-1]
        area_color = '#27AE60' if final_value >= 0 else '#E74C3C'
        ax.fill_between(df_sorted['DATA'], df_sorted['profitto_cumulativo'], 0, 
                       alpha=0.2, color=area_color)
        
        # Linea dello zero
        ax.axhline(y=0, color='#95A5A6', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # Styling moderno
        ax.set_ylabel('Profitto (€)', fontsize=10, color='#34495E', fontweight='bold')
        ax.set_xlabel('Data', fontsize=10, color='#34495E', fontweight='bold')
        
        # Griglia elegante
        ax.grid(True, linestyle='--', alpha=0.3, color='#BDC3C7')
        ax.set_axisbelow(True)
        
        # Rimuovi bordi superiore e destro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Formattazione date
        total_days = (df_sorted['DATA'].max() - df_sorted['DATA'].min()).days
        
        if total_days <= 31:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        elif total_days <= 90:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        else:
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", color='#2C3E50')
        
        # Formattazione asse Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.tick_params(colors='#2C3E50', which='both')
        
        self.cumulative_profit_canvas.figure.tight_layout(pad=1.5)
        self.cumulative_profit_canvas.draw()

    def _update_daily_performance_chart(self):
        """Aggiorna il grafico delle performance giornaliere."""
        # Pulisci la figura esistente
        self.daily_performance_canvas.figure.clear()
        ax = self.daily_performance_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.daily_performance_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        try:
            # Carica tutti i dati storici dal database
            historical_data = self.db_manager.load_all_transactions()
            
            if not historical_data:
                ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
            
            # Applica parsing robusto delle date usando la utility function
            df['DATA'] = df['DATA'].apply(parse_date_robust)
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            if len(df) == 0:
                ax.text(0.5, 0.5, "Nessun dato valido da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # Aggiungi il giorno della settimana (0=Lunedì, 6=Domenica)
            df['DayOfWeek'] = df['DATA'].dt.dayofweek
            df['DayName'] = df['DATA'].dt.day_name()

            # CALCOLO CORRETTO della media uscite giornaliera
            # Considera solo i giorni che hanno effettivamente uscite, non tutti i giorni del periodo
            uscite_df = df[df['IMPORTO NETTO'] < 0].copy()
            if len(uscite_df) > 0:
                # Raggruppa per data e somma le uscite giornaliere
                uscite_per_giorno = uscite_df.groupby(uscite_df['DATA'].dt.date)['IMPORTO NETTO'].sum().abs()
                media_uscite_giornaliera = uscite_per_giorno.mean()
            else:
                media_uscite_giornaliera = 0

            # Filtra solo le entrate (importi positivi) 
            entrate_df = df[df['IMPORTO NETTO'] > 0].copy()

            if len(entrate_df) == 0:
                ax.text(0.5, 0.5, "Nessuna entrata da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # ANALISI PERFORMANCE PER GIORNO DELLA SETTIMANA (METODOLOGIA CORRETTA)
            # 1. Raggruppa le entrate per giorno specifico e giorno della settimana
            entrate_per_giorno = entrate_df.groupby([entrate_df['DATA'].dt.date, 'DayOfWeek'])['IMPORTO NETTO'].sum().reset_index()
            
            # 2. Calcola la media delle entrate per ogni giorno della settimana
            # Questo ci dice quanto si guadagna in media ogni lunedì, martedì, ecc.
            performance_settimanale = entrate_per_giorno.groupby('DayOfWeek')['IMPORTO NETTO'].mean().reset_index()
            
            # 3. Mappa i numeri dei giorni ai nomi in italiano
            giorni_map = {
                0: 'Lunedì', 
                1: 'Martedì', 
                2: 'Mercoledì', 
                3: 'Giovedì', 
                4: 'Venerdì', 
                5: 'Sabato', 
                6: 'Domenica'
            }
            performance_settimanale['DayName'] = performance_settimanale['DayOfWeek'].map(giorni_map)
            
            # 4. Ordina per giorno della settimana (Lunedì = 0, Domenica = 6)
            performance_settimanale = performance_settimanale.sort_values('DayOfWeek')
            
            if len(performance_settimanale) == 0:
                ax.text(0.5, 0.5, "Nessun dato per l'analisi settimanale", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # Crea il grafico a barre per giorni della settimana
            bars = ax.bar(performance_settimanale['DayName'], performance_settimanale['IMPORTO NETTO'], 
                         color='#27AE60', alpha=0.8, edgecolor='white', linewidth=2)

            # Aggiungi valori sopra le barre
            for bar, value in zip(bars, performance_settimanale['IMPORTO NETTO']):
                height = bar.get_height()
                ax.annotate(f'€{value:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=10, fontweight='bold', color='#333333')

            # Calcola il range appropriato per l'asse Y
            max_entrate = performance_settimanale['IMPORTO NETTO'].max()
            min_entrate = performance_settimanale['IMPORTO NETTO'].min()
            
            # Imposta i limiti dell'asse Y per rendere visibili le barre
            # Usa un range che mostri bene sia le entrate che la linea obiettivo
            y_max = max(max_entrate * 1.15, media_uscite_giornaliera * 1.1) if media_uscite_giornaliera > 0 else max_entrate * 1.2
            y_min = min_entrate * 0.9
            ax.set_ylim(y_min, y_max)
            
            # Aggiungi la linea rossa orizzontale per la media uscite
            if media_uscite_giornaliera > 0:
                ax.axhline(y=media_uscite_giornaliera, color='#E74C3C', linestyle='--', 
                          linewidth=2, alpha=0.8, label=f'Obiettivo Pareggio: €{media_uscite_giornaliera:,.0f}')

            # Styling moderno
            ax.set_ylabel('Media Entrate Giornaliere (€)', fontsize=10, color='#34495E', fontweight='bold')
            ax.set_xlabel('Giorno della Settimana', fontsize=10, color='#34495E', fontweight='bold')

            # Formattazione assi
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
            ax.tick_params(colors='#2C3E50', which='both')
            
            # Ruota le etichette dell'asse X
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", color='#2C3E50', fontsize=9)

            # Griglia elegante
            ax.grid(axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
            ax.set_axisbelow(True)

            # Rimuovi bordi superiore e destro
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#BDC3C7')
            ax.spines['bottom'].set_color('#BDC3C7')

            # Legenda per la linea obiettivo
            if media_uscite_giornaliera > 0:
                legend = ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                                 fontsize=8, borderpad=0.1, handlelength=0.8)
                legend.get_frame().set_facecolor('#F8F9FA')
                legend.get_frame().set_edgecolor('#BDC3C7')
                legend.get_frame().set_alpha(0.9)

            self.daily_performance_canvas.figure.tight_layout(pad=1.5)
            self.daily_performance_canvas.draw()

        except Exception as e:
            print(f"Errore nell'aggiornamento del grafico performance giornaliera: {e}")
            ax.text(0.5, 0.5, "Errore nel caricamento dati", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#E74C3C', weight='bold')
            style_empty_chart(ax)
            self.daily_performance_canvas.draw()

    def _update_average_performance_chart(self):
        """Aggiorna il grafico delle performance medie cumulative."""
        # Pulisci la figura esistente
        self.average_performance_canvas.figure.clear()
        ax = self.average_performance_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.average_performance_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        try:
            # Carica tutti i dati storici dal database
            historical_data = self.db_manager.load_all_transactions()
            
            if not historical_data:
                ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.average_performance_canvas.draw()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
            
            # Applica parsing robusto delle date usando la utility function
            df['DATA'] = df['DATA'].apply(parse_date_robust)
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            if len(df) == 0:
                ax.text(0.5, 0.5, "Nessun dato valido da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.average_performance_canvas.draw()
                return

            # Ottieni l'anno più recente dai dati
            latest_year = df['DATA'].max().year
            
            # Filtra i dati per l'anno più recente
            df_year = df[df['DATA'].dt.year == latest_year].copy()
            
            if len(df_year) == 0:
                ax.text(0.5, 0.5, f"Nessun dato per l'anno {latest_year}", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                style_empty_chart(ax)
                self.average_performance_canvas.draw()
                return

            # Aggiungi colonna mese-anno
            df_year['Mese'] = df_year['DATA'].dt.to_period('M')
            
            # Raggruppa per mese e calcola entrate, uscite e profitti mensili
            monthly_summary = df_year.groupby('Mese')['IMPORTO NETTO'].agg([
                ('entrate_mensili', lambda x: x[x > 0].sum()),
                ('uscite_mensili', lambda x: abs(x[x < 0].sum())),
                ('profitto_mensile', 'sum')
            ]).reset_index()
            
            # Ordina per mese
            monthly_summary = monthly_summary.sort_values('Mese')
            
            # Calcola le medie cumulative
            monthly_summary['media_entrate'] = monthly_summary['entrate_mensili'].expanding().mean()
            monthly_summary['media_uscite'] = monthly_summary['uscite_mensili'].expanding().mean()
            monthly_summary['media_profitti'] = monthly_summary['profitto_mensile'].expanding().mean()
            
            # Converti i mesi in etichette leggibili
            monthly_summary['Mese_label'] = monthly_summary['Mese'].dt.strftime('%b')
            
            # Colori coordinati con i box delle metriche
            color_entrate = '#27AE60'  # Verde (uguale al box TOTALE ENTRATE)
            color_uscite = '#C0392B'   # Rosso (uguale al box TOTALE USCITE) 
            color_profitti = '#2980B9' # Blu (uguale al box PROFITTO)
            
            # Crea le linee del grafico
            x_pos = range(len(monthly_summary))
            
            line1 = ax.plot(x_pos, monthly_summary['media_entrate'], 
                           linewidth=2.5, color=color_entrate, alpha=0.9,
                           marker='o', markersize=5, markerfacecolor=color_entrate,
                           markeredgecolor='white', markeredgewidth=1,
                           label='Media Entrate')
            
            line2 = ax.plot(x_pos, monthly_summary['media_uscite'], 
                           linewidth=2.5, color=color_uscite, alpha=0.9,
                           marker='s', markersize=5, markerfacecolor=color_uscite,
                           markeredgecolor='white', markeredgewidth=1,
                           label='Media Uscite')
            
            line3 = ax.plot(x_pos, monthly_summary['media_profitti'], 
                           linewidth=2.5, color=color_profitti, alpha=0.9,
                           marker='^', markersize=5, markerfacecolor=color_profitti,
                           markeredgecolor='white', markeredgewidth=1,
                           label='Media Profitti')
            
            # Aggiungi valori sui punti dell'ultima linea (ogni 2 punti per leggibilità)
            step = max(1, len(x_pos) // 6)  # Mostra circa 6 valori
            for i in range(0, len(x_pos), step):
                # Valori per Media Entrate
                ax.annotate(f'€{monthly_summary["media_entrate"].iloc[i]:,.0f}',
                           xy=(x_pos[i], monthly_summary['media_entrate'].iloc[i]),
                           xytext=(0, 8),  # 8 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=6, fontweight='bold', color=color_entrate)
                
                # Valori per Media Uscite
                ax.annotate(f'€{monthly_summary["media_uscite"].iloc[i]:,.0f}',
                           xy=(x_pos[i], monthly_summary['media_uscite'].iloc[i]),
                           xytext=(0, -12),  # Offset negativo per posizionare sotto
                           textcoords="offset points",
                           ha='center', va='top',
                           fontsize=6, fontweight='bold', color=color_uscite)
                
                # Valori per Media Profitti (solo se valore significativo)
                if abs(monthly_summary['media_profitti'].iloc[i]) > 50:
                    ax.annotate(f'€{monthly_summary["media_profitti"].iloc[i]:,.0f}',
                               xy=(x_pos[i], monthly_summary['media_profitti'].iloc[i]),
                               xytext=(10, 0),  # Offset orizzontale
                               textcoords="offset points",
                               ha='left', va='center',
                               fontsize=6, fontweight='bold', color=color_profitti)
            
            # Linea dello zero per riferimento
            ax.axhline(y=0, color='#95A5A6', linestyle='--', linewidth=1, alpha=0.5)
            
            # Styling moderno
            ax.set_ylabel('IMPORTO NETTO Medio (€)', fontsize=10, color='#34495E', fontweight='bold')
            ax.set_xlabel('Mese', fontsize=10, color='#34495E', fontweight='bold')
            
            # Imposta le etichette dell'asse X
            ax.set_xticks(x_pos)
            ax.set_xticklabels(monthly_summary['Mese_label'], 
                              color='#2C3E50', fontsize=9)
            
            # Legenda compatta
            legend = ax.legend(loc='upper left', 
                              frameon=True, fancybox=True, shadow=True, 
                              fontsize=8, borderpad=0.3, handlelength=1.0,
                              ncol=1)
            legend.get_frame().set_facecolor('#F8F9FA')
            legend.get_frame().set_edgecolor('#BDC3C7')
            legend.get_frame().set_alpha(0.9)
            
            # Griglia elegante
            ax.grid(True, linestyle='--', alpha=0.3, color='#BDC3C7')
            ax.set_axisbelow(True)
            
            # Rimuovi bordi superiore e destro
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#BDC3C7')
            ax.spines['bottom'].set_color('#BDC3C7')
            
            # Formattazione asse Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
            ax.tick_params(colors='#2C3E50', which='both')
            
            self.average_performance_canvas.figure.tight_layout(pad=1.5)
            self.average_performance_canvas.draw()

        except Exception as e:
            print(f"Errore nell'aggiornamento del grafico performance medie: {e}")
            ax.text(0.5, 0.5, "Errore nel caricamento dati", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#E74C3C', weight='bold')
            style_empty_chart(ax)
            self.average_performance_canvas.draw()

    def _show_error_in_charts(self, error_message):
        """Mostra un messaggio di errore in tutti i grafici."""
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas, 
                      self.daily_performance_canvas, self.average_performance_canvas,
                      self.top_suppliers_canvas, self.supplier_frequency_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, error_message, 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#E74C3C', weight='bold')
            style_empty_chart(ax)
            canvas.draw()

    def _update_supplier_charts(self, df):
        """Aggiorna i grafici di analisi per fornitore."""
        # Filtra solo le spese (importi negativi) con fornitori
        expenses_df = df[(df['IMPORTO NETTO'] < 0) & (df['FORNITORE'].notna()) & (df['FORNITORE'] != '')].copy()
        
        if len(expenses_df) == 0:
            # Se non ci sono dati sui fornitori, mostra grafici vuoti
            self._reset_supplier_charts()
            return
        
        # Aggiorna entrambi i grafici
        self._update_top_suppliers_chart(expenses_df)
        self._update_supplier_frequency_chart(expenses_df)

    def _update_top_suppliers_chart(self, expenses_df):
        """Aggiorna il grafico dei top fornitori per spesa totale."""
        # Pulisci la figura esistente
        self.top_suppliers_canvas.figure.clear()
        ax = self.top_suppliers_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.top_suppliers_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        # Calcola la spesa totale per fornitore (valore assoluto)
        supplier_totals = expenses_df.groupby('FORNITORE')['IMPORTO NETTO'].sum().abs().sort_values(ascending=True)
        
        # Prendi i top 10 fornitori
        top_suppliers = supplier_totals.tail(10)
        
        if len(top_suppliers) == 0:
            ax.text(0.5, 0.5, "Nessun dato sui fornitori", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.top_suppliers_canvas.draw()
            return

        # Tronca i nomi dei fornitori se troppo lunghi
        supplier_names = [name[:30] + '...' if len(name) > 30 else name for name in top_suppliers.index]
        
        # Crea il grafico a barre orizzontali
        bars = ax.barh(range(len(top_suppliers)), top_suppliers.values, 
                      color='#E74C3C', alpha=0.8, edgecolor='white', linewidth=1)

        # Aggiungi valori alla fine delle barre
        for i, (bar, value) in enumerate(zip(bars, top_suppliers.values)):
            width = bar.get_width()
            ax.text(width + (max(top_suppliers.values) * 0.01), bar.get_y() + bar.get_height()/2,
                   f'€{value:,.0f}', ha='left', va='center', 
                   fontsize=9, fontweight='bold', color='#333333')

        # Styling moderno
        ax.set_ylabel('Fornitore', fontsize=10, color='#34495E', fontweight='bold')
        ax.set_xlabel('Spesa Totale (€)', fontsize=10, color='#34495E', fontweight='bold')
        
        # Imposta le etichette dell'asse Y
        ax.set_yticks(range(len(top_suppliers)))
        ax.set_yticklabels(supplier_names, fontsize=8, color='#2C3E50')
        
        # Griglia elegante
        ax.grid(axis='x', linestyle='--', alpha=0.3, color='#BDC3C7')
        ax.set_axisbelow(True)
        
        # Rimuovi bordi superiore e destro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Formattazione asse X
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.tick_params(colors='#2C3E50', which='both')
        
        self.top_suppliers_canvas.figure.tight_layout(pad=1.5)
        self.top_suppliers_canvas.draw()

    def _update_supplier_frequency_chart(self, expenses_df):
        """Aggiorna il grafico della frequenza degli ordini per fornitore."""
        # Pulisci la figura esistente
        self.supplier_frequency_canvas.figure.clear()
        ax = self.supplier_frequency_canvas.figure.add_subplot(111)
        
        # Imposta colore di sfondo
        self.supplier_frequency_canvas.figure.patch.set_facecolor('#FAFAFA')
        ax.set_facecolor('#FFFFFF')

        # Conta il numero di transazioni per fornitore
        supplier_frequency = expenses_df['FORNITORE'].value_counts().sort_values(ascending=True)
        
        # Prendi i top 10 fornitori per frequenza
        top_frequency = supplier_frequency.tail(10)
        
        if len(top_frequency) == 0:
            ax.text(0.5, 0.5, "Nessun dato sulla frequenza ordini", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.supplier_frequency_canvas.draw()
            return

        # Tronca i nomi dei fornitori se troppo lunghi
        supplier_names = [name[:30] + '...' if len(name) > 30 else name for name in top_frequency.index]
        
        # Crea il grafico a barre orizzontali
        bars = ax.barh(range(len(top_frequency)), top_frequency.values, 
                      color='#3498DB', alpha=0.8, edgecolor='white', linewidth=1)

        # Aggiungi valori alla fine delle barre
        for i, (bar, value) in enumerate(zip(bars, top_frequency.values)):
            width = bar.get_width()
            ax.text(width + (max(top_frequency.values) * 0.01), bar.get_y() + bar.get_height()/2,
                   f'{value}', ha='left', va='center', 
                   fontsize=9, fontweight='bold', color='#333333')

        # Styling moderno
        ax.set_ylabel('Fornitore', fontsize=10, color='#34495E', fontweight='bold')
        ax.set_xlabel('Numero di Ordini', fontsize=10, color='#34495E', fontweight='bold')
        
        # Imposta le etichette dell'asse Y
        ax.set_yticks(range(len(top_frequency)))
        ax.set_yticklabels(supplier_names, fontsize=8, color='#2C3E50')
        
        # Griglia elegante
        ax.grid(axis='x', linestyle='--', alpha=0.3, color='#BDC3C7')
        ax.set_axisbelow(True)
        
        # Rimuovi bordi superiore e destro
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#BDC3C7')
        ax.spines['bottom'].set_color('#BDC3C7')
        
        # Formattazione asse X
        ax.tick_params(colors='#2C3E50', which='both')
        
        self.supplier_frequency_canvas.figure.tight_layout(pad=1.5)
        self.supplier_frequency_canvas.draw()

    def _reset_supplier_charts(self):
        """Resetta i grafici dei fornitori quando non ci sono dati."""
        for canvas in [self.top_suppliers_canvas, self.supplier_frequency_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato sui fornitori", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            canvas.draw()

    def _reset_view(self):
        """Resetta la vista quando non ci sono dati."""
        # Reset delle metriche utilizzando le utility functions
        update_metric_box_value(self.total_gains_label, "0.00 €")
        update_metric_box_value(self.total_expenses_label, "0.00 €")
        update_metric_box_value(self.profit_label, "0.00 €")
        
        # Reset di tutti i grafici
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas, 
                      self.daily_performance_canvas, self.average_performance_canvas,
                      self.top_suppliers_canvas, self.supplier_frequency_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            style_empty_chart(ax)
            canvas.draw()
