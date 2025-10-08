"""
Finestra principale dell'applicazione BarFlow
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QMessageBox, QFileDialog,
                              QListWidget, QListWidgetItem, 
                              QFrame, QStackedWidget, QApplication)
from PySide6.QtCore import Qt
import pandas as pd
from datetime import datetime
from .import_widget import ImportWidget
from .transactions_widget import TransactionsWidget
from .welcome_widget import WelcomeWidget
from .analysis_widget import AnalysisWidget
from .history_management_widget import HistoryManagementWidget
from barflow.data.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione BarFlow"""
    
    def __init__(self):
        super().__init__()
        
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
        self.setWindowTitle("BarFlow - Gestione Semplificata")
        
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
            ("⚙️ Gestione Dati Storici", "historical_data_management"),
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
        """Esporta i risultati aggregati in un file XLSX"""
        # Controllo che ci siano dati caricati
        if not self.transactions_data:
            QMessageBox.warning(
                self, 
                "Errore - Nessun dato", 
                "Non ci sono dati da esportare.\nCarica prima dei dati utilizzando la sezione 'Importa dati'."
            )
            return

        # Genera il nome del file con timestamp
        today = datetime.now().strftime("%Y-%m-%d")
        default_filename = f"{today}_risultati_barflow.xlsx"

        # Finestra di dialogo per scegliere dove salvare il file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Esporta dati - Scegli dove salvare", 
            default_filename, 
            "File Excel (*.xlsx)"
        )

        if file_path:
            try:
                df = pd.DataFrame(self.transactions_data)
                
                # Assicurati che la colonna 'IMPORTO' sia numerica
                df['IMPORTO'] = pd.to_numeric(df['IMPORTO'], errors='coerce')
                
                # Per i dati temporanei, gestisci il formato YYYY-MM-DD specificamente
                # Prova prima il formato ISO (YYYY-MM-DD) poi altri formati
                def parse_temp_date(date_str):
                    if pd.isna(date_str) or str(date_str).strip() == '':
                        return pd.NaT
                    
                    date_str = str(date_str).strip()
                    
                    # Prova formato YYYY-MM-DD (tipico dei dati temporanei)
                    try:
                        return pd.to_datetime(date_str, format='%Y-%m-%d')
                    except:
                        pass
                    
                    # Prova formato DD/MM/YYYY
                    try:
                        return pd.to_datetime(date_str, format='%d/%m/%Y')
                    except:
                        pass
                    
                    # Fallback con dayfirst=True
                    try:
                        return pd.to_datetime(date_str, dayfirst=True)
                    except:
                        return pd.NaT
                
                df['DATA_PARSED'] = df['DATA'].apply(parse_temp_date)
                
                # Rimuovi righe con valori IMPORTO non validi (mantieni quelle con date mancanti)
                df = df.dropna(subset=['IMPORTO'])

                # Calcola gli aggregati dei dati temporanei
                total_gains_temp = df[df['IMPORTO'] > 0]['IMPORTO'].sum()
                total_expenses_temp = abs(df[df['IMPORTO'] < 0]['IMPORTO'].sum())
                profit_temp = total_gains_temp - total_expenses_temp

                # Calcola il periodo di analisi temporaneo (usa solo date valide)
                valid_dates_temp = df['DATA_PARSED'].dropna()
                if len(valid_dates_temp) > 0:
                    min_date_temp = valid_dates_temp.min()
                    max_date_temp = valid_dates_temp.max()
                    periodo_temp = f"{min_date_temp.strftime('%d/%m/%Y')} - {max_date_temp.strftime('%d/%m/%Y')}"
                else:
                    periodo_temp = "Date non disponibili"

                # Carica e calcola i dati storici
                historical_data = self.db_manager.load_all_transactions()
                
                if historical_data:
                    df_hist = pd.DataFrame(historical_data)
                    df_hist['IMPORTO'] = pd.to_numeric(df_hist['IMPORTO'], errors='coerce')
                    df_hist['DATA_PARSED'] = pd.to_datetime(df_hist['DATA'], dayfirst=True, errors='coerce')
                    df_hist = df_hist.dropna(subset=['IMPORTO'])
                    
                    total_gains_hist = df_hist[df_hist['IMPORTO'] > 0]['IMPORTO'].sum()
                    total_expenses_hist = abs(df_hist[df_hist['IMPORTO'] < 0]['IMPORTO'].sum())
                    profit_hist = total_gains_hist - total_expenses_hist
                    
                    valid_dates_hist = df_hist['DATA_PARSED'].dropna()
                    if len(valid_dates_hist) > 0:
                        min_date_hist = valid_dates_hist.min()
                        max_date_hist = valid_dates_hist.max()
                        periodo_hist = f"{min_date_hist.strftime('%d/%m/%Y')} - {max_date_hist.strftime('%d/%m/%Y')}"
                    else:
                        periodo_hist = "Date non disponibili"
                else:
                    total_gains_hist = total_expenses_hist = profit_hist = 0
                    periodo_hist = "Nessun dato storico"

                # Crea il foglio "Risultati" con entrambe le tabelle
                risultati_data = [
                    ['DATI TEMPORANEI', '', '', ''],
                    ['PERIODO', 'TOTALE ENTRATE', 'TOTALE USCITE', 'PROFITTO'],
                    [periodo_temp, f"{total_gains_temp:,.2f}", f"{total_expenses_temp:,.2f}", f"{profit_temp:,.2f}"],
                    ['', '', '', ''],  # Riga vuota
                    ['DATI STORICI', '', '', ''],
                    ['PERIODO', 'TOTALE ENTRATE', 'TOTALE USCITE', 'PROFITTO'],
                    [periodo_hist, f"{total_gains_hist:,.2f}", f"{total_expenses_hist:,.2f}", f"{profit_hist:,.2f}"]
                ]
                risultati_df = pd.DataFrame(risultati_data)

                # Prepara il foglio "Transazioni" con tutti i dati temporanei
                transazioni_df = df.copy()
                
                # Formatta le date temporanee: usa DATA_PARSED se disponibile
                def format_temp_date(row):
                    if pd.notna(row['DATA_PARSED']):
                        return row['DATA_PARSED'].strftime('%d-%m-%Y')
                    else:
                        # Se la data non è parsabile, prova a mantenerla o segnala problema
                        original_date = str(row['DATA']) if pd.notna(row['DATA']) else ''
                        if original_date.strip() == '' or original_date.lower() == 'nan':
                            return "Data non disponibile"
                        else:
                            return f"Data non valida: {original_date}"
                
                transazioni_df['DATA'] = transazioni_df.apply(format_temp_date, axis=1)
                transazioni_df['IMPORTO'] = transazioni_df['IMPORTO'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "0.00")
                
                # Rimuovi colonne temporanee
                if 'DATA_PARSED' in transazioni_df.columns:
                    transazioni_df = transazioni_df.drop('DATA_PARSED', axis=1)
                if '_IMPORT_TIMESTAMP' in transazioni_df.columns:
                    transazioni_df = transazioni_df.drop('_IMPORT_TIMESTAMP', axis=1)
                
                # Riordina le colonne
                colonne_ordinate = ["DATA", "SORGENTE", "PRODOTTO", "FORNITORE", "CATEGORIA", "QUANTITA'", "IMPORTO"]
                transazioni_df = transazioni_df[colonne_ordinate]

                # Prepara il foglio "Transazioni Storiche"
                if historical_data:
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
                    
                    transazioni_storiche_df = transazioni_storiche_df[colonne_ordinate]
                else:
                    # Crea un DataFrame vuoto con le colonne corrette
                    transazioni_storiche_df = pd.DataFrame(columns=colonne_ordinate)

                # Esporta in Excel con tre fogli
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Foglio "Risultati" con gli aggregati
                    risultati_df.to_excel(writer, index=False, sheet_name='Risultati', header=False)
                    
                    # Foglio "Transazioni" con tutti i dati temporanei
                    transazioni_df.to_excel(writer, index=False, sheet_name='Transazioni')
                    
                    # Foglio "Transazioni Storiche" con tutti i dati storici
                    transazioni_storiche_df.to_excel(writer, index=False, sheet_name='Transazioni Storiche')

                QMessageBox.information(
                    self, 
                    "Esportazione completata", 
                    f"File salvato con successo in:\n{file_path}\n\nIl file contiene:\n• Foglio 'Risultati': aggregati temporanei e storici\n• Foglio 'Transazioni': dettaglio dati temporanei\n• Foglio 'Transazioni Storiche': dettaglio dati storici"
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