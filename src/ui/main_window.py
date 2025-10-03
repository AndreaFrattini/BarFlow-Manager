"""
Finestra principale dell'applicazione BarFlow
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QMessageBox, QFileDialog,
                              QListWidget, QListWidgetItem, 
                              QFrame, QStackedWidget)
from PySide6.QtCore import Qt
import pandas as pd

# Importa i moduli del nostro progetto
from .import_widget import ImportWidget
from .transactions_widget import TransactionsWidget
from .welcome_widget import WelcomeWidget
from .analysis_widget import AnalysisWidget

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione BarFlow"""
    
    def __init__(self):
        super().__init__()
        
        # Inizializza componenti core
        self.transactions_data = []
        
        # Inizializza UI
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle("BarFlow - Gestione Semplificata")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar di navigazione
        self.create_sidebar(main_layout)
        
        # Area contenuto principale
        self.create_main_content(main_layout)
        
        # Applica stile
        self.apply_styles()
    
    def create_sidebar(self, parent_layout):
        """Crea la sidebar di navigazione"""
        sidebar_frame = QFrame()
        sidebar_frame.setMinimumWidth(220)
        sidebar_frame.setMaximumWidth(280)
        sidebar_frame.setFrameStyle(QFrame.StyledPanel)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-right: 2px solid #34495E;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
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
        
        nav_items = [
            ("🏠 Home", "home"),
            ("📥 Importa dati", "import"),
            ("💸 Transazioni", "transactions"),
            ("📊 Analisi", "analysis"),
            ("📤 Esporta risultati", "export")
        ]
        
        for text, key in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.nav_list.addItem(item)
        
        sidebar_layout.addWidget(self.nav_list)
        
        info_label = QLabel("v2.0.0\n© 2025 BarFlow Simplified")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #BDC3C7;
                font-size: 10px;
                padding: 10px;
            }
        """)
        sidebar_layout.addWidget(info_label)
        
        parent_layout.addWidget(sidebar_frame)
    
    def create_main_content(self, parent_layout):
        """Crea l'area del contenuto principale"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Crea i widget delle diverse sezioni
        self.welcome_widget = WelcomeWidget()
        self.import_widget = ImportWidget()
        self.transactions_widget = TransactionsWidget()
        self.analysis_widget = AnalysisWidget()
        
        # Aggiungi i widget allo stacked widget
        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.import_widget)
        self.stacked_widget.addWidget(self.transactions_widget)
        self.stacked_widget.addWidget(self.analysis_widget)

        # Imposta il widget di benvenuto come predefinito
        self.stacked_widget.setCurrentWidget(self.welcome_widget)
        
        parent_layout.addWidget(content_widget)
    
    def apply_styles(self):
        """Applica gli stili globali"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECF0F1;
            }
        """)
    
    def setup_connections(self):
        """Configura le connessioni dei segnali"""
        self.nav_list.currentRowChanged.connect(self.change_section)
        self.import_widget.data_imported.connect(self.handle_data_import)
        # Deseleziona qualsiasi elemento all'avvio per mostrare la pagina di benvenuto
        self.nav_list.setCurrentRow(-1)

    def change_section(self, index):
        """Cambia sezione in base alla selezione della sidebar"""
        item = self.nav_list.item(index)
        if not item:
            return
            
        key = item.data(Qt.UserRole)
        
        if key == "home":
            self.stacked_widget.setCurrentWidget(self.welcome_widget)
        elif key == "import":
            self.stacked_widget.setCurrentWidget(self.import_widget)
        elif key == "transactions":
            self.stacked_widget.setCurrentWidget(self.transactions_widget)
            self.transactions_widget.update_table(self.transactions_data)
        elif key == "analysis":
            self.stacked_widget.setCurrentWidget(self.analysis_widget)
            self.analysis_widget.update_data(self.transactions_data)
        elif key == "export":
            self.export_results()
            # Rimani sulla sezione corrente
            self.nav_list.blockSignals(True)
            # Trova l'indice della vista corrente e reimpostalo
            current_widget = self.stacked_widget.currentWidget()
            if current_widget == self.welcome_widget:
                self.nav_list.setCurrentRow(0)
            elif current_widget == self.import_widget:
                self.nav_list.setCurrentRow(1)
            elif current_widget == self.transactions_widget:
                self.nav_list.setCurrentRow(2)
            elif current_widget == self.analysis_widget:
                self.nav_list.setCurrentRow(3)
            self.nav_list.blockSignals(False)


    def handle_data_import(self, source_type, data):
        """Gestisce i dati importati e li aggiunge al dataset principale"""
        # Mappa i tipi di sorgente ai valori richiesti
        source_mapping = {
            "Fornitore": "fornitore",
            "POS": "pos",
            "Manuale": "manuale"
        }
        
        sorgente_value = source_mapping.get(source_type, source_type.lower())
        
        for row in data:
            # Aggiungi la colonna SORGENTE al record
            row['SORGENTE'] = sorgente_value
            self.transactions_data.append(row)
        
        # Il popup di successo è ora gestito in ImportWidget
        
        # Aggiorna la tabella delle transazioni se è la vista corrente
        if self.stacked_widget.currentWidget() == self.transactions_widget:
            self.transactions_widget.update_table(self.transactions_data)
        else:
            # Passa alla vista transazioni per mostrare i dati aggiornati
            # Trova l'indice corretto per "transactions"
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                if item.data(Qt.UserRole) == "transactions":
                    self.nav_list.setCurrentRow(i)
                    break
        self.transactions_widget.update_table(self.transactions_data)
        self.analysis_widget.update_data(self.transactions_data)

    def export_results(self):
        """Esporta i risultati aggregati in un file XLSX"""
        if not self.transactions_data:
            QMessageBox.warning(self, "Nessun dato", "Non ci sono dati da esportare.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salva File", "", "Excel Files (*.xlsx)")

        if file_path:
            try:
                df = pd.DataFrame(self.transactions_data)
                
                # Assicurati che la colonna 'IMPORTO' sia numerica
                df['IMPORTO'] = pd.to_numeric(df['IMPORTO'])

                entrate = df[df['IMPORTO'] > 0]['IMPORTO'].sum()
                uscite = df[df['IMPORTO'] < 0]['IMPORTO'].sum()
                guadagno_netto = df['IMPORTO'].sum()

                summary_df = pd.DataFrame({
                    'Metrica': ['Entrate Totali', 'Uscite Totali', 'Guadagno Netto'],
                    'Valore': [entrate, uscite, guadagno_netto]
                })

                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    summary_df.to_excel(writer, index=False, sheet_name='Riepilogo')
                    df.to_excel(writer, index=False, sheet_name='Dettaglio Transazioni')

                QMessageBox.information(self, "Esportazione completata", f"File salvato con successo in:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Errore Esportazione", f"Errore durante il salvataggio del file:\n{e}")