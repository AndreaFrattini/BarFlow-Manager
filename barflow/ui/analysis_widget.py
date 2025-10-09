from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget
from PySide6.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from .historical_analysis_widget import HistoricalAnalysisWidget
from .analysis_utils import (
    create_metric_box, 
    create_chart_canvas, 
    style_empty_chart, 
    prepare_dataframe_for_analysis,
    update_metric_box_value,
    create_info_button
)

class AnalysisWidget(QWidget):
    """Widget per la sezione di analisi dei dati con tab per analisi attuale e storica."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia utente del widget con tab."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

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
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Layout per i box delle metriche
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.total_gains_label = create_metric_box("TOTALE ENTRATE", "0.00 €", "#27AE60")
        self.total_expenses_label = create_metric_box("TOTALE USCITE", "0.00 €", "#C0392B")
        self.profit_label = create_metric_box("PROFITTO", "0.00 €", "#2980B9")
        
        metrics_layout.addWidget(self.total_gains_label)
        metrics_layout.addWidget(self.total_expenses_label)
        metrics_layout.addWidget(self.profit_label)
        
        # Contenitore per i box per limitarne l'altezza
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_layout)
        metrics_container.setFixedHeight(60)

        layout.addWidget(metrics_container)

        # Layout per i grafici
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

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
        
        self.monthly_chart_canvas = create_chart_canvas(figsize=(10, 7))
        
        monthly_container_layout.addLayout(monthly_title_layout)
        monthly_container_layout.addWidget(self.monthly_chart_canvas)
        
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
        
        self.cumulative_profit_canvas = create_chart_canvas(figsize=(10, 7))
        
        performance_container_layout.addLayout(performance_title_layout)
        performance_container_layout.addWidget(self.cumulative_profit_canvas)

        charts_layout.addWidget(monthly_chart_container)
        charts_layout.addWidget(performance_chart_container)

        layout.addLayout(charts_layout)
        
        return widget

    def _on_tab_changed(self, index):
        """Gestisce il cambio di tab per aggiornare dinamicamente i dati storici."""
        # Se viene selezionato il tab "Analisi Storico" (indice 1)
        if index == 1:
            try:
                # Aggiorna i dati storici caricandoli dal database al momento
                self.historical_analysis_widget.update_data()
            except Exception as e:
                print(f"Errore durante il caricamento dei dati storici: {e}")
                import traceback
                traceback.print_exc()
                # Non fare crash dell'app, l'errore è già gestito nel widget storico

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
        layout.setContentsMargins(5, 5, 5, 5)  # Ridotto il padding interno
        layout.setSpacing(3)  # Ridotto lo spazio tra title e value
        layout.setAlignment(Qt.AlignCenter)  # Centra il contenuto verticalmente
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Permette il wrapping del testo se necessario
        title_label.setStyleSheet("""
            color: white; 
            font-size: 10px; 
            font-weight: bold;
            margin: 0px;
            padding: 2px;
        """)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)  # Permette il wrapping del testo se necessario
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
        df = prepare_dataframe_for_analysis(transactions_data)
        
        if df is None:
            self._reset_view()
            return

        try:
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
            self._update_daily_performance_chart(df)
                
        except Exception as e:
            print(f"Errore nell'aggiornamento dei dati: {e}")
            import traceback
            traceback.print_exc()
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
        monthly_summary = df.groupby('Mese')['IMPORTO NETTO'].agg(
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
            style_empty_chart(ax)
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

    def _update_daily_performance_chart(self, df):
        """Aggiorna il grafico delle performance giornaliere basato sui dati attuali."""
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
            style_empty_chart(ax)
            self.cumulative_profit_canvas.draw()
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
                   fontsize=14, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.cumulative_profit_canvas.draw()
            return

        # ANALISI PERFORMANCE PER GIORNO DELLA SETTIMANA
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
                   fontsize=14, color='#666666', weight='bold')
            style_empty_chart(ax)
            self.cumulative_profit_canvas.draw()
            return

        # Crea il grafico a barre per giorni della settimana
        bars = ax.bar(performance_settimanale['DayName'], performance_settimanale['IMPORTO NETTO'], 
                     color='#27AE60', alpha=0.8, edgecolor='white', linewidth=2)

        # Aggiungi valori sopra le barre
        for bar, value in zip(bars, performance_settimanale['IMPORTO NETTO']):
            height = bar.get_height()
            ax.annotate(f'€{value:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 5),  # 5 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=10, fontweight='bold', color='#333333')

        # Calcola il range appropriato per l'asse Y
        max_entrate = performance_settimanale['IMPORTO NETTO'].max()
        min_entrate = performance_settimanale['IMPORTO NETTO'].min()
        
        # Imposta i limiti dell'asse Y per rendere visibili le barre
        # Usa un range che mostri bene sia le entrate che la linea obiettivo
        y_max = max(max_entrate * 1.15, media_uscite_giornaliera * 1.1) if media_uscite_giornaliera > 0 else max_entrate * 1.2
        y_min = min(0, min_entrate * 0.9)  # Inizia da 0 o poco sotto il minimo
        ax.set_ylim(y_min, y_max)
        
        # Aggiungi la linea rossa orizzontale per la media uscite (obiettivo di pareggio)
        if media_uscite_giornaliera > 0:
            ax.axhline(y=media_uscite_giornaliera, color='#E74C3C', linestyle='--', 
                      linewidth=2, alpha=0.8, label=f'Obiettivo Pareggio: €{media_uscite_giornaliera:,.0f}')

        # Styling moderno
        ax.set_ylabel('Media Entrate Giornaliere (€)', fontsize=12, color='#34495E', fontweight='bold')
        ax.set_xlabel('Giorno della Settimana', fontsize=12, color='#34495E', fontweight='bold')

        # Formattazione assi
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.tick_params(colors='#2C3E50', which='both')
        
        # Ruota le etichette dell'asse X per una migliore leggibilità
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", color='#2C3E50', fontsize=11)

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

        # Aumenta il margine inferiore per le etichette inclinate
        self.cumulative_profit_canvas.figure.subplots_adjust(bottom=0.15)
        self.cumulative_profit_canvas.figure.tight_layout(pad=2.0)
        self.cumulative_profit_canvas.draw()

    def _reset_view(self):
        """Resetta la vista quando non ci sono dati."""
        # Reset delle metriche utilizzando le utility functions
        update_metric_box_value(self.total_gains_label, "0.00 €")
        update_metric_box_value(self.total_expenses_label, "0.00 €")
        update_metric_box_value(self.profit_label, "0.00 €")
        
        # Reset dei grafici con stile moderno
        for canvas in [self.monthly_chart_canvas, self.cumulative_profit_canvas]:
            canvas.figure.clear()
            canvas.figure.patch.set_facecolor('#FAFAFA')
            ax = canvas.figure.add_subplot(111)
            ax.set_facecolor('#FFFFFF')
            ax.text(0.5, 0.5, "Nessun dato da visualizzare", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='#666666', weight='bold')
            style_empty_chart(ax)
            canvas.draw()
