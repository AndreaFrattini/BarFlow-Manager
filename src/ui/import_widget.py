"""
Widget per l'importazione dei dati da file Excel e XML
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QFileDialog, QTableWidget, QTableWidgetItem, QComboBox,
                              QFrame, QProgressBar, QTextEdit, QSplitter, QGroupBox,
                              QFormLayout, QLineEdit, QCheckBox, QMessageBox, QDialog,
                              QDialogButtonBox, QListWidget, QStackedWidget, QTabWidget,
                              QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon
import sys
import os
from pathlib import Path

# Importa i parser
sys.path.append(str(Path(__file__).parent.parent))
from parsers.file_parser import ExcelParser, XMLParser
from utils.common_utils import FileUtils, ValidationUtils, MessageUtils


class ImportPreviewDialog(QDialog):
    """Dialog per l'anteprima e mapping dei dati"""
    
    def __init__(self, parser, db_manager, parent=None):
        super().__init__(parent)
        self.parser = parser
        self.db_manager = db_manager
        self.preview_data = None
        self.mapping = {}
        self.init_ui()
        self.load_preview()
    
    def init_ui(self):
        """Inizializza l'interfaccia del dialog"""
        self.setWindowTitle("Anteprima e Mapping Dati")
        self.setModal(True)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Tab widget per le diverse sezioni
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Tab 1: Anteprima dati
        self.create_preview_tab(tab_widget)
        
        # Tab 2: Mapping campi
        self.create_mapping_tab(tab_widget)
        
        # Tab 3: Configurazione import
        self.create_config_tab(tab_widget)
        
        # Pulsanti
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_preview_tab(self, parent):
        """Crea il tab di anteprima"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # Info file
        info_group = QGroupBox("Informazioni File")
        info_layout = QFormLayout(info_group)
        
        self.file_info_label = QLabel()
        info_layout.addRow("File:", self.file_info_label)
        
        self.file_size_label = QLabel()
        info_layout.addRow("Dimensione:", self.file_size_label)
        
        self.rows_count_label = QLabel()
        info_layout.addRow("Righe rilevate:", self.rows_count_label)
        
        layout.addWidget(info_group)
        
        # Anteprima dati
        preview_group = QGroupBox("Anteprima Dati (Prime 10 righe)")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        parent.addTab(preview_widget, "📋 Anteprima")
    
    def create_mapping_tab(self, parent):
        """Crea il tab di mapping"""
        mapping_widget = QWidget()
        layout = QVBoxLayout(mapping_widget)
        
        # Istruzioni
        instructions = QLabel("""
        <b>Mappatura Campi:</b><br>
        Seleziona come mappare le colonne del file ai campi del database.<br>
        I campi marcati con * sono obbligatori.
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #E8F4FD; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Form mapping
        mapping_group = QGroupBox("Mappatura Campi")
        mapping_layout = QFormLayout(mapping_group)
        
        # Campo data (obbligatorio)
        self.date_mapping = QComboBox()
        mapping_layout.addRow("Data Transazione *:", self.date_mapping)
        
        # Campo descrizione (obbligatorio)
        self.description_mapping = QComboBox()
        mapping_layout.addRow("Descrizione *:", self.description_mapping)
        
        # Campo importo (obbligatorio)
        self.amount_mapping = QComboBox()
        mapping_layout.addRow("Importo *:", self.amount_mapping)
        
        # Campo tipo entrata/uscita (opzionale)
        self.type_mapping = QComboBox()
        mapping_layout.addRow("Indicatore Tipo:", self.type_mapping)
        
        layout.addWidget(mapping_group)
        
        # Suggerimenti automatici
        suggestions_group = QGroupBox("Suggerimenti Automatici")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        auto_btn = QPushButton("🤖 Rileva Automaticamente")
        auto_btn.clicked.connect(self.auto_detect_mapping)
        auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        suggestions_layout.addWidget(auto_btn)
        
        layout.addWidget(suggestions_group)
        
        layout.addStretch()
        
        parent.addTab(mapping_widget, "🔗 Mapping")
    
    def create_config_tab(self, parent):
        """Crea il tab di configurazione"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Categoria default
        category_group = QGroupBox("Configurazione Import")
        category_layout = QFormLayout(category_group)
        
        self.default_category = QComboBox()
        self.load_categories()
        category_layout.addRow("Categoria Default:", self.default_category)
        
        # Gestione duplicati
        self.duplicate_handling = QComboBox()
        self.duplicate_handling.addItems(["Chiedi all'utente", "Salta duplicati", "Aggiorna esistenti", "Crea duplicati"])
        category_layout.addRow("Gestione Duplicati:", self.duplicate_handling)
        
        # Granularità dati
        self.granularity_combo = QComboBox()
        self.granularity_combo.addItems(["Rilevamento automatico", "Giornaliera", "Settimanale", "Mensile"])
        category_layout.addRow("Granularità Dati:", self.granularity_combo)
        
        layout.addWidget(category_group)
        
        # Salva profilo
        profile_group = QGroupBox("Salva Profilo Import")
        profile_layout = QVBoxLayout(profile_group)
        
        self.save_profile_checkbox = QCheckBox("Salva questo mapping come profilo riutilizzabile")
        self.save_profile_checkbox.setChecked(True)
        profile_layout.addWidget(self.save_profile_checkbox)
        
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setPlaceholderText("Nome del profilo (es. 'POS Restaurant', 'Fatture Fornitori')")
        profile_layout.addWidget(self.profile_name_edit)
        
        layout.addWidget(profile_group)
        
        layout.addStretch()
        
        parent.addTab(config_widget, "⚙️ Configurazione")
    
    def load_preview(self):
        """Carica l'anteprima dei dati"""
        try:
            if isinstance(self.parser, ExcelParser):
                # Carica il primo foglio
                sheets = self.parser.get_sheets()
                if sheets:
                    self.parser.load_sheet(sheets[0])
                    self.preview_data = self.parser.get_preview_data()
                    
                    # Aggiorna info file
                    self.file_info_label.setText(f"{os.path.basename(self.parser.file_path)} (Foglio: {sheets[0]})")
                    self.file_size_label.setText(FileUtils.get_file_size(self.parser.file_path))
                    self.rows_count_label.setText(str(self.preview_data['total_rows']))
                    
                    # Popola tabella anteprima
                    self.populate_preview_table()
                    
                    # Popola combo mapping
                    self.populate_mapping_combos()
                    
                    # Suggerimento automatico nome profilo
                    base_name = os.path.splitext(os.path.basename(self.parser.file_path))[0]
                    self.profile_name_edit.setText(f"Profilo {base_name}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento anteprima: {e}")
    
    def populate_preview_table(self):
        """Popola la tabella di anteprima"""
        if not self.preview_data:
            return
        
        columns = self.preview_data['columns']
        data = self.preview_data['data']
        
        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        self.preview_table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            for col, column_name in enumerate(columns):
                value = record.get(column_name, '')
                item = QTableWidgetItem(str(value))
                self.preview_table.setItem(row, col, item)
        
        # Ridimensiona colonne
        self.preview_table.resizeColumnsToContents()
    
    def populate_mapping_combos(self):
        """Popola le combo box del mapping"""
        if not self.preview_data:
            return
        
        columns = ['-- Non mappato --'] + self.preview_data['columns']
        
        # Popola tutte le combo
        for combo in [self.date_mapping, self.description_mapping, 
                     self.amount_mapping, self.type_mapping]:
            combo.clear()
            combo.addItems(columns)
    
    def load_categories(self):
        """Carica le categorie disponibili"""
        try:
            categories = self.db_manager.get_categories()
            
            for category in categories:
                self.default_category.addItem(category['name'], category['category_id'])
                
        except Exception as e:
            print(f"Errore nel caricamento categorie: {e}")
    
    def auto_detect_mapping(self):
        """Rileva automaticamente il mapping"""
        if not isinstance(self.parser, ExcelParser):
            return
        
        try:
            suggestions = self.parser.suggest_column_mapping()
            
            # Applica i suggerimenti
            for field, column in suggestions.items():
                if field == 'transaction_date':
                    self.set_combo_value(self.date_mapping, column)
                elif field == 'description':
                    self.set_combo_value(self.description_mapping, column)
                elif field == 'amount':
                    self.set_combo_value(self.amount_mapping, column)
                elif field in ['is_income_indicator', 'is_expense_indicator']:
                    self.set_combo_value(self.type_mapping, column)
            
            QMessageBox.information(
                self,
                "Rilevamento Completato",
                f"Rilevati {len(suggestions)} suggerimenti di mapping.\n"
                "Verifica che siano corretti prima di procedere."
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore nel rilevamento automatico: {e}")
    
    def set_combo_value(self, combo, value):
        """Imposta il valore di una combo box"""
        for i in range(combo.count()):
            if combo.itemText(i) == value:
                combo.setCurrentIndex(i)
                break
    
    def get_mapping(self):
        """Ottiene la mappatura configurata"""
        mapping = {}
        
        if self.date_mapping.currentIndex() > 0:
            mapping['transaction_date'] = self.date_mapping.currentText()
        
        if self.description_mapping.currentIndex() > 0:
            mapping['description'] = self.description_mapping.currentText()
        
        if self.amount_mapping.currentIndex() > 0:
            mapping['amount'] = self.amount_mapping.currentText()
        
        if self.type_mapping.currentIndex() > 0:
            mapping['is_income_indicator'] = self.type_mapping.currentText()
        
        return mapping
    
    def get_config(self):
        """Ottiene la configurazione dell'import"""
        return {
            'default_category_id': self.default_category.currentData(),
            'duplicate_handling': self.duplicate_handling.currentText(),
            'granularity': self.granularity_combo.currentText(),
            'save_profile': self.save_profile_checkbox.isChecked(),
            'profile_name': self.profile_name_edit.text().strip()
        }
    
    def validate_mapping(self):
        """Valida la mappatura"""
        mapping = self.get_mapping()
        
        # Verifica campi obbligatori
        required_fields = ['transaction_date', 'description', 'amount']
        missing_fields = []
        
        for field in required_fields:
            if field not in mapping:
                missing_fields.append(field)
        
        if missing_fields:
            QMessageBox.warning(
                self,
                "Mapping Incompleto",
                f"I seguenti campi obbligatori non sono mappati:\n"
                f"• {', '.join(missing_fields)}\n\n"
                "Completa il mapping prima di procedere."
            )
            return False
        
        return True
    
    def accept(self):
        """Override accept per validazione"""
        if not self.validate_mapping():
            return
        
        super().accept()


class ImportWorker(QThread):
    """Thread per l'importazione dei dati"""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    import_completed = Signal(int)  # numero transazioni importate
    import_failed = Signal(str)     # messaggio errore
    
    def __init__(self, parser, mapping, config, db_manager):
        super().__init__()
        self.parser = parser
        self.mapping = mapping
        self.config = config
        self.db_manager = db_manager
    
    def run(self):
        """Esegue l'importazione"""
        try:
            self.status_updated.emit("Verifica file già importato...")
            self.progress_updated.emit(10)
            
            # Verifica se il file è già stato importato
            existing_source = self.db_manager.check_file_already_imported(self.parser.file_hash)
            
            if existing_source:
                duplicate_handling = self.config['duplicate_handling']
                
                if duplicate_handling == "Salta duplicati":
                    self.import_failed.emit("File già importato precedentemente")
                    return
                elif duplicate_handling == "Chiedi all'utente":
                    # Segnala che serve interazione utente
                    self.import_failed.emit("DUPLICATE_NEEDS_USER_CHOICE")
                    return
            
            self.status_updated.emit("Parsing dati...")
            self.progress_updated.emit(30)
            
            # Parse dei dati
            default_category_id = self.config['default_category_id']
            transactions = self.parser.parse_with_mapping(self.mapping, default_category_id)
            
            if not transactions:
                self.import_failed.emit("Nessuna transazione valida trovata nel file")
                return
            
            self.status_updated.emit("Rilevamento granularità...")
            self.progress_updated.emit(50)
            
            # Rileva granularità se automatico
            granularity = self.config['granularity']
            if granularity == "Rilevamento automatico":
                if hasattr(self.parser, 'detect_granularity'):
                    granularity = self.parser.detect_granularity()
                else:
                    granularity = 'monthly'  # default
            
            self.status_updated.emit("Verifica coerenza dati...")
            self.progress_updated.emit(70)
            
            # Verifica coerenza granularità
            is_consistent, existing_granularities = self.db_manager.check_data_granularity_consistency()
            
            if existing_granularities and granularity.lower() not in [g.lower() for g in existing_granularities]:
                self.import_failed.emit(
                    f"Granularità non coerente. Esistente: {', '.join(existing_granularities)}, "
                    f"Nuovo file: {granularity}"
                )
                return
            
            self.status_updated.emit("Registrazione file importato...")
            self.progress_updated.emit(80)
            
            # Registra il file importato
            filename = os.path.basename(self.parser.file_path)
            source_id = self.db_manager.add_imported_source(
                filename,
                self.parser.file_hash,
                granularity=granularity
            )
            
            # Aggiungi source_id alle transazioni
            for transaction in transactions:
                transaction['source_id'] = source_id
            
            self.status_updated.emit("Importazione transazioni...")
            self.progress_updated.emit(90)
            
            # Importa le transazioni
            count = self.db_manager.add_transactions(transactions)
            
            self.status_updated.emit("Completato!")
            self.progress_updated.emit(100)
            
            self.import_completed.emit(count)
            
        except Exception as e:
            self.import_failed.emit(str(e))


class ImportWidget(QWidget):
    """Widget principale per l'importazione dati"""
    
    # Segnale emesso quando i dati sono importati
    data_imported = Signal(int)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_parser = None
        self.import_worker = None
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header con istruzioni
        self.create_header(layout)
        
        # Selezione file
        self.create_file_selection(layout)
        
        # Area di stato e progresso
        self.create_status_area(layout)
        
        # Profili salvati
        self.create_profiles_section(layout)
    
    def create_header(self, parent_layout):
        """Crea l'header con istruzioni"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #3498DB, stop:1 #2980B9);
                border-radius: 10px;
                color: white;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🚀 Importazione Dati")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        instructions = QLabel("""
        Importa i tuoi dati finanziari da file Excel o XML.<br>
        Il sistema supporta il rilevamento automatico del formato e la mappatura intelligente dei campi.<br>
        <b>Formati supportati:</b> .xlsx, .xls, .xml
        """)
        instructions.setStyleSheet("color: white; font-size: 14px; line-height: 1.4;")
        instructions.setWordWrap(True)
        header_layout.addWidget(instructions)
        
        parent_layout.addWidget(header_frame)
    
    def create_file_selection(self, parent_layout):
        """Crea la sezione di selezione file"""
        file_frame = QFrame()
        file_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px dashed #BDC3C7;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        
        file_layout = QVBoxLayout(file_frame)
        file_layout.setAlignment(Qt.AlignCenter)
        
        # Icona e testo
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 20px;")
        file_layout.addWidget(icon_label)
        
        info_label = QLabel("Seleziona un file da importare")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 18px; color: #7F8C8D; margin-bottom: 20px;")
        file_layout.addWidget(info_label)
        
        # Pulsante selezione file
        self.select_file_btn = QPushButton("📂 Scegli File")
        self.select_file_btn.clicked.connect(self.select_file)
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        file_layout.addWidget(self.select_file_btn)
        
        # Info file selezionato
        self.file_info_label = QLabel("")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("color: #27AE60; font-weight: bold; margin-top: 10px;")
        file_layout.addWidget(self.file_info_label)
        
        # Pulsante preview (nascosto inizialmente)
        self.preview_btn = QPushButton("👁️ Anteprima e Import")
        self.preview_btn.clicked.connect(self.show_preview)
        self.preview_btn.setVisible(False)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        file_layout.addWidget(self.preview_btn)
        
        parent_layout.addWidget(file_frame)
    
    def create_status_area(self, parent_layout):
        """Crea l'area di stato e progresso"""
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
        
        # Label stato
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        status_layout.addWidget(self.status_label)
        
        # Barra di progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # Log dettagliato
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        status_layout.addWidget(self.log_text)
        
        parent_layout.addWidget(self.status_frame)
    
    def create_profiles_section(self, parent_layout):
        """Crea la sezione dei profili salvati"""
        profiles_frame = QFrame()
        profiles_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        profiles_layout = QVBoxLayout(profiles_frame)
        
        # Titolo
        title = QLabel("📋 Profili di Importazione Salvati")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        profiles_layout.addWidget(title)
        
        # Lista profili
        self.profiles_list = QListWidget()
        self.profiles_list.setMaximumHeight(150)
        self.load_saved_profiles()
        profiles_layout.addWidget(self.profiles_list)
        
        # Pulsanti profili
        profiles_buttons = QHBoxLayout()
        
        refresh_profiles_btn = QPushButton("🔄 Aggiorna")
        refresh_profiles_btn.clicked.connect(self.load_saved_profiles)
        profiles_buttons.addWidget(refresh_profiles_btn)
        
        profiles_buttons.addStretch()
        
        delete_profile_btn = QPushButton("🗑️ Elimina Selezionato")
        delete_profile_btn.clicked.connect(self.delete_selected_profile)
        profiles_buttons.addWidget(delete_profile_btn)
        
        profiles_layout.addLayout(profiles_buttons)
        
        parent_layout.addWidget(profiles_frame)
    
    def select_file(self):
        """Apre il dialog di selezione file"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("File supportati (*.xlsx *.xls *.xml);;Excel Files (*.xlsx *.xls);;XML Files (*.xml)")
        
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Carica e analizza il file selezionato"""
        try:
            # Verifica accessibilità file
            if not FileUtils.is_file_accessible(file_path):
                QMessageBox.critical(self, "Errore", f"Impossibile accedere al file:\n{file_path}")
                return
            
            # Determina il tipo di parser
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                self.current_parser = ExcelParser(file_path)
            elif file_ext == '.xml':
                self.current_parser = XMLParser(file_path)
            else:
                QMessageBox.critical(self, "Errore", f"Formato file non supportato: {file_ext}")
                return
            
            # Aggiorna UI
            filename = os.path.basename(file_path)
            file_size = FileUtils.format_file_size(FileUtils.get_file_size(file_path))
            
            self.file_info_label.setText(f"✅ {filename} ({file_size})")
            self.preview_btn.setVisible(True)
            
            # Mostra area stato
            self.status_frame.setVisible(True)
            self.status_label.setText(f"File caricato: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento del file:\n{str(e)}")
    
    def show_preview(self):
        """Mostra il dialog di anteprima e mapping"""
        if not self.current_parser:
            QMessageBox.warning(self, "Avviso", "Nessun file selezionato")
            return
        
        try:
            preview_dialog = ImportPreviewDialog(self.current_parser, self.db_manager, self)
            
            if preview_dialog.exec() == QDialog.Accepted:
                mapping = preview_dialog.get_mapping()
                config = preview_dialog.get_config()
                
                self.start_import(mapping, config)
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'anteprima:\n{str(e)}")
    
    def start_import(self, mapping, config):
        """Avvia l'importazione in background"""
        if self.import_worker and self.import_worker.isRunning():
            QMessageBox.warning(self, "Avviso", "Un'importazione è già in corso")
            return
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.setVisible(True)
        self.log_text.clear()
        
        # Disabilita controlli
        self.select_file_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        
        # Avvia worker
        self.import_worker = ImportWorker(self.current_parser, mapping, config, self.db_manager)
        self.import_worker.progress_updated.connect(self.progress_bar.setValue)
        self.import_worker.status_updated.connect(self.update_status)
        self.import_worker.import_completed.connect(self.on_import_completed)
        self.import_worker.import_failed.connect(self.on_import_failed)
        self.import_worker.start()
    
    def update_status(self, message):
        """Aggiorna il messaggio di stato"""
        self.status_label.setText(message)
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def on_import_completed(self, count):
        """Gestisce il completamento dell'importazione"""
        self.progress_bar.setVisible(False)
        self.select_file_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        
        # Messaggio di successo
        QMessageBox.information(
            self,
            "Importazione Completata",
            f"✅ Importazione completata con successo!\n\n"
            f"Transazioni importate: {count}\n"
            f"File: {os.path.basename(self.current_parser.file_path)}"
        )
        
        # Reset UI
        self.reset_ui()
        
        # Aggiorna profili
        self.load_saved_profiles()
        
        # Emetti segnale
        self.data_imported.emit(count)
    
    def on_import_failed(self, error_message):
        """Gestisce l'errore nell'importazione"""
        self.progress_bar.setVisible(False)
        self.select_file_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        
        if error_message == "DUPLICATE_NEEDS_USER_CHOICE":
            # Gestione speciale per duplicati
            reply = QMessageBox.question(
                self,
                "File Duplicato",
                "Questo file è già stato importato.\n\n"
                "Cosa vuoi fare?",
                QMessageBox.Retry | QMessageBox.Ignore | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Retry:
                # L'utente può modificare la configurazione
                self.show_preview()
            
        else:
            QMessageBox.critical(
                self,
                "Errore Importazione",
                f"❌ Errore durante l'importazione:\n\n{error_message}"
            )
    
    def reset_ui(self):
        """Reset dell'interfaccia utente"""
        self.file_info_label.setText("")
        self.preview_btn.setVisible(False)
        self.status_frame.setVisible(False)
        self.log_text.setVisible(False)
        self.current_parser = None
    
    def load_saved_profiles(self):
        """Carica i profili salvati"""
        self.profiles_list.clear()
        
        try:
            profiles = self.db_manager.get_source_profiles()
            
            for profile in profiles:
                item_text = f"{profile['name']} ({profile['file_type'].upper()})"
                self.profiles_list.addItem(item_text)
                
        except Exception as e:
            print(f"Errore nel caricamento profili: {e}")
    
    def delete_selected_profile(self):
        """Elimina il profilo selezionato"""
        current_item = self.profiles_list.currentItem()
        
        if not current_item:
            QMessageBox.information(self, "Info", "Seleziona un profilo da eliminare")
            return
        
        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare il profilo:\n{current_item.text()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Implementare eliminazione profilo nel database
            QMessageBox.information(self, "Info", "Funzione eliminazione profilo da implementare")
            self.load_saved_profiles()