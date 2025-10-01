"""
Widget Dashboard per la visualizzazione delle metriche principali
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QFrame, QGridLayout, QScrollArea, QPushButton,
                              QComboBox, QDateEdit, QSplitter)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QPalette
from PySide6.QtWebEngineWidgets import QWebEngineView
import json


class MetricCard(QFrame):
    """Widget per visualizzare una singola metrica"""
    
    def __init__(self, title, value, subtitle="", color="#3498DB"):
        super().__init__()
        self.init_ui(title, value, subtitle, color)
    
    def init_ui(self, title, value, subtitle, color):
        """Inizializza l'interfaccia della card"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Titolo
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7F8C8D; font-size: 12px; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Valore principale
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #2C3E50; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
        # Sottotitolo (opzionale)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #95A5A6; font-size: 10px;")
            layout.addWidget(subtitle_label)
        
        layout.addStretch()
    
    def update_value(self, value):
        """Aggiorna il valore della metrica"""
        self.value_label.setText(value)


class DashboardWidget(QWidget):
    """Widget principale della dashboard"""
    
    def __init__(self, db_manager, report_generator):
        super().__init__()
        self.db_manager = db_manager
        self.report_generator = report_generator
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header con controlli periodo
        self.create_period_controls(layout)
        
        # Cards delle metriche principali
        self.create_metrics_cards(layout)
        
        # Splitter per grafici
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)
        
        # Grafici
        self.create_charts_section(splitter)
        
        # Pannello laterale con informazioni aggiuntive
        self.create_info_panel(splitter)
        
        # Imposta proporzioni splitter
        splitter.setSizes([800, 400])
    
    def create_period_controls(self, parent_layout):
        """Crea i controlli per la selezione del periodo"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(60)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Etichetta periodo
        period_label = QLabel("Periodo di analisi:")
        period_label.setStyleSheet("font-weight: 500; color: #2C3E50;")
        header_layout.addWidget(period_label)
        
        # Selezione rapida periodo
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Ultimo mese chiuso",
            "Ultimi 3 mesi",
            "Ultimi 6 mesi",
            "Anno corrente",
            "Personalizzato"
        ])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        header_layout.addWidget(self.period_combo)
        
        header_layout.addSpacing(20)
        
        # Date personalizzate
        header_layout.addWidget(QLabel("Da:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.dateChanged.connect(self.on_custom_date_changed)
        header_layout.addWidget(self.start_date)
        
        header_layout.addWidget(QLabel("A:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.on_custom_date_changed)
        header_layout.addWidget(self.end_date)
        
        header_layout.addSpacing(20)
        
        # Pulsante aggiorna
        refresh_btn = QPushButton("🔄 Aggiorna")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        header_layout.addWidget(refresh_btn)
        
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
    
    def create_metrics_cards(self, parent_layout):
        """Crea le cards delle metriche principali"""
        metrics_frame = QFrame()
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(15)
        
        # Crea le cards delle metriche
        self.income_card = MetricCard("Entrate Totali", "€0.00", "Ricavi del periodo", "#27AE60")
        self.expenses_card = MetricCard("Spese Totali", "€0.00", "Costi del periodo", "#E74C3C")
        self.cogs_card = MetricCard("COGS", "€0.00", "Costi diretti", "#F39C12")
        self.gross_profit_card = MetricCard("Profitto Lordo", "€0.00", "Entrate - COGS", "#8E44AD")
        self.net_profit_card = MetricCard("Profitto Netto", "€0.00", "Entrate - Tutte le spese", "#2C3E50")
        self.transactions_card = MetricCard("Transazioni", "0", "Numero operazioni", "#16A085")
        
        # Aggiungi cards al layout
        metrics_layout.addWidget(self.income_card, 0, 0)
        metrics_layout.addWidget(self.expenses_card, 0, 1)
        metrics_layout.addWidget(self.cogs_card, 0, 2)
        metrics_layout.addWidget(self.gross_profit_card, 1, 0)
        metrics_layout.addWidget(self.net_profit_card, 1, 1)
        metrics_layout.addWidget(self.transactions_card, 1, 2)
        
        parent_layout.addWidget(metrics_frame)
    
    def create_charts_section(self, parent_splitter):
        """Crea la sezione dei grafici"""
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(15)
        
        # Frame per i grafici
        charts_frame = QFrame()
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        
        charts_frame_layout = QVBoxLayout(charts_frame)
        charts_frame_layout.setContentsMargins(15, 15, 15, 15)
        
        # Titolo sezione grafici
        charts_title = QLabel("Analisi Grafiche")
        charts_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        charts_frame_layout.addWidget(charts_title)
        
        # WebView per i grafici Plotly
        self.charts_webview = QWebEngineView()
        self.charts_webview.setMinimumHeight(400)
        charts_frame_layout.addWidget(self.charts_webview)
        
        charts_layout.addWidget(charts_frame)
        parent_splitter.addWidget(charts_widget)
    
    def create_info_panel(self, parent_splitter):
        """Crea il pannello informazioni laterale"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(15)
        
        # Riepilogo per categoria
        self.create_category_summary(info_layout)
        
        # Indicatori performance
        self.create_performance_indicators(info_layout)
        
        # Trend recenti
        self.create_recent_trends(info_layout)
        
        info_layout.addStretch()
        
        parent_splitter.addWidget(info_widget)
    
    def create_category_summary(self, parent_layout):
        """Crea il riepilogo per categoria"""
        category_frame = QFrame()
        category_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        category_layout = QVBoxLayout(category_frame)
        
        # Titolo
        title = QLabel("Spese per Categoria")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        category_layout.addWidget(title)
        
        # Scroll area per le categorie
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet("border: none;")
        
        self.category_content = QWidget()
        self.category_content_layout = QVBoxLayout(self.category_content)
        scroll.setWidget(self.category_content)
        
        category_layout.addWidget(scroll)
        parent_layout.addWidget(category_frame)
    
    def create_performance_indicators(self, parent_layout):
        """Crea gli indicatori di performance"""
        perf_frame = QFrame()
        perf_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        perf_layout = QVBoxLayout(perf_frame)
        
        # Titolo
        title = QLabel("Indicatori Performance")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        perf_layout.addWidget(title)
        
        # Margine lordo
        self.gross_margin_label = QLabel("Margine Lordo: --")
        self.gross_margin_label.setStyleSheet("color: #34495E; font-size: 14px; margin: 5px 0;")
        perf_layout.addWidget(self.gross_margin_label)
        
        # Margine netto
        self.net_margin_label = QLabel("Margine Netto: --")
        self.net_margin_label.setStyleSheet("color: #34495E; font-size: 14px; margin: 5px 0;")
        perf_layout.addWidget(self.net_margin_label)
        
        # Media transazione
        self.avg_transaction_label = QLabel("Media Transazione: --")
        self.avg_transaction_label.setStyleSheet("color: #34495E; font-size: 14px; margin: 5px 0;")
        perf_layout.addWidget(self.avg_transaction_label)
        
        parent_layout.addWidget(perf_frame)
    
    def create_recent_trends(self, parent_layout):
        """Crea la sezione trend recenti"""
        trends_frame = QFrame()
        trends_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        trends_layout = QVBoxLayout(trends_frame)
        
        # Titolo
        title = QLabel("Trend Recenti")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        trends_layout.addWidget(title)
        
        # Indicatori trend
        self.trend_direction_label = QLabel("Direzione: --")
        self.trend_direction_label.setStyleSheet("color: #34495E; font-size: 14px; margin: 5px 0;")
        trends_layout.addWidget(self.trend_direction_label)
        
        self.best_day_label = QLabel("Giorno migliore: --")
        self.best_day_label.setStyleSheet("color: #27AE60; font-size: 12px; margin: 5px 0;")
        trends_layout.addWidget(self.best_day_label)
        
        self.worst_day_label = QLabel("Giorno peggiore: --")
        self.worst_day_label.setStyleSheet("color: #E74C3C; font-size: 12px; margin: 5px 0;")
        trends_layout.addWidget(self.worst_day_label)
        
        parent_layout.addWidget(trends_frame)
    
    def on_period_changed(self, period_text):
        """Gestisce il cambio di periodo"""
        if period_text == "Personalizzato":
            return
        
        current_date = QDate.currentDate()
        
        if period_text == "Ultimo mese chiuso":
            start_date = current_date.addMonths(-1)
            start_date = QDate(start_date.year(), start_date.month(), 1)
            end_date = current_date.addDays(-current_date.day())
        elif period_text == "Ultimi 3 mesi":
            start_date = current_date.addMonths(-3)
            end_date = current_date
        elif period_text == "Ultimi 6 mesi":
            start_date = current_date.addMonths(-6)
            end_date = current_date
        elif period_text == "Anno corrente":
            start_date = QDate(current_date.year(), 1, 1)
            end_date = current_date
        else:
            return
        
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        
        # Auto-refresh se non è personalizzato
        QTimer.singleShot(100, self.refresh_data)
    
    def on_custom_date_changed(self):
        """Gestisce il cambio di date personalizzate"""
        self.period_combo.setCurrentText("Personalizzato")
    
    def refresh_data(self):
        """Aggiorna tutti i dati della dashboard"""
        try:
            # Ottieni il periodo selezionato
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # Genera i dati del dashboard
            dashboard_data = self.report_generator.generate_dashboard_data(start_date, end_date)
            
            # Aggiorna le metriche
            self.update_metrics(dashboard_data['financial_summary'])
            
            # Aggiorna le categorie
            self.update_category_summary(dashboard_data['category_analysis'])
            
            # Aggiorna indicatori performance
            self.update_performance_indicators(dashboard_data['financial_summary'], dashboard_data['transaction_count'])
            
            # Aggiorna trend
            self.update_trends(dashboard_data['time_trend'])
            
            # Aggiorna grafici
            self.update_charts(dashboard_data['charts'])
            
        except Exception as e:
            print(f"Errore nell'aggiornamento dashboard: {e}")
    
    def update_metrics(self, financial_summary):
        """Aggiorna le cards delle metriche"""
        self.income_card.update_value(f"€{financial_summary['total_income']:,.2f}")
        self.expenses_card.update_value(f"€{financial_summary['total_expenses']:,.2f}")
        self.cogs_card.update_value(f"€{financial_summary['total_cogs']:,.2f}")
        self.gross_profit_card.update_value(f"€{financial_summary['gross_profit']:,.2f}")
        self.net_profit_card.update_value(f"€{financial_summary['net_profit']:,.2f}")
    
    def update_category_summary(self, category_analysis):
        """Aggiorna il riepilogo per categoria"""
        # Pulisci il contenuto esistente
        for i in reversed(range(self.category_content_layout.count())):
            self.category_content_layout.itemAt(i).widget().setParent(None)
        
        # Aggiungi le categorie
        for category in category_analysis['categories']:
            if category['expenses'] > 0:
                cat_widget = QWidget()
                cat_layout = QHBoxLayout(cat_widget)
                cat_layout.setContentsMargins(0, 2, 0, 2)
                
                name_label = QLabel(category['name'])
                name_label.setStyleSheet("font-weight: 500;")
                cat_layout.addWidget(name_label)
                
                cat_layout.addStretch()
                
                amount_label = QLabel(f"€{category['expenses']:,.2f}")
                amount_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
                cat_layout.addWidget(amount_label)
                
                perc_label = QLabel(f"({category['expense_percentage']:.1f}%)")
                perc_label.setStyleSheet("color: #95A5A6; font-size: 11px;")
                cat_layout.addWidget(perc_label)
                
                self.category_content_layout.addWidget(cat_widget)
        
        self.category_content_layout.addStretch()
    
    def update_performance_indicators(self, financial_summary, transaction_count):
        """Aggiorna gli indicatori di performance"""
        # Calcola margini
        total_income = financial_summary['total_income']
        
        if total_income > 0:
            gross_margin = (financial_summary['gross_profit'] / total_income) * 100
            net_margin = (financial_summary['net_profit'] / total_income) * 100
            
            self.gross_margin_label.setText(f"Margine Lordo: {gross_margin:.1f}%")
            self.net_margin_label.setText(f"Margine Netto: {net_margin:.1f}%")
        else:
            self.gross_margin_label.setText("Margine Lordo: --")
            self.net_margin_label.setText("Margine Netto: --")
        
        # Media transazione
        if transaction_count > 0:
            avg_transaction = total_income / transaction_count
            self.avg_transaction_label.setText(f"Media Transazione: €{avg_transaction:.2f}")
            self.transactions_card.update_value(str(transaction_count))
        else:
            self.avg_transaction_label.setText("Media Transazione: --")
            self.transactions_card.update_value("0")
    
    def update_trends(self, time_trend):
        """Aggiorna i trend recenti"""
        trend_analysis = time_trend.get('trend_analysis', {})
        
        direction = trend_analysis.get('trend_direction', 'stabile')
        self.trend_direction_label.setText(f"Direzione: {direction.title()}")
        
        # Colore basato sulla direzione
        if direction == 'crescente':
            color = "#27AE60"
        elif direction == 'decrescente':
            color = "#E74C3C"
        else:
            color = "#34495E"
        
        self.trend_direction_label.setStyleSheet(f"color: {color}; font-size: 14px; margin: 5px 0; font-weight: bold;")
        
        # Migliore e peggiore giorno
        best_day = trend_analysis.get('best_day')
        worst_day = trend_analysis.get('worst_day')
        
        if best_day:
            self.best_day_label.setText(f"Giorno migliore: {best_day['date']} (€{best_day['net_amount']:,.2f})")
        else:
            self.best_day_label.setText("Giorno migliore: --")
        
        if worst_day:
            self.worst_day_label.setText(f"Giorno peggiore: {worst_day['date']} (€{worst_day['net_amount']:,.2f})")
        else:
            self.worst_day_label.setText("Giorno peggiore: --")
    
    def update_charts(self, charts):
        """Aggiorna i grafici"""
        if not charts:
            self.charts_webview.setHtml("<html><body><h3>Nessun dato per i grafici</h3></body></html>")
            return
        
        # Combina tutti i grafici in una singola pagina HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { margin: 10px; font-family: Arial, sans-serif; }
                .chart-container { margin-bottom: 30px; }
                .chart-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2C3E50; }
            </style>
        </head>
        <body>
        """
        
        # Aggiungi ogni grafico
        chart_titles = {
            'financial_summary': 'Riepilogo Finanziario',
            'income_pie': 'Distribuzione Entrate',
            'expense_pie': 'Distribuzione Spese',
            'trend_line': 'Trend Temporale'
        }
        
        for chart_key, chart_html in charts.items():
            if chart_html:
                title = chart_titles.get(chart_key, chart_key.replace('_', ' ').title())
                html_content += f"""
                <div class="chart-container">
                    <div class="chart-title">{title}</div>
                    {chart_html}
                </div>
                """
        
        html_content += "</body></html>"
        
        self.charts_webview.setHtml(html_content)