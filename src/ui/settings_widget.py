"""
Widget per le impostazioni dell'applicazione
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QLineEdit, QComboBox, QCheckBox, QSpinBox, QGroupBox,
                              QFormLayout, QFileDialog, QMessageBox, QTextEdit,
                              QTabWidget, QFrame, QScrollArea, QSlider, QProgressBar)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
import os
import json
import shutil
from pathlib import Path


class SettingsWidget(QWidget):
    """Widget per le impostazioni dell'applicazione"""
    
    # Segnale emesso quando le impostazioni cambiano
    settings_changed = Signal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header
        self.create_header(layout)
        
        # Tab widget per diverse categorie di impostazioni
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Tab 1: Generale
        self.create_general_tab(tab_widget)
        
        # Tab 2: Database
        self.create_database_tab(tab_widget)
        
        # Tab 3: Import/Export
        self.create_import_export_tab(tab_widget)
        
        # Tab 4: Interfaccia
        self.create_interface_tab(tab_widget)
        
        # Tab 5: Avanzate
        self.create_advanced_tab(tab_widget)
        
        # Pulsanti di controllo
        self.create_control_buttons(layout)
    
    def create_header(self, parent_layout):
        """Crea l'header del widget"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #34495E, stop:1 #2C3E50);
                border-radius: 10px;
                color: white;
                padding: 20px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("⚙️ Impostazioni")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Personalizza il comportamento e l'aspetto di BarFlow")
        subtitle.setStyleSheet("color: white; font-size: 14px;")
        header_layout.addWidget(subtitle)
        
        parent_layout.addWidget(header_frame)
    
    def create_general_tab(self, parent):
        """Crea il tab delle impostazioni generali"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Impostazioni di base
        basic_group = QGroupBox("Impostazioni Base")
        basic_layout = QFormLayout(basic_group)
        
        # Valuta
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["EUR", "USD", "GBP", "CHF"])
        basic_layout.addRow("Valuta predefinita:", self.currency_combo)
        
        # Formato data
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        basic_layout.addRow("Formato data:", self.date_format_combo)
        
        # Separatori numerici
        self.decimal_separator_combo = QComboBox()
        self.decimal_separator_combo.addItems([",", "."])
        basic_layout.addRow("Separatore decimale:", self.decimal_separator_combo)
        
        self.thousands_separator_combo = QComboBox()
        self.thousands_separator_combo.addItems([".", ",", " "])
        basic_layout.addRow("Separatore migliaia:", self.thousands_separator_combo)
        
        layout.addWidget(basic_group)
        
        # Comportamento applicazione
        behavior_group = QGroupBox("Comportamento Applicazione")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.auto_refresh_check = QCheckBox("Aggiorna automaticamente la dashboard")
        self.auto_refresh_check.setChecked(True)
        behavior_layout.addWidget(self.auto_refresh_check)
        
        self.confirm_delete_check = QCheckBox("Conferma prima di eliminare transazioni")
        self.confirm_delete_check.setChecked(True)
        behavior_layout.addWidget(self.confirm_delete_check)
        
        self.remember_window_size_check = QCheckBox("Ricorda dimensioni finestra")
        self.remember_window_size_check.setChecked(True)
        behavior_layout.addWidget(self.remember_window_size_check)
        
        layout.addWidget(behavior_group)
        
        # Periodo predefinito
        period_group = QGroupBox("Periodo Predefinito per Report")
        period_layout = QFormLayout(period_group)
        
        self.default_period_combo = QComboBox()
        self.default_period_combo.addItems([
            "Ultimo mese chiuso",
            "Ultimi 3 mesi",
            "Ultimi 6 mesi",
            "Anno corrente"
        ])
        period_layout.addRow("Periodo predefinito:", self.default_period_combo)
        
        layout.addWidget(period_group)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "🏠 Generale")
    
    def create_database_tab(self, parent):
        """Crea il tab delle impostazioni database"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Percorso database
        db_path_group = QGroupBox("Percorso Database")
        db_path_layout = QVBoxLayout(db_path_group)
        
        # Info corrente
        self.current_db_label = QLabel()
        self.current_db_label.setStyleSheet("color: #2C3E50; font-weight: bold; padding: 10px; background-color: #ECF0F1; border-radius: 5px;")
        db_path_layout.addWidget(self.current_db_label)
        
        # Pulsanti gestione database
        db_buttons_layout = QHBoxLayout()
        
        backup_btn = QPushButton("💾 Crea Backup")
        backup_btn.clicked.connect(self.create_database_backup)
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        db_buttons_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📥 Ripristina Backup")
        restore_btn.clicked.connect(self.restore_database_backup)
        db_buttons_layout.addWidget(restore_btn)
        
        db_buttons_layout.addStretch()
        
        change_location_btn = QPushButton("📁 Cambia Posizione")
        change_location_btn.clicked.connect(self.change_database_location)
        db_buttons_layout.addWidget(change_location_btn)
        
        db_path_layout.addLayout(db_buttons_layout)
        layout.addWidget(db_path_group)
        
        # Backup automatico
        backup_group = QGroupBox("Backup Automatico")
        backup_layout = QFormLayout(backup_group)
        
        self.auto_backup_check = QCheckBox("Abilita backup automatico")
        self.auto_backup_check.setChecked(True)
        backup_layout.addRow("Backup automatico:", self.auto_backup_check)
        
        self.backup_frequency_combo = QComboBox()
        self.backup_frequency_combo.addItems(["Giornaliero", "Settimanale", "Mensile"])
        self.backup_frequency_combo.setCurrentText("Settimanale")
        backup_layout.addRow("Frequenza:", self.backup_frequency_combo)
        
        self.backup_retention_spinbox = QSpinBox()
        self.backup_retention_spinbox.setRange(1, 30)
        self.backup_retention_spinbox.setValue(5)
        self.backup_retention_spinbox.setSuffix(" backup")
        backup_layout.addRow("Mantieni:", self.backup_retention_spinbox)
        
        layout.addWidget(backup_group)
        
        # Statistiche database
        stats_group = QGroupBox("Statistiche Database")
        stats_layout = QVBoxLayout(stats_group)
        
        self.db_stats_label = QLabel()
        self.db_stats_label.setStyleSheet("color: #2C3E50; padding: 10px;")
        stats_layout.addWidget(self.db_stats_label)
        
        refresh_stats_btn = QPushButton("🔄 Aggiorna Statistiche")
        refresh_stats_btn.clicked.connect(self.refresh_database_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "🗄️ Database")
    
    def create_import_export_tab(self, parent):
        """Crea il tab delle impostazioni import/export"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Impostazioni import
        import_group = QGroupBox("Impostazioni Import")
        import_layout = QFormLayout(import_group)
        
        # Granularità predefinita
        self.default_granularity_combo = QComboBox()
        self.default_granularity_combo.addItems(["Rilevamento automatico", "Giornaliera", "Settimanale", "Mensile"])
        import_layout.addRow("Granularità predefinita:", self.default_granularity_combo)
        
        # Gestione duplicati
        self.duplicate_handling_combo = QComboBox()
        self.duplicate_handling_combo.addItems(["Chiedi all'utente", "Salta duplicati", "Aggiorna esistenti", "Crea duplicati"])
        import_layout.addRow("Gestione duplicati:", self.duplicate_handling_combo)
        
        # Validazione dati
        self.validate_dates_check = QCheckBox("Valida date durante import")
        self.validate_dates_check.setChecked(True)
        import_layout.addRow("Validazione:", self.validate_dates_check)
        
        self.validate_amounts_check = QCheckBox("Valida importi durante import")
        self.validate_amounts_check.setChecked(True)
        import_layout.addRow("", self.validate_amounts_check)
        
        layout.addWidget(import_group)
        
        # Impostazioni export
        export_group = QGroupBox("Impostazioni Export")
        export_layout = QFormLayout(export_group)
        
        # Formato export
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"])
        export_layout.addRow("Formato predefinito:", self.export_format_combo)
        
        # Includi dati per default
        self.include_transactions_default_check = QCheckBox("Includi sempre dettaglio transazioni")
        self.include_transactions_default_check.setChecked(True)
        export_layout.addRow("Dettagli:", self.include_transactions_default_check)
        
        self.include_charts_default_check = QCheckBox("Includi grafici nei report")
        self.include_charts_default_check.setChecked(True)
        export_layout.addRow("", self.include_charts_default_check)
        
        # Cartella export
        export_folder_layout = QHBoxLayout()
        
        self.export_folder_edit = QLineEdit()
        self.export_folder_edit.setReadOnly(True)
        export_folder_layout.addWidget(self.export_folder_edit)
        
        browse_export_btn = QPushButton("📁")
        browse_export_btn.clicked.connect(self.browse_export_folder)
        browse_export_btn.setFixedWidth(40)
        export_folder_layout.addWidget(browse_export_btn)
        
        export_layout.addRow("Cartella export:", export_folder_layout)
        
        layout.addWidget(export_group)
        
        # Pulizia file temporanei
        cleanup_group = QGroupBox("Pulizia File Temporanei")
        cleanup_layout = QVBoxLayout(cleanup_group)
        
        self.auto_cleanup_check = QCheckBox("Rimuovi automaticamente file temporanei dopo 7 giorni")
        self.auto_cleanup_check.setChecked(True)
        cleanup_layout.addWidget(self.auto_cleanup_check)
        
        cleanup_now_btn = QPushButton("🧹 Pulisci Ora")
        cleanup_now_btn.clicked.connect(self.cleanup_temp_files)
        cleanup_layout.addWidget(cleanup_now_btn)
        
        layout.addWidget(cleanup_group)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "📁 Import/Export")
    
    def create_interface_tab(self, parent):
        """Crea il tab delle impostazioni interfaccia"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Tema
        theme_group = QGroupBox("Aspetto")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Chiaro", "Scuro", "Automatico (sistema)"])
        theme_layout.addRow("Tema:", self.theme_combo)
        
        # Dimensioni font
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(8, 16)
        self.font_size_slider.setValue(10)
        self.font_size_slider.valueChanged.connect(self.update_font_size_label)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(self.font_size_slider)
        self.font_size_label = QLabel("10px")
        font_layout.addWidget(self.font_size_label)
        
        theme_layout.addRow("Dimensione font:", font_layout)
        
        layout.addWidget(theme_group)
        
        # Dashboard
        dashboard_group = QGroupBox("Dashboard")
        dashboard_layout = QVBoxLayout(dashboard_group)
        
        self.show_animations_check = QCheckBox("Mostra animazioni nei grafici")
        self.show_animations_check.setChecked(True)
        dashboard_layout.addWidget(self.show_animations_check)
        
        self.auto_refresh_dashboard_check = QCheckBox("Aggiorna automaticamente ogni 5 minuti")
        self.auto_refresh_dashboard_check.setChecked(True)
        dashboard_layout.addWidget(self.auto_refresh_dashboard_check)
        
        self.compact_view_check = QCheckBox("Usa vista compatta")
        dashboard_layout.addWidget(self.compact_view_check)
        
        layout.addWidget(dashboard_group)
        
        # Notifiche
        notifications_group = QGroupBox("Notifiche")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.show_success_notifications_check = QCheckBox("Mostra notifiche di successo")
        self.show_success_notifications_check.setChecked(True)
        notifications_layout.addWidget(self.show_success_notifications_check)
        
        self.show_warning_notifications_check = QCheckBox("Mostra avvisi")
        self.show_warning_notifications_check.setChecked(True)
        notifications_layout.addWidget(self.show_warning_notifications_check)
        
        self.notification_duration_spinbox = QSpinBox()
        self.notification_duration_spinbox.setRange(1, 10)
        self.notification_duration_spinbox.setValue(3)
        self.notification_duration_spinbox.setSuffix(" secondi")
        
        notification_duration_layout = QFormLayout()
        notification_duration_layout.addRow("Durata notifiche:", self.notification_duration_spinbox)
        notifications_layout.addLayout(notification_duration_layout)
        
        layout.addWidget(notifications_group)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "🎨 Interfaccia")
    
    def create_advanced_tab(self, parent):
        """Crea il tab delle impostazioni avanzate"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setSpacing(15)
        
        # Performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.max_transactions_display_spinbox = QSpinBox()
        self.max_transactions_display_spinbox.setRange(100, 10000)
        self.max_transactions_display_spinbox.setValue(1000)
        performance_layout.addRow("Max transazioni visualizzate:", self.max_transactions_display_spinbox)
        
        self.cache_enabled_check = QCheckBox("Abilita cache per migliorare le performance")
        self.cache_enabled_check.setChecked(True)
        performance_layout.addRow("Cache:", self.cache_enabled_check)
        
        layout.addWidget(performance_group)
        
        # Debug
        debug_group = QGroupBox("Debug e Logging")
        debug_layout = QVBoxLayout(debug_group)
        
        self.enable_logging_check = QCheckBox("Abilita logging dettagliato")
        debug_layout.addWidget(self.enable_logging_check)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["INFO", "DEBUG", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        
        log_level_layout = QFormLayout()
        log_level_layout.addRow("Livello log:", self.log_level_combo)
        debug_layout.addLayout(log_level_layout)
        
        # Pulsante visualizza log
        view_logs_btn = QPushButton("📋 Visualizza Log")
        view_logs_btn.clicked.connect(self.view_application_logs)
        debug_layout.addWidget(view_logs_btn)
        
        layout.addWidget(debug_group)
        
        # Reset applicazione
        reset_group = QGroupBox("Reset Applicazione")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_warning = QLabel("""
        <b>⚠️ Attenzione:</b> Queste operazioni sono irreversibili.<br>
        Assicurati di aver creato un backup prima di procedere.
        """)
        reset_warning.setStyleSheet("color: #E74C3C; padding: 10px; background-color: #FADBD8; border-radius: 5px;")
        reset_warning.setWordWrap(True)
        reset_layout.addWidget(reset_warning)
        
        reset_buttons_layout = QHBoxLayout()
        
        reset_settings_btn = QPushButton("🔄 Reset Impostazioni")
        reset_settings_btn.clicked.connect(self.reset_settings)
        reset_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #F39C12;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E67E22;
            }
        """)
        reset_buttons_layout.addWidget(reset_settings_btn)
        
        reset_all_btn = QPushButton("💥 Reset Completo")
        reset_all_btn.clicked.connect(self.reset_all_data)
        reset_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        reset_buttons_layout.addWidget(reset_all_btn)
        
        reset_buttons_layout.addStretch()
        
        reset_layout.addLayout(reset_buttons_layout)
        layout.addWidget(reset_group)
        
        layout.addStretch()
        
        parent.addTab(tab_widget, "🔧 Avanzate")
    
    def create_control_buttons(self, parent_layout):
        """Crea i pulsanti di controllo"""
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        buttons_layout = QHBoxLayout(buttons_frame)
        
        # Pulsante reset
        reset_btn = QPushButton("🔄 Ripristina Default")
        reset_btn.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        # Pulsante annulla
        cancel_btn = QPushButton("❌ Annulla")
        cancel_btn.clicked.connect(self.cancel_changes)
        buttons_layout.addWidget(cancel_btn)
        
        # Pulsante salva
        save_btn = QPushButton("💾 Salva Impostazioni")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
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
        buttons_layout.addWidget(save_btn)
        
        parent_layout.addWidget(buttons_frame)
    
    def load_current_settings(self):
        """Carica le impostazioni correnti nell'interfaccia"""
        try:
            # Generale
            self.currency_combo.setCurrentText(self.config.get('default_currency', 'EUR'))
            self.date_format_combo.setCurrentText(self.config.get('date_format', 'DD/MM/YYYY'))
            self.decimal_separator_combo.setCurrentText(self.config.get('decimal_separator', ','))
            self.thousands_separator_combo.setCurrentText(self.config.get('thousands_separator', '.'))
            
            # Database - aggiorna info corrente
            self.update_database_info()
            self.refresh_database_stats()
            
            # Export folder
            import tempfile
            default_export = tempfile.gettempdir()
            self.export_folder_edit.setText(self.config.get('export_folder', default_export))
            
        except Exception as e:
            print(f"Errore nel caricamento impostazioni: {e}")
    
    def update_database_info(self):
        """Aggiorna le informazioni del database"""
        try:
            from ..utils.common_utils import ConfigUtils
            app_data_dir = ConfigUtils.get_app_data_dir()
            db_path = os.path.join(app_data_dir, "barflow.db")
            
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                size_mb = file_size / (1024 * 1024)
                
                self.current_db_label.setText(
                    f"📍 {db_path}\n"
                    f"📊 Dimensione: {size_mb:.2f} MB"
                )
            else:
                self.current_db_label.setText("❌ Database non trovato")
                
        except Exception as e:
            self.current_db_label.setText(f"❌ Errore: {e}")
    
    def refresh_database_stats(self):
        """Aggiorna le statistiche del database"""
        try:
            # Dovremmo iniettare il db_manager o importarlo
            # Per ora mostra info di base
            stats_text = """
            📊 Statistiche Database:
            • Transazioni: -- (richiede connessione DB)
            • Categorie: -- 
            • Profili import: --
            • Ultimo backup: --
            
            Utilizza il pulsante 'Aggiorna Statistiche' per informazioni dettagliate.
            """
            
            self.db_stats_label.setText(stats_text)
            
        except Exception as e:
            self.db_stats_label.setText(f"Errore nel caricamento statistiche: {e}")
    
    def update_font_size_label(self, value):
        """Aggiorna l'etichetta della dimensione font"""
        self.font_size_label.setText(f"{value}px")
    
    def create_database_backup(self):
        """Crea un backup del database"""
        try:
            from ..utils.common_utils import ConfigUtils
            app_data_dir = ConfigUtils.get_app_data_dir()
            db_path = os.path.join(app_data_dir, "barflow.db")
            
            if not os.path.exists(db_path):
                QMessageBox.warning(self, "Avviso", "Database non trovato")
                return
            
            # Selezione cartella backup
            backup_folder = QFileDialog.getExistingDirectory(
                self,
                "Seleziona cartella per il backup",
                os.path.expanduser("~")
            )
            
            if backup_folder:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"barflow_backup_{timestamp}.db"
                backup_path = os.path.join(backup_folder, backup_filename)
                
                # Copia il database
                shutil.copy2(db_path, backup_path)
                
                QMessageBox.information(
                    self,
                    "Backup Completato",
                    f"✅ Backup creato con successo!\n\n"
                    f"File: {backup_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella creazione del backup: {e}")
    
    def restore_database_backup(self):
        """Ripristina un backup del database"""
        reply = QMessageBox.warning(
            self,
            "Conferma Ripristino",
            "⚠️ ATTENZIONE!\n\n"
            "Il ripristino del backup sostituirà completamente il database corrente.\n"
            "Tutti i dati non salvati andranno persi.\n\n"
            "Vuoi continuare?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Selezione file backup
                backup_file, _ = QFileDialog.getOpenFileName(
                    self,
                    "Seleziona file di backup",
                    os.path.expanduser("~"),
                    "File Database (*.db);;Tutti i file (*)"
                )
                
                if backup_file:
                    from ..utils.common_utils import ConfigUtils
                    app_data_dir = ConfigUtils.get_app_data_dir()
                    db_path = os.path.join(app_data_dir, "barflow.db")
                    
                    # Crea backup del database corrente
                    if os.path.exists(db_path):
                        backup_current = db_path + ".backup_before_restore"
                        shutil.copy2(db_path, backup_current)
                    
                    # Ripristina il backup
                    shutil.copy2(backup_file, db_path)
                    
                    QMessageBox.information(
                        self,
                        "Ripristino Completato",
                        "✅ Database ripristinato con successo!\n\n"
                        "L'applicazione verrà riavviata per applicare le modifiche."
                    )
                    
                    # TODO: Riavvia l'applicazione
                    
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nel ripristino: {e}")
    
    def change_database_location(self):
        """Cambia la posizione del database"""
        QMessageBox.information(
            self,
            "Funzione Non Disponibile",
            "La modifica della posizione del database verrà implementata in una versione futura."
        )
    
    def browse_export_folder(self):
        """Seleziona la cartella di export"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleziona cartella per i file esportati",
            self.export_folder_edit.text()
        )
        
        if folder:
            self.export_folder_edit.setText(folder)
    
    def cleanup_temp_files(self):
        """Pulisce i file temporanei"""
        try:
            import tempfile
            import glob
            
            temp_dir = tempfile.gettempdir()
            pattern = os.path.join(temp_dir, "BarFlow_Report_*.xlsx")
            temp_files = glob.glob(pattern)
            
            if temp_files:
                count = len(temp_files)
                
                reply = QMessageBox.question(
                    self,
                    "Conferma Pulizia",
                    f"Trovati {count} file temporanei di BarFlow.\n"
                    "Vuoi eliminarli?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    for file_path in temp_files:
                        try:
                            os.remove(file_path)
                        except:
                            continue
                    
                    QMessageBox.information(
                        self,
                        "Pulizia Completata",
                        f"✅ Eliminati {count} file temporanei"
                    )
            else:
                QMessageBox.information(
                    self,
                    "Pulizia",
                    "Nessun file temporaneo da eliminare"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nella pulizia: {e}")
    
    def view_application_logs(self):
        """Visualizza i log dell'applicazione"""
        QMessageBox.information(
            self,
            "Log Applicazione",
            "La visualizzazione dei log verrà implementata in una versione futura.\n\n"
            "I log dell'applicazione saranno salvati in:\n"
            f"{Path.home() / 'AppData' / 'Local' / 'BarFlow' / 'logs'}"
        )
    
    def reset_settings(self):
        """Reset delle sole impostazioni"""
        reply = QMessageBox.question(
            self,
            "Conferma Reset Impostazioni",
            "Vuoi ripristinare tutte le impostazioni ai valori predefiniti?\n\n"
            "I dati delle transazioni NON saranno toccati.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from ..utils.common_utils import ConfigUtils
                
                # Reset alla configurazione di default
                self.config = ConfigUtils.DEFAULT_CONFIG.copy()
                
                # Ricarica l'interfaccia
                self.load_current_settings()
                
                QMessageBox.information(
                    self,
                    "Reset Completato",
                    "✅ Impostazioni ripristinate ai valori predefiniti"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nel reset: {e}")
    
    def reset_all_data(self):
        """Reset completo di tutti i dati"""
        reply = QMessageBox.critical(
            self,
            "⚠️ RESET COMPLETO",
            "ATTENZIONE: Questa operazione eliminerà TUTTI i dati:\n\n"
            "• Tutte le transazioni\n"
            "• Tutte le categorie personalizzate\n"
            "• Tutti i profili di import\n"
            "• Tutte le impostazioni\n\n"
            "Questa operazione è IRREVERSIBILE!\n\n"
            "Sei assolutamente sicuro di voler continuare?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Seconda conferma
            confirm_text, ok = QDialog().getText(
                self,
                "Conferma Reset",
                "Per confermare, digita 'RESET COMPLETO':",
                QLineEdit.Normal,
                ""
            )
            
            if ok and confirm_text == "RESET COMPLETO":
                try:
                    # TODO: Implementare reset completo
                    QMessageBox.information(
                        self,
                        "Reset Completo",
                        "Reset completo implementato in versione futura.\n"
                        "Per ora elimina manualmente il database dalla cartella AppData."
                    )
                    
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Errore nel reset: {e}")
    
    def reset_to_defaults(self):
        """Ripristina i valori predefiniti nel form"""
        from ..utils.common_utils import ConfigUtils
        
        default_config = ConfigUtils.DEFAULT_CONFIG.copy()
        
        # Aggiorna solo i controlli dell'interfaccia
        self.currency_combo.setCurrentText(default_config.get('default_currency', 'EUR'))
        self.date_format_combo.setCurrentText(default_config.get('date_format', 'DD/MM/YYYY'))
        # ... altri controlli
        
        QMessageBox.information(
            self,
            "Default Ripristinati",
            "Valori predefiniti ripristinati nell'interfaccia.\n"
            "Clicca 'Salva Impostazioni' per confermare."
        )
    
    def cancel_changes(self):
        """Annulla le modifiche"""
        self.load_current_settings()
        QMessageBox.information(
            self,
            "Modifiche Annullate",
            "Tutte le modifiche sono state annullate"
        )
    
    def save_settings(self):
        """Salva le impostazioni"""
        try:
            # Aggiorna la configurazione
            self.config['default_currency'] = self.currency_combo.currentText()
            self.config['date_format'] = self.date_format_combo.currentText()
            self.config['decimal_separator'] = self.decimal_separator_combo.currentText()
            self.config['thousands_separator'] = self.thousands_separator_combo.currentText()
            self.config['export_folder'] = self.export_folder_edit.text()
            
            # Salva nel file
            from ..utils.common_utils import ConfigUtils
            if ConfigUtils.save_config(self.config):
                QMessageBox.information(
                    self,
                    "Impostazioni Salvate",
                    "✅ Impostazioni salvate con successo!"
                )
                
                # Emetti segnale di cambio
                self.settings_changed.emit()
                
            else:
                QMessageBox.warning(
                    self,
                    "Errore Salvataggio",
                    "Impossibile salvare le impostazioni nel file di configurazione"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {e}")