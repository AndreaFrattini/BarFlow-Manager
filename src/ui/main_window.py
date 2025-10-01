"""
Finestra principale dell'applicazione BarFlow
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QStackedWidget, QLabel,
                              QMessageBox, QStatusBar, QToolBar, QSplitter,
                              QListWidget, QListWidgetItem, QFrame)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon, QFont, QPixmap, QAction

# Importa i moduli del nostro progetto
sys.path.append(str(Path(__file__).parent.parent))
from database.database_manager import DatabaseManager
from reports.report_generator import ReportGenerator
from utils.common_utils import ConfigUtils, DataConsistencyChecker, MessageUtils


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione BarFlow"""
    
    def __init__(self):
        super().__init__()
        
        # Inizializza componenti core
        self.db_manager = DatabaseManager()
        self.report_generator = ReportGenerator(self.db_manager)
        self.consistency_checker = DataConsistencyChecker(self.db_manager)
        self.config = ConfigUtils.load_config()
        
        # Inizializza UI
        self.init_ui()
        self.setup_connections()
        
        # Controlla coerenza dati all'avvio
        self.check_data_consistency()
        
        # Timer per aggiornamenti periodici
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(300000)  # Aggiorna ogni 5 minuti
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle("BarFlow - Gestione Finanziaria Bar")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter per dividere sidebar e contenuto
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sidebar di navigazione
        self.create_sidebar(splitter)
        
        # Area contenuto principale
        self.create_main_content(splitter)
        
        # Imposta proporzioni splitter
        splitter.setSizes([250, 1150])
        splitter.setCollapsible(0, False)  # Sidebar non collassabile
        
        # Barra di stato
        self.create_status_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Applica stile
        self.apply_styles()
    
    def create_sidebar(self, parent):
        """Crea la sidebar di navigazione"""
        # Frame per la sidebar
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(250)
        sidebar_frame.setFrameStyle(QFrame.StyledPanel)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-right: 2px solid #34495E;
            }
        """)
        
        # Layout della sidebar
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # Logo/Titolo
        title_label = QLabel("BarFlow")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: #34495E;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        sidebar_layout.addWidget(title_label)
        
        # Lista di navigazione
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: white;
                padding: 15px;
                margin: 2px 0;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background-color: #34495E;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
                color: white;
            }
        """)
        
        # Elementi di navigazione
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("💰 Transazioni", "transactions"),
            ("📁 Importa Dati", "import"),
            ("📈 Report", "reports"),
            ("⚙️ Impostazioni", "settings")
        ]
        
        for text, key in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.nav_list.addItem(item)
        
        sidebar_layout.addWidget(self.nav_list)
        
        # Spazio flessibile
        sidebar_layout.addStretch()
        
        # Informazioni app
        info_label = QLabel("v1.0.0\n© 2025 BarFlow")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #BDC3C7;
                font-size: 10px;
                padding: 10px;
            }
        """)
        sidebar_layout.addWidget(info_label)
        
        parent.addWidget(sidebar_frame)
    
    def create_main_content(self, parent):
        """Crea l'area del contenuto principale"""
        # Widget contenitore per il contenuto
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header del contenuto
        self.content_header = QLabel("Dashboard")
        self.content_header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2C3E50;
                padding: 10px 0;
                border-bottom: 2px solid #3498DB;
                margin-bottom: 20px;
            }
        """)
        content_layout.addWidget(self.content_header)
        
        # Stack widget per le diverse sezioni
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Crea le diverse sezioni
        self.create_sections()
        
        parent.addWidget(content_widget)
    
    def create_sections(self):
        """Crea le sezioni dell'applicazione"""
        # Dashboard
        from .dashboard_widget import DashboardWidget
        self.dashboard_widget = DashboardWidget(self.db_manager, self.report_generator)
        self.content_stack.addWidget(self.dashboard_widget)
        
        # Transazioni
        from .transactions_widget import TransactionsWidget
        self.transactions_widget = TransactionsWidget(self.db_manager)
        self.content_stack.addWidget(self.transactions_widget)
        
        # Import dati
        from .import_widget import ImportWidget
        self.import_widget = ImportWidget(self.db_manager)
        self.content_stack.addWidget(self.import_widget)
        
        # Report
        from .reports_widget import ReportsWidget
        self.reports_widget = ReportsWidget(self.db_manager, self.report_generator)
        self.content_stack.addWidget(self.reports_widget)
        
        # Impostazioni
        from .settings_widget import SettingsWidget
        self.settings_widget = SettingsWidget(self.config)
        self.content_stack.addWidget(self.settings_widget)
    
    def create_status_bar(self):
        """Crea la barra di stato"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Messaggio di default
        self.status_bar.showMessage("Pronto")
        
        # Label per informazioni database
        self.db_info_label = QLabel()
        self.update_db_info()
        self.status_bar.addPermanentWidget(self.db_info_label)
    
    def create_toolbar(self):
        """Crea la toolbar"""
        toolbar = QToolBar("Principale")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Azione aggiorna
        refresh_action = QAction("🔄 Aggiorna", self)
        refresh_action.setStatusTip("Aggiorna i dati della dashboard")
        refresh_action.triggered.connect(self.update_dashboard)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Azione esporta
        export_action = QAction("📊 Esporta Report", self)
        export_action.setStatusTip("Esporta report Excel")
        export_action.triggered.connect(self.quick_export)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Azione verifica coerenza
        check_action = QAction("✅ Verifica Dati", self)
        check_action.setStatusTip("Verifica coerenza dei dati")
        check_action.triggered.connect(self.check_data_consistency)
        toolbar.addAction(check_action)
    
    def apply_styles(self):
        """Applica gli stili globali"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECF0F1;
            }
            QToolBar {
                background-color: white;
                border: 1px solid #BDC3C7;
                padding: 5px;
                spacing: 10px;
            }
            QToolBar QToolButton {
                padding: 8px 12px;
                margin: 2px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                background-color: white;
            }
            QToolBar QToolButton:hover {
                background-color: #F8F9FA;
                border-color: #3498DB;
            }
            QStatusBar {
                background-color: white;
                border-top: 1px solid #BDC3C7;
                padding: 5px;
            }
        """)
    
    def setup_connections(self):
        """Configura le connessioni dei segnali"""
        # Navigazione
        self.nav_list.currentRowChanged.connect(self.change_section)
        
        # Connessioni tra widget
        if hasattr(self, 'import_widget'):
            self.import_widget.data_imported.connect(self.on_data_imported)
        
        if hasattr(self, 'transactions_widget'):
            self.transactions_widget.transaction_changed.connect(self.update_dashboard)
    
    def change_section(self, index):
        """Cambia sezione in base alla selezione della sidebar"""
        if index < 0:
            return
        
        section_names = ["Dashboard", "Transazioni", "Importa Dati", "Report", "Impostazioni"]
        
        if index < len(section_names):
            self.content_header.setText(section_names[index])
            self.content_stack.setCurrentIndex(index)
            
            # Aggiorna contenuto se necessario
            if index == 0:  # Dashboard
                self.update_dashboard()
            elif index == 1:  # Transazioni
                if hasattr(self.transactions_widget, 'refresh_data'):
                    self.transactions_widget.refresh_data()
    
    def update_dashboard(self):
        """Aggiorna i dati della dashboard"""
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.refresh_data()
        
        self.update_db_info()
        self.status_bar.showMessage("Dashboard aggiornata", 2000)
    
    def update_db_info(self):
        """Aggiorna le informazioni del database nella status bar"""
        try:
            transactions = self.db_manager.get_transactions()
            count = len(transactions)
            
            if count == 0:
                self.db_info_label.setText("Nessuna transazione")
            else:
                latest_date = max(t['transaction_date'] for t in transactions)
                self.db_info_label.setText(f"Transazioni: {count} | Ultima: {latest_date}")
                
        except Exception as e:
            self.db_info_label.setText("Errore database")
    
    def check_data_consistency(self):
        """Verifica la coerenza dei dati"""
        try:
            # Verifica granularità
            is_consistent, granularities, error_msg = self.consistency_checker.check_granularity_consistency()
            
            if not is_consistent:
                QMessageBox.warning(
                    self,
                    "Inconsistenza Dati",
                    f"⚠️ {error_msg}\n\n"
                    "Per risolvere:\n"
                    "1. Rimuovi le fonti con granularità diverse\n"
                    "2. Oppure raggruppa i dati alla stessa granularità\n"
                    "3. Reimporta i dati corretti"
                )
                return
            
            # Verifica date
            date_valid, date_error = self.consistency_checker.check_date_ranges()
            if not date_valid:
                QMessageBox.warning(self, "Date Non Valide", f"⚠️ {date_error}")
                return
            
            # Verifica importi
            amounts_valid, amounts_error = self.consistency_checker.check_amounts_validity()
            if not amounts_valid:
                QMessageBox.warning(self, "Importi Non Validi", f"⚠️ {amounts_error}")
                return
            
            # Tutto OK
            QMessageBox.information(
                self,
                "Verifica Completata",
                "✅ Tutti i controlli di coerenza sono stati superati.\n"
                "I dati sono pronti per l'analisi."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore Verifica",
                f"❌ Errore durante la verifica dei dati:\n{str(e)}"
            )
    
    def quick_export(self):
        """Esportazione rapida report"""
        try:
            file_path = self.report_generator.export_to_excel()
            
            QMessageBox.information(
                self,
                "Export Completato",
                f"✅ Report esportato con successo!\n\n"
                f"File salvato in:\n{file_path}\n\n"
                "Il file si trova nella cartella Temp del sistema."
            )
            
            # Opzionalmente apri la cartella
            import os
            import subprocess
            
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
            QMessageBox.critical(
                self,
                "Errore Export",
                f"❌ Errore durante l'esportazione:\n{str(e)}"
            )
    
    def on_data_imported(self, count):
        """Gestisce l'evento di importazione dati"""
        self.update_dashboard()
        self.status_bar.showMessage(f"Importate {count} transazioni", 5000)
        
        # Verifica automaticamente la coerenza dopo l'import
        QTimer.singleShot(1000, self.check_data_consistency)
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        reply = QMessageBox.question(
            self,
            "Conferma Chiusura",
            "Sei sicuro di voler chiudere BarFlow?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Salva configurazione
            ConfigUtils.save_config(self.config)
            event.accept()
        else:
            event.ignore()


def main():
    """Funzione principale"""
    app = QApplication(sys.argv)
    
    # Imposta informazioni applicazione
    app.setApplicationName("BarFlow")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BarFlow Solutions")
    
    # Crea e mostra la finestra principale
    window = MainWindow()
    window.show()
    
    # Avvia l'applicazione
    sys.exit(app.exec())


if __name__ == "__main__":
    main()