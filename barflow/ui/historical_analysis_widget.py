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
        
        self.total_gains_label = self._create_metric_box("TOTALE ENTRATE", "0.00 €", "#27AE60")
        self.total_expenses_label = self._create_metric_box("TOTALE USCITE", "0.00 €", "#C0392B")
        self.profit_label = self._create_metric_box("PROFITTO", "0.00 €", "#2980B9")
        
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
        
        main_layout.addWidget(self.tab_widget)
        
        # Non caricare automaticamente i dati - verranno caricati solo quando necessario

    def _setup_historical_tab(self):
        """Configura la tab 'Entrate vs Uscite'."""
        layout = QHBoxLayout(self.historical_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Grafico Entrate vs Uscite Mensili
        self.monthly_chart_canvas = self._create_chart_canvas()
        layout.addWidget(self.monthly_chart_canvas)

        # Grafico Performance Media Giornaliera
        self.daily_performance_canvas = self._create_chart_canvas()
        layout.addWidget(self.daily_performance_canvas)

    def _setup_performance_tab(self):
        """Configura la tab 'Andamento Temporale'."""
        layout = QVBoxLayout(self.performance_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Grafico Andamento Profitto Cumulativo (in alto)
        self.cumulative_profit_canvas = self._create_chart_canvas()
        layout.addWidget(self.cumulative_profit_canvas)

        # Grafico Performance Medie (in basso)
        self.average_performance_canvas = self._create_chart_canvas()
        layout.addWidget(self.average_performance_canvas)

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
        layout.setContentsMargins(5, 5, 5, 5)  # Ridotto da 20 a 15
        layout.setSpacing(3)  # Ridotto da 10 a 8
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            color: white; 
            font-size: 10px;
            font-weight: bold;
            margin: 0px;
            padding: 2px;
        """)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("""
            color: white; 
            font-size: 12px;
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
        
        fig, ax = plt.subplots(figsize=(8, 3))
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
            df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            # Calcola le metriche
            total_gains = df[df['IMPORTO NETTO'] > 0]['IMPORTO NETTO'].sum()
            total_expenses = abs(df[df['IMPORTO NETTO'] < 0]['IMPORTO NETTO'].sum())
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

            # Aggiorna i grafici
            self._update_monthly_chart(df)
            self._update_cumulative_profit_chart(df)
            self._update_daily_performance_chart()
            self._update_average_performance_chart()
                
        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati storici: {e}")
            self._reset_view()

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
            self._style_empty_chart(ax)
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
        ax.set_title('Entrate vs Uscite Mensili', fontsize=14, fontweight='bold', 
                    color='#2C3E50', pad=15)
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
            self._style_empty_chart(ax)
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
        ax.set_title('Andamento Profitto Cumulativo', fontsize=14, fontweight='bold', 
                    color='#2C3E50', pad=15)
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
                self._style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
            df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            if len(df) == 0:
                ax.text(0.5, 0.5, "Nessun dato valido da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                self._style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # Aggiungi il giorno della settimana (0=Lunedì, 6=Domenica)
            df['DayOfWeek'] = df['DATA'].dt.dayofweek
            df['DayName'] = df['DATA'].dt.day_name()

            # Calcola la media delle uscite totali per la linea di riferimento
            # Considera solo le uscite e calcola la media giornaliera su tutti i giorni con dati
            uscite_totali = df[df['IMPORTO NETTO'] < 0]['IMPORTO NETTO'].abs().sum()
            giorni_unici = len(df['DATA'].dt.date.unique())
            media_uscite_giornaliera = uscite_totali / giorni_unici if giorni_unici > 0 else 0

            # Filtra solo le entrate (importi positivi) 
            entrate_df = df[df['IMPORTO NETTO'] > 0].copy()

            if len(entrate_df) == 0:
                ax.text(0.5, 0.5, "Nessuna entrata da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                self._style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # CALCOLO CORRETTO: Somma le entrate per ogni giorno specifico, poi calcola la media per giorno della settimana
            # 1. Raggruppa per DATA e DayOfWeek e somma le entrate giornaliere
            entrate_per_giorno = entrate_df.groupby(['DATA', 'DayOfWeek'])['IMPORTO NETTO'].sum().reset_index()
            
            # 2. Escludi lunedì (DayOfWeek = 0) e calcola la media delle entrate giornaliere per giorno della settimana
            entrate_lavorative = entrate_per_giorno[entrate_per_giorno['DayOfWeek'] != 0]
            
            if len(entrate_lavorative) == 0:
                ax.text(0.5, 0.5, "Nessuna entrata nei giorni lavorativi", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                self._style_empty_chart(ax)
                self.daily_performance_canvas.draw()
                return

            # 3. Calcola la media delle entrate giornaliere per ogni giorno della settimana
            giorni_lavorativi = entrate_lavorative.groupby('DayOfWeek')['IMPORTO NETTO'].mean().reset_index()
            
            # Mappa i numeri dei giorni ai nomi completi
            giorni_map = {1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
            giorni_lavorativi['DayName'] = giorni_lavorativi['DayOfWeek'].map(giorni_map)
            
            # Ordina per giorno della settimana
            giorni_lavorativi = giorni_lavorativi.sort_values('DayOfWeek')

            # Crea il grafico a barre (colore verde per coerenza con altri grafici)
            bars = ax.bar(giorni_lavorativi['DayName'], giorni_lavorativi['IMPORTO NETTO'], 
                         color='#27AE60', alpha=0.8, edgecolor='white', linewidth=1)

            # Aggiungi valori sopra le barre
            for bar, value in zip(bars, giorni_lavorativi['IMPORTO NETTO']):
                height = bar.get_height()
                ax.annotate(f'€{value:,.0f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=8, fontweight='bold', color='#333333')

            # Calcola il range appropriato per l'asse Y
            max_entrate = giorni_lavorativi['IMPORTO NETTO'].max()
            min_entrate = giorni_lavorativi['IMPORTO NETTO'].min()
            
            # Imposta i limiti dell'asse Y per rendere visibili le barre
            # Usa un range che mostri bene sia le entrate che la linea obiettivo
            y_max = max(max_entrate * 1.1, media_uscite_giornaliera * 1.1) if media_uscite_giornaliera > 0 else max_entrate * 1.2
            y_min = min_entrate * 0.9
            ax.set_ylim(y_min, y_max)
            
            # Aggiungi la linea rossa orizzontale per la media uscite
            if media_uscite_giornaliera > 0:
                ax.axhline(y=media_uscite_giornaliera, color='#E74C3C', linestyle='-', 
                          linewidth=2, alpha=0.7, label=f'Spesa media giornaliera: €{media_uscite_giornaliera:,.0f}')

            # Styling moderno
            ax.set_title('Performance Media Giornaliera', fontsize=14, fontweight='bold', 
                        color='#2C3E50', pad=15)
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
            self._style_empty_chart(ax)
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
                self._style_empty_chart(ax)
                self.average_performance_canvas.draw()
                return

            df = pd.DataFrame(historical_data)
            df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
            df['DATA'] = pd.to_datetime(df['DATA'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])

            if len(df) == 0:
                ax.text(0.5, 0.5, "Nessun dato valido da visualizzare", 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='#666666', weight='bold')
                self._style_empty_chart(ax)
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
                self._style_empty_chart(ax)
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
            ax.set_title(f'Performance Medie {latest_year}', fontsize=14, fontweight='bold', 
                        color='#2C3E50', pad=15)
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
            self._style_empty_chart(ax)
            self.average_performance_canvas.draw()

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
        
        # Reset di tutti i grafici
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas, 
                      self.daily_performance_canvas, self.average_performance_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12, color='#666666', weight='bold')
            self._style_empty_chart(ax)
            canvas.draw()
