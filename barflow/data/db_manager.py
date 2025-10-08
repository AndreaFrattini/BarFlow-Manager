from appdirs import user_data_dir
from .py_sqlite_migrator import PySQLiteMigrator
import shutil
import importlib.resources
from pathlib import Path
import sqlite3
import logging

APP_NAME = "BarFlow"
APP_AUTHOR = "BarFlowTeam"

logger = logging.getLogger(__name__)

def get_db_path() -> Path:
    """Ottieni il percorso del database nell'area dati utente del sistema"""
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "barflow_history.db"

def initialize_and_migrate_db():
    """Inizializza e aggiorna il database"""
    db_path = get_db_path()
    logger.info(f"Database path: {db_path}")
    
    if not db_path.exists():
        logger.info("Database not found. Initializing...")
        try:
            # Cerca il template del database nelle risorse
            with importlib.resources.path("barflow.migrations", "initial_db.sqlite") as template_path:
                if template_path.exists():
                    logger.info(f"Copying initial database from template")
                    shutil.copyfile(template_path, db_path)
                else:
                    logger.info("No template found, creating empty database")
        except (FileNotFoundError, ImportError):
            logger.info("No template available, will create empty database")

    # Applica le migrazioni
    migrator = PySQLiteMigrator(str(db_path), "barflow.migrations")
    migrator.apply_migrations()
    logger.info("Database initialization complete")

class DatabaseManager:
    def __init__(self):
        # Usa il nuovo percorso con appdirs
        self.db_path = str(get_db_path())

    def get_connection(self):
        """Ottieni una connessione al database"""
        return sqlite3.connect(self.db_path)