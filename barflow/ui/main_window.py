"""
Finestra principale dell'applicazione AccountFlow
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QMessageBox, QFileDialog,
                              QListWidget, QListWidgetItem, 
                              QFrame, QStackedWidget, QApplication)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import pandas as pd
from datetime import datetime
import os
import sys
import platform
from .import_widget import ImportWidget
from .transactions_widget import TransactionsWidget
from .welcome_widget import WelcomeWidget
from .analysis_widget import AnalysisWidget
from .history_management_widget import HistoryManagementWidget
from barflow.data.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione AccountFlow"""
    
    def __init__(self):
        super().__init__()
        
        # Imposta l'icona della finestra
        self.set_window_icon()
        
        # Inizializza database manager
        self.db_manager = DatabaseManager()
        
        # Inizializza con dati temporanei vuoti (per tabella Transazioni e Analisi Attuale)
        self.transactions_data = []  # Dati temporanei caricati dall'utente
        
        # Inizializza UI
        self.init_ui()
        self.setup_connections()
        
        # Inizializza le viste vuote
        self._refresh_all_views()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle("AccountFlow - Gestione Finanziaria")
        
        # Calcola le dimensioni ottimali in base allo schermo
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            # Usa l'80% della larghezza e altezza disponibile dello schermo
            width = min(1200, int(screen_geometry.width() * 0.8))
            height = min(800, int(screen_geometry.height() * 0.8))
            self.resize(width, height)
        else:
            # Fallback se non riesce a rilevare lo schermo
            self.resize(1000, 700)
        
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
        
        title_label = QLabel("AccountFlow")
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
            ("⚙️ Gestione Dati Storici", "historical_data_management"),
            ("📤 Esporta Storico", "export")
        ]
        
        for text, key in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.nav_list.addItem(item)
        
        sidebar_layout.addWidget(self.nav_list)
        
        info_label = QLabel("v1.0.0\n© 2025 AccountFlow")
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
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Crea i widget delle diverse sezioni
        self.welcome_widget = WelcomeWidget()
        self.import_widget = ImportWidget()
        self.transactions_widget = TransactionsWidget()
        self.analysis_widget = AnalysisWidget()
        self.history_management_widget = HistoryManagementWidget()
        
        # Aggiungi i widget allo stacked widget
        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.import_widget)
        self.stacked_widget.addWidget(self.transactions_widget)
        self.stacked_widget.addWidget(self.analysis_widget)
        self.stacked_widget.addWidget(self.history_management_widget)

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
        self.transactions_widget.save_requested.connect(self.save_and_update_history)
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
            # Mostra sempre solo i dati temporanei nella tabella Transazioni
            self.transactions_widget.update_table(self.transactions_data)
        elif key == "analysis":
            self.stacked_widget.setCurrentWidget(self.analysis_widget)
            # Analisi Attuale usa solo i dati temporanei
            self.analysis_widget.update_data(self.transactions_data)
        elif key == "historical_data_management":
            self.stacked_widget.setCurrentWidget(self.history_management_widget)
            # Carica i dati solo se non sono ancora stati caricati
            self.history_management_widget.load_data_if_needed()
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
            elif current_widget == self.history_management_widget:
                self.nav_list.setCurrentRow(4)
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
        import_timestamp = datetime.now().timestamp()
        
        for row in data:
            # Aggiungi la colonna SORGENTE al record e timestamp di importazione
            row['SORGENTE'] = sorgente_value
            row['_IMPORT_TIMESTAMP'] = import_timestamp
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
        """Esporta tutto lo storico in un file XLSX"""
        # Carica i dati storici
        historical_data = self.db_manager.load_all_transactions()
        
        # Controllo che ci siano dati storici
        if not historical_data:
            QMessageBox.warning(
                self, 
                "Errore - Nessun dato storico", 
                "Non ci sono dati storici da esportare.\nSalva prima dei dati utilizzando la sezione 'Transazioni' o 'Gestione Dati Storici'."
            )
            return

        # Genera il nome del file con timestamp
        today = datetime.now().strftime("%Y-%m-%d")
        default_filename = f"{today}_storico_accountflow.xlsx"

        # Finestra di dialogo per scegliere dove salvare il file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Esporta Storico - Scegli dove salvare", 
            default_filename, 
            "File Excel (*.xlsx)"
        )

        if file_path:
            try:
                df_hist = pd.DataFrame(historical_data)
                df_hist['IMPORTO'] = pd.to_numeric(df_hist['IMPORTO'], errors='coerce')
                df_hist['DATA_PARSED'] = pd.to_datetime(df_hist['DATA'], dayfirst=True, errors='coerce')
                df_hist = df_hist.dropna(subset=['IMPORTO'])
                
                # Prepara il foglio "Transazioni Storico"
                transazioni_storiche_df = df_hist.copy()
                
                # Formatta le date storiche
                def format_hist_date(row):
                    if pd.notna(row['DATA_PARSED']):
                        return row['DATA_PARSED'].strftime('%d-%m-%Y')
                    else:
                        original_date = str(row['DATA']) if pd.notna(row['DATA']) else ''
                        if original_date.strip() == '' or original_date.lower() == 'nan':
                            return "Data non disponibile"
                        else:
                            return f"Data non valida: {original_date}"
                
                transazioni_storiche_df['DATA'] = transazioni_storiche_df.apply(format_hist_date, axis=1)
                transazioni_storiche_df['IMPORTO'] = transazioni_storiche_df['IMPORTO'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "0.00")
                
                # Rimuovi colonna temporanea
                if 'DATA_PARSED' in transazioni_storiche_df.columns:
                    transazioni_storiche_df = transazioni_storiche_df.drop('DATA_PARSED', axis=1)
                
                # Riordina le colonne
                colonne_ordinate = ["DATA", "SORGENTE", "PRODOTTO", "FORNITORE", "CATEGORIA", "QUANTITA'", "IMPORTO"]
                transazioni_storiche_df = transazioni_storiche_df[colonne_ordinate]

                # Esporta in Excel con un solo foglio
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Foglio "Transazioni Storico" con tutti i dati storici
                    transazioni_storiche_df.to_excel(writer, index=False, sheet_name='Transazioni Storico')

                QMessageBox.information(
                    self, 
                    "Esportazione completata", 
                    f"File storico salvato con successo in:\n{file_path}\n\nIl file contiene {len(transazioni_storiche_df)} transazioni storiche."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Errore durante l'esportazione", 
                    f"Si è verificato un errore durante il salvataggio del file:\n\n{str(e)}"
                )
    
    def _refresh_all_views(self):
        """Aggiorna tutte le viste con i dati correnti."""
        self.transactions_widget.update_table(self.transactions_data)
        self.analysis_widget.update_data(self.transactions_data)
    
    def save_and_update_history(self):
        """Salva le transazioni temporanee nello storico e svuota la tabella temporanea."""
        if not self.transactions_data:
            QMessageBox.warning(self, "Nessun dato", 
                              "Non ci sono transazioni da salvare.")
            return
        
        try:
            # Salva le transazioni temporanee nel database
            saved, duplicates = self.db_manager.save_transactions(
                self.transactions_data, 
                file_origin=f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Svuota i dati temporanei dopo il salvataggio
            self.transactions_data = []
            
            # Aggiorna le viste (ora vuote per la tabella temporanea)
            self._refresh_all_views()
            
            stats = self.db_manager.get_database_stats()
            
            QMessageBox.information(self, "Salvataggio completato", 
                f"Salvate {saved} nuove transazioni nello storico (saltati {duplicates} duplicati).\n"
                f"La tabella temporanea è stata svuotata.\n"
                f"Database storico contiene ora {stats['total_records']} transazioni totali.\n"
                f"Periodo storico: {stats['date_range'][0]} - {stats['date_range'][1]}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", 
                               f"Errore durante il salvataggio: {e}")
    
    def set_window_icon(self):
        """Imposta l'icona della finestra per tutte le piattaforme"""
        icon_filename = self._get_platform_icon_filename()
        icon_path = None
        
        # Percorso base alle icone - gestisce sia ambiente di sviluppo che app pacchettizzata
        current_dir = os.path.dirname(os.path.abspath(__file__))
        barflow_dir = os.path.dirname(current_dir)
        
        # Lista di possibili percorsi da provare in ordine di priorità
        possible_paths = [
            # Struttura di sviluppo
            os.path.join(os.path.dirname(barflow_dir), 'resources', 'icons'),
            # Struttura app pacchettizzata - risorse accanto al modulo barflow
            os.path.join(barflow_dir, 'resources', 'icons'),
            # Struttura Briefcase - risorse nella directory principale dell'app
            os.path.join(os.path.dirname(os.path.dirname(barflow_dir)), 'resources', 'icons'),
            # Struttura Briefcase alternativa - risorse nella directory app
            os.path.join(os.path.dirname(barflow_dir), 'app', 'resources', 'icons'),
        ]
        
        for icons_dir in possible_paths:            
            if not os.path.exists(icons_dir):
                continue
                
            test_icon_path = os.path.join(icons_dir, icon_filename)
            if os.path.exists(test_icon_path):
                icon_path = test_icon_path
                break
            else:
                # Prova formati alternativi
                alt_icon_path = self._find_available_icon(icons_dir)
                if alt_icon_path:
                    icon_path = alt_icon_path
                    break
        
        # Carica l'icona se trovata
        if icon_path and os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                # Imposta l'icona della finestra (barra del titolo)
                self.setWindowIcon(icon)
                # Imposta l'icona dell'applicazione (taskbar)
                QApplication.instance().setWindowIcon(icon)
                
                # Su Windows, imposta anche l'Application User Model ID per una migliore integrazione con la taskbar
                if platform.system().lower() == "windows":
                    try:
                        import ctypes
                        # Imposta l'Application User Model ID per Windows
                        app_id = 'BarFlowTeam.BarFlow.GestioneFinanziaria.1.0'
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                    except Exception as e:
                        print(f"Avviso: Impossibile impostare Application User Model ID: {e}")
                
                print(f"✓ Icona impostata correttamente per finestra e taskbar.")
            except Exception as e:
                print(f"✗ Errore durante il caricamento dell'icona: {e}")
        else:
            print(f"✗ Nessuna icona trovata per il formato: {icon_filename}")
    
    def _get_platform_icon_filename(self):
        """Restituisce il nome del file icona appropriato per la piattaforma corrente"""
        system = platform.system().lower()
        
        if system == "windows":
            return "icon.ico"
        elif system == "darwin":  # macOS
            return "icon.icns"
        else:  # Linux e altre piattaforme Unix
            return "icon.png"
    
    def _find_available_icon(self, icons_dir):
        """Cerca un'icona disponibile come fallback"""
        # Lista di priorità per i formati di icona
        fallback_formats = ["icon.png", "icon.ico", "icon.icns"]
        
        for icon_file in fallback_formats:
            icon_path = os.path.join(icons_dir, icon_file)
            if os.path.exists(icon_path):
                return icon_path
        
        # Se non trova nessuna icona specifica, prova a cercare qualsiasi file immagine
        if os.path.exists(icons_dir):
            for file in os.listdir(icons_dir):
                if file.lower().endswith(('.png', '.ico', '.icns', '.svg')):
                    return os.path.join(icons_dir, file)
        
        return None