"""
Widget per la generazione e visualizzazione dei report
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QComboBox, QDateEdit, QFrame, QTextEdit, QTabWidget,
                              QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
                              QFormLayout, QProgressBar, QMessageBox, QCheckBox,
                              QSpinBox, QSplitter, QScrollArea)
from PySide6.QtCore import Qt, QDate, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
import subprocess
from datetime import datetime


class ReportGenerationWorker(QThread):
    """Thread per la generazione asincrona dei report"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    report_completed = Signal(str)  # file path
    report_failed = Signal(str)     # error message
    
    def __init__(self, report_generator, start_date, end_date, include_transactions, include_monthly_comparison):
        super().__init__()
        self.report_generator = report_generator
        self.start_date = start_date
        self.end_date = end_date
        self.include_transactions = include_transactions
        self.include_monthly_comparison = include_monthly_comparison
    
    def run(self):
        """Esegue la generazione del report"""
        try:
            self.status_updated.emit("Raccolta dati...")
            self.progress_updated.emit(20)
            
            # Genera il report base
            file_path = self.report_generator.export_to_excel(
                self.start_date,
                self.end_date,
                self.include_transactions
            )
            
            self.progress_updated.emit(80)
            
            if self.include_monthly_comparison:
                self.status_updated.emit("Generazione confronto mensile...")
                # TODO: Aggiungere confronto mensile al file Excel
                pass
            
            self.status_updated.emit("Report completato!")
            self.progress_updated.emit(100)
            
            self.report_completed.emit(file_path)
            
        except Exception as e:
            self.report_failed.emit(str(e))


class ReportsWidget(QWidget):
    """Widget principale per i report"""
    
    def __init__(self, db_manager, report_generator):
        super().__init__()
        self.db_manager = db_manager
        self.report_generator = report_generator
        self.report_worker = None
        self.init_ui()
        
        # Carica dati iniziali
        QTimer.singleShot(500, self.refresh_quick_stats)
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header
        self.create_header(layout)
        
        # Tab widget per diverse tipologie di report
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Tab 1: Report Finanziario
        self.create_financial_report_tab(tab_widget)
        
        # Tab 2: Confronto Mensile
        self.create_monthly_comparison_tab(tab_widget)
        
        # Tab 3: Analisi Categorie
        self.create_category_analysis_tab(tab_widget)
        
        # Area di stato
        self.create_status_area(layout)
    
    def create_header(self, parent_layout):
        """Crea l'header del widget"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #8E44AD, stop:1 #9B59B6);
                border-radius: 10px;
                color: white;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("📊 Report e Analisi")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Genera report dettagliati e analizza le performance del tuo bar")
        subtitle.setStyleSheet("color: white; font-size: 14px;")
        header_layout.addWidget(subtitle)
        
        parent_layout.addWidget(header_frame)
    
    def create_financial_report_tab(self, parent):
        """Crea il tab per il report finanziario"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Configurazione report
        config_group = QGroupBox("Configurazione Report")
        config_layout = QFormLayout(config_group)
        
        # Periodo
        period_layout = QHBoxLayout()
        
        self.financial_start_date = QDateEdit()
        self.financial_start_date.setCalendarPopup(True)
        self.financial_start_date.setDate(QDate.currentDate().addMonths(-1))
        period_layout.addWidget(QLabel("Da:"))
        period_layout.addWidget(self.financial_start_date)
        
        self.financial_end_date = QDateEdit()
        self.financial_end_date.setCalendarPopup(True)
        self.financial_end_date.setDate(QDate.currentDate())
        period_layout.addWidget(QLabel("A:"))
        period_layout.addWidget(self.financial_end_date)
        
        period_layout.addStretch()
        
        config_layout.addRow("Periodo:", period_layout)
        
        # Opzioni
        self.include_transactions_check = QCheckBox("Includi dettaglio transazioni")
        self.include_transactions_check.setChecked(True)
        config_layout.addRow("Dettagli:", self.include_transactions_check)
        
        self.include_charts_check = QCheckBox("Includi grafici nel report")
        self.include_charts_check.setChecked(True)
        config_layout.addRow("Grafici:", self.include_charts_check)
        
        layout.addWidget(config_group)
        
        # Anteprima veloce
        preview_group = QGroupBox("Anteprima Dati")
        preview_layout = QVBoxLayout(preview_group)
        
        # Statistiche rapide
        self.quick_stats_layout = QHBoxLayout()
        preview_layout.addLayout(self.quick_stats_layout)
        
        # Tabella riassuntiva
        self.financial_summary_table = QTableWidget()
        self.financial_summary_table.setMaximumHeight(200)
        preview_layout.addWidget(self.financial_summary_table)
        
        layout.addWidget(preview_group)
        
        # Azioni
        actions_layout = QHBoxLayout()
        
        preview_btn = QPushButton("👁️ Anteprima")
        preview_btn.clicked.connect(self.preview_financial_report)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        actions_layout.addWidget(preview_btn)
        
        actions_layout.addStretch()
        
        generate_btn = QPushButton("📊 Genera Report Excel")
        generate_btn.clicked.connect(self.generate_financial_report)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        actions_layout.addWidget(generate_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "💰 Report Finanziario")
    
    def create_monthly_comparison_tab(self, parent):
        """Crea il tab per il confronto mensile"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Configurazione
        config_group = QGroupBox("Configurazione Confronto")
        config_layout = QFormLayout(config_group)
        
        self.months_back_spinbox = QSpinBox()
        self.months_back_spinbox.setRange(3, 24)
        self.months_back_spinbox.setValue(6)
        self.months_back_spinbox.setSuffix(" mesi")
        config_layout.addRow("Numero mesi da confrontare:", self.months_back_spinbox)
        
        layout.addWidget(config_group)
        
        # Area visualizzazione
        visualization_group = QGroupBox("Confronto Mensile")
        visualization_layout = QVBoxLayout(visualization_group)
        
        # WebView per i grafici
        self.monthly_chart_webview = QWebEngineView()
        self.monthly_chart_webview.setMinimumHeight(400)
        visualization_layout.addWidget(self.monthly_chart_webview)
        
        # Tabella dati
        self.monthly_data_table = QTableWidget()
        self.monthly_data_table.setMaximumHeight(200)
        visualization_layout.addWidget(self.monthly_data_table)
        
        layout.addWidget(visualization_group)
        
        # Azioni
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Aggiorna Confronto")
        refresh_btn.clicked.connect(self.refresh_monthly_comparison)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        
        export_btn = QPushButton("📊 Esporta Confronto")
        export_btn.clicked.connect(self.export_monthly_comparison)
        actions_layout.addWidget(export_btn)
        
        layout.addLayout(actions_layout)
        
        parent.addTab(tab_widget, "📈 Confronto Mensile")
    
    def create_category_analysis_tab(self, parent):
        """Crea il tab per l'analisi per categorie"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Filtri
        filters_group = QGroupBox("Filtri Analisi")
        filters_layout = QFormLayout(filters_group)
        
        # Periodo
        period_layout = QHBoxLayout()
        
        self.category_start_date = QDateEdit()
        self.category_start_date.setCalendarPopup(True)
        self.category_start_date.setDate(QDate.currentDate().addMonths(-3))
        period_layout.addWidget(self.category_start_date)
        
        period_layout.addWidget(QLabel(" - "))
        
        self.category_end_date = QDateEdit()
        self.category_end_date.setCalendarPopup(True)
        self.category_end_date.setDate(QDate.currentDate())
        period_layout.addWidget(self.category_end_date)
        
        period_layout.addStretch()
        
        filters_layout.addRow("Periodo:", period_layout)
        
        # Tipo analisi
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Spese per categoria",
            "Entrate per categoria", 
            "Profitto per categoria",
            "Confronto COGS vs Altri costi"
        ])
        filters_layout.addRow("Tipo analisi:", self.analysis_type_combo)
        
        layout.addWidget(filters_group)
        
        # Risultati
        results_group = QGroupBox("Risultati Analisi")
        results_layout = QVBoxLayout(results_group)
        
        # Splitter per tabella e grafico
        splitter = QSplitter(Qt.Horizontal)
        
        # Tabella risultati
        self.category_results_table = QTableWidget()
        splitter.addWidget(self.category_results_table)
        
        # Grafico
        self.category_chart_webview = QWebEngineView()
        splitter.addWidget(self.category_chart_webview)
        
        splitter.setSizes([400, 600])
        results_layout.addWidget(splitter)
        
        layout.addWidget(results_group)
        
        # Azioni
        actions_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("🔍 Analizza")
        analyze_btn.clicked.connect(self.run_category_analysis)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
        """)
        actions_layout.addWidget(analyze_btn)
        
        actions_layout.addStretch()
        
        export_analysis_btn = QPushButton("📊 Esporta Analisi")
        export_analysis_btn.clicked.connect(self.export_category_analysis)
        actions_layout.addWidget(export_analysis_btn)
        
        layout.addLayout(actions_layout)
        
        parent.addTab(tab_widget, "📊 Analisi Categorie")
    
    def create_status_area(self, parent_layout):
        """Crea l'area di stato"""
        self.status_frame = QFrame()
        self.status_frame.setVisible(False)
        self.status_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        status_layout = QVBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("font-weight: bold; color: #2C3E50;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(self.status_frame)
    
    def refresh_quick_stats(self):
        """Aggiorna le statistiche rapide"""
        try:
            start_date = self.financial_start_date.date().toString("yyyy-MM-dd")
            end_date = self.financial_end_date.date().toString("yyyy-MM-dd")
            
            # Ottieni dati
            financial_summary = self.db_manager.get_financial_summary(start_date, end_date)
            
            # Pulisci layout precedente
            for i in reversed(range(self.quick_stats_layout.count())):
                self.quick_stats_layout.itemAt(i).widget().setParent(None)
            
            # Crea card statistiche
            stats = [
                ("Entrate", financial_summary['total_income'], "#27AE60"),
                ("Spese", financial_summary['total_expenses'], "#E74C3C"),
                ("Profitto Netto", financial_summary['net_profit'], "#2C3E50")
            ]
            
            for title, value, color in stats:
                card = self.create_stat_card(title, f"€{value:,.2f}", color)
                self.quick_stats_layout.addWidget(card)
            
            # Aggiorna tabella riassuntiva
            self.update_financial_summary_table(financial_summary)
            
        except Exception as e:
            print(f"Errore nell'aggiornamento statistiche: {e}")
    
    def create_stat_card(self, title, value, color):
        """Crea una card per le statistiche"""
        card = QFrame()
        card.setFixedSize(150, 80)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7F8C8D; font-size: 11px; font-weight: 500;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(value_label)
        
        return card
    
    def update_financial_summary_table(self, financial_summary):
        """Aggiorna la tabella riassuntiva finanziaria"""
        data = [
            ("Entrate Totali", financial_summary['total_income']),
            ("COGS (Costi Diretti)", financial_summary['total_cogs']),
            ("Altre Spese", financial_summary['total_expenses'] - financial_summary['total_cogs']),
            ("Spese Totali", financial_summary['total_expenses']),
            ("Profitto Lordo", financial_summary['gross_profit']),
            ("Profitto Netto", financial_summary['net_profit'])
        ]
        
        self.financial_summary_table.setRowCount(len(data))
        self.financial_summary_table.setColumnCount(2)
        self.financial_summary_table.setHorizontalHeaderLabels(["Voce", "Importo (€)"])
        
        for row, (label, value) in enumerate(data):
            # Etichetta
            label_item = QTableWidgetItem(label)
            self.financial_summary_table.setItem(row, 0, label_item)
            
            # Valore
            value_item = QTableWidgetItem(f"{value:,.2f}")
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Colore basato sul tipo
            if "Profitto" in label:
                if value >= 0:
                    value_item.setForeground(QColor("#27AE60"))
                else:
                    value_item.setForeground(QColor("#E74C3C"))
            elif "Spese" in label or "COGS" in label:
                value_item.setForeground(QColor("#E74C3C"))
            else:
                value_item.setForeground(QColor("#27AE60"))
            
            self.financial_summary_table.setItem(row, 1, value_item)
        
        # Ridimensiona colonne
        header = self.financial_summary_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
    
    def preview_financial_report(self):
        """Mostra anteprima del report finanziario"""
        self.refresh_quick_stats()
        QMessageBox.information(
            self,
            "Anteprima",
            "L'anteprima è mostrata nella tabella sopra.\n"
            "Clicca 'Genera Report Excel' per creare il file completo."
        )
    
    def generate_financial_report(self):
        """Genera il report finanziario Excel"""
        if self.report_worker and self.report_worker.isRunning():
            QMessageBox.warning(self, "Avviso", "Un report è già in generazione")
            return
        
        start_date = self.financial_start_date.date().toString("yyyy-MM-dd")
        end_date = self.financial_end_date.date().toString("yyyy-MM-dd")
        include_transactions = self.include_transactions_check.isChecked()
        
        # Mostra progresso
        self.show_progress("Generazione report...")
        
        # Avvia worker
        self.report_worker = ReportGenerationWorker(
            self.report_generator,
            start_date,
            end_date,
            include_transactions,
            False
        )
        
        self.report_worker.progress_updated.connect(self.progress_bar.setValue)
        self.report_worker.status_updated.connect(self.status_label.setText)
        self.report_worker.report_completed.connect(self.on_report_completed)
        self.report_worker.report_failed.connect(self.on_report_failed)
        self.report_worker.start()
    
    def refresh_monthly_comparison(self):
        """Aggiorna il confronto mensile"""
        try:
            months_back = self.months_back_spinbox.value()
            comparison_data = self.report_generator.get_monthly_comparison(months_back)
            
            # Aggiorna grafico
            if comparison_data['chart']:
                self.monthly_chart_webview.setHtml(comparison_data['chart'])
            
            # Aggiorna tabella
            monthly_data = comparison_data['monthly_data']
            
            if monthly_data:
                self.monthly_data_table.setRowCount(len(monthly_data))
                self.monthly_data_table.setColumnCount(5)
                self.monthly_data_table.setHorizontalHeaderLabels([
                    "Mese", "Entrate (€)", "Spese (€)", "Profitto Lordo (€)", "Profitto Netto (€)"
                ])
                
                for row, data in enumerate(monthly_data):
                    items = [
                        data['month_name'],
                        f"{data['total_income']:,.2f}",
                        f"{data['total_expenses']:,.2f}",
                        f"{data['gross_profit']:,.2f}",
                        f"{data['net_profit']:,.2f}"
                    ]
                    
                    for col, item_text in enumerate(items):
                        item = QTableWidgetItem(item_text)
                        if col > 0:  # Valori numerici
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        self.monthly_data_table.setItem(row, col, item)
                
                # Ridimensiona colonne
                header = self.monthly_data_table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Stretch)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel confronto mensile: {e}")
    
    def run_category_analysis(self):
        """Esegue l'analisi per categorie"""
        try:
            start_date = self.category_start_date.date().toString("yyyy-MM-dd")
            end_date = self.category_end_date.date().toString("yyyy-MM-dd")
            
            # Ottieni dati dashboard per analisi categorie
            dashboard_data = self.report_generator.generate_dashboard_data(start_date, end_date)
            category_analysis = dashboard_data['category_analysis']
            
            # Aggiorna tabella risultati
            categories = category_analysis['categories']
            analysis_type = self.analysis_type_combo.currentText()
            
            if categories:
                self.category_results_table.setRowCount(len(categories))
                
                if "Spese" in analysis_type:
                    headers = ["Categoria", "Spese (€)", "% sul Totale", "N. Transazioni"]
                    self.category_results_table.setColumnCount(4)
                    
                    for row, cat in enumerate(categories):
                        if cat['expenses'] > 0:
                            items = [
                                cat['name'],
                                f"{cat['expenses']:,.2f}",
                                f"{cat['expense_percentage']:.1f}%",
                                str(cat['transaction_count'])
                            ]
                            
                            for col, item_text in enumerate(items):
                                item = QTableWidgetItem(item_text)
                                if col in [1, 2]:
                                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                self.category_results_table.setItem(row, col, item)
                
                elif "Entrate" in analysis_type:
                    headers = ["Categoria", "Entrate (€)", "% sul Totale", "N. Transazioni"]
                    self.category_results_table.setColumnCount(4)
                    
                    for row, cat in enumerate(categories):
                        if cat['income'] > 0:
                            items = [
                                cat['name'],
                                f"{cat['income']:,.2f}",
                                f"{cat['income_percentage']:.1f}%",
                                str(cat['transaction_count'])
                            ]
                            
                            for col, item_text in enumerate(items):
                                item = QTableWidgetItem(item_text)
                                if col in [1, 2]:
                                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                self.category_results_table.setItem(row, col, item)
                
                self.category_results_table.setHorizontalHeaderLabels(headers)
                
                # Ridimensiona colonne
                header = self.category_results_table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.Stretch)
            
            # Aggiorna grafico (usa quello della dashboard)
            charts = dashboard_data.get('charts', {})
            if 'expense_pie' in charts and "Spese" in analysis_type:
                self.category_chart_webview.setHtml(charts['expense_pie'])
            elif 'income_pie' in charts and "Entrate" in analysis_type:
                self.category_chart_webview.setHtml(charts['income_pie'])
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'analisi categorie: {e}")
    
    def export_monthly_comparison(self):
        """Esporta il confronto mensile"""
        try:
            months_back = self.months_back_spinbox.value()
            
            # Per ora usa il report generator standard
            file_path = self.report_generator.export_to_excel(include_transactions=False)
            
            QMessageBox.information(
                self,
                "Export Completato",
                f"Confronto mensile esportato!\n\nFile: {file_path}"
            )
            
            # Opzione per aprire cartella
            reply = QMessageBox.question(
                self,
                "Aprire Cartella?",
                "Vuoi aprire la cartella contenente il file?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                folder_path = os.path.dirname(file_path)
                subprocess.run(f'explorer "{folder_path}"', shell=True)
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'export: {e}")
    
    def export_category_analysis(self):
        """Esporta l'analisi per categorie"""
        try:
            start_date = self.category_start_date.date().toString("yyyy-MM-dd")
            end_date = self.category_end_date.date().toString("yyyy-MM-dd")
            
            file_path = self.report_generator.export_to_excel(start_date, end_date, include_transactions=True)
            
            QMessageBox.information(
                self,
                "Export Completato",
                f"Analisi categorie esportata!\n\nFile: {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'export: {e}")
    
    def show_progress(self, message):
        """Mostra la barra di progresso"""
        self.status_frame.setVisible(True)
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
    
    def hide_progress(self):
        """Nasconde la barra di progresso"""
        self.status_frame.setVisible(False)
    
    def on_report_completed(self, file_path):
        """Gestisce il completamento del report"""
        self.hide_progress()
        
        QMessageBox.information(
            self,
            "Report Completato",
            f"✅ Report generato con successo!\n\nFile salvato in:\n{file_path}"
        )
        
        # Opzione per aprire cartella
        reply = QMessageBox.question(
            self,
            "Aprire Cartella?",
            "Vuoi aprire la cartella contenente il file?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            folder_path = os.path.dirname(file_path)
            subprocess.run(f'explorer "{folder_path}"', shell=True)
    
    def on_report_failed(self, error_message):
        """Gestisce l'errore nella generazione del report"""
        self.hide_progress()
        
        QMessageBox.critical(
            self,
            "Errore Report",
            f"❌ Errore nella generazione del report:\n\n{error_message}"
        )