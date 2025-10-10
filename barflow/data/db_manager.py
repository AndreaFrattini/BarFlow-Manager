from barflow.utils import get_app_data_directory
from .py_sqlite_migrator import PySQLiteMigrator
import shutil
import importlib.resources
from pathlib import Path
import sqlite3
import hashlib
import pandas as pd
import logging

APP_NAME = "BarFlow"
APP_AUTHOR = "BarFlowTeam"

logger = logging.getLogger(__name__)

def get_db_path() -> Path:
    """Ottieni il percorso del database nell'area dati dell'applicazione"""
    # Utilizza il sistema di percorsi centralizzato per garantire la portabilità
    app_data_dir = get_app_data_directory()
    return app_data_dir / "barflow_history.db"

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
    
    # Assicurati che la struttura base esista
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                sorgente TEXT NOT NULL,
                descrizione TEXT,
                fornitore TEXT,
                numero_fornitore TEXT,
                numero_operazione_pos TEXT,
                importo_lordo_pos REAL,
                commissione_pos REAL,
                importo_netto REAL NOT NULL,
                hash_record TEXT UNIQUE,
                data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_origine TEXT
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_data ON transactions(data);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sorgente ON transactions(sorgente);
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_hash ON transactions(hash_record);
        """)

    # Applica le migrazioni solo se necessarie
    try:
        migrator = PySQLiteMigrator(str(db_path), "barflow.migrations")
        migrator.apply_migrations()
        logger.info("Database migrations applied successfully")
    except Exception as e:
        logger.warning(f"Migration failed, but basic structure exists: {e}")
    
    logger.info("Database initialization complete")

class DatabaseManager:
    def __init__(self, db_path=None):
        # Usa lo stesso path del sistema di migrazione se non specificato
        self.db_path = Path(db_path) if db_path else get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inizializza il database con le tabelle necessarie."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    sorgente TEXT NOT NULL,
                    descrizione TEXT,
                    fornitore TEXT,
                    numero_fornitore TEXT,
                    numero_operazione_pos TEXT,
                    importo_lordo_pos REAL,
                    commissione_pos REAL,
                    importo_netto REAL NOT NULL,
                    hash_record TEXT UNIQUE,
                    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_origine TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_data ON transactions(data);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sorgente ON transactions(sorgente);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_hash ON transactions(hash_record);
            """)
    
    def _generate_record_hash(self, record):
        """Genera un hash univoco per il record per evitare duplicati."""
        key = f"{record['DATA']}{record['SORGENTE']}{record.get('DESCRIZIONE', '')}{record.get('FORNITORE', '')}{record.get('NUMERO FORNITORE', '')}{record.get('NUMERO OPERAZIONE POS', '')}{record['IMPORTO NETTO']}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def save_transactions(self, transactions_data, file_origin=None):
        """Salva le transazioni nel database, evitando duplicati."""
        saved_count = 0
        duplicate_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for record in transactions_data:
                record_hash = self._generate_record_hash(record)
                
                try:
                    conn.execute("""
                        INSERT INTO transactions 
                        (data, sorgente, descrizione, fornitore, numero_fornitore, numero_operazione_pos, 
                         importo_lordo_pos, commissione_pos, importo_netto, hash_record, file_origine)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['DATA'],
                        record['SORGENTE'],
                        record.get('DESCRIZIONE'),
                        record.get('FORNITORE'),
                        record.get('NUMERO FORNITORE'),
                        record.get('NUMERO OPERAZIONE POS'),
                        record.get('IMPORTO LORDO POS'),
                        record.get('COMMISSIONE POS'),
                        float(record['IMPORTO NETTO']),
                        record_hash,
                        file_origin
                    ))
                    saved_count += 1
                except sqlite3.IntegrityError:
                    # Record duplicato
                    duplicate_count += 1
        
        return saved_count, duplicate_count
    
    def load_all_transactions(self):
        """Carica tutte le transazioni dal database."""
        with sqlite3.connect(self.db_path) as conn:
            # Prima controlla quali colonne esistono nella tabella
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(transactions)")
            columns_info = cursor.fetchall()
            existing_columns = [col[1] for col in columns_info]
            
            # Costruisci la query dinamicamente basandoti sulle colonne esistenti
            select_clauses = [
                "data as DATA",
                "sorgente as SORGENTE"
            ]
            
            # Aggiungi DESCRIZIONE se esiste
            if "descrizione" in existing_columns:
                select_clauses.append("descrizione as DESCRIZIONE")
            else:
                select_clauses.append("NULL as DESCRIZIONE")
                
            # Aggiungi FORNITORE
            select_clauses.append("fornitore as FORNITORE")
            
            # Aggiungi colonne opzionali solo se esistono
            optional_columns = [
                ("numero_fornitore", "NUMERO FORNITORE"),
                ("numero_operazione_pos", "NUMERO OPERAZIONE POS"),
                ("importo_lordo_pos", "IMPORTO LORDO POS"),
                ("commissione_pos", "COMMISSIONE POS")
            ]
            
            for db_col, alias in optional_columns:
                if db_col in existing_columns:
                    select_clauses.append(f"{db_col} as `{alias}`")
                else:
                    # Aggiungi NULL come valore di default per colonne mancanti
                    select_clauses.append(f"NULL as `{alias}`")
            
            # La colonna importo_netto deve sempre esistere
            select_clauses.append("importo_netto as `IMPORTO NETTO`")
            
            query = f"""
                SELECT {', '.join(select_clauses)}
                FROM transactions 
                ORDER BY data DESC
            """
            
            try:
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
            except Exception as e:
                logger.error(f"Errore nel caricamento transazioni: {e}")
                # Fallback: carica solo le colonne essenziali
                fallback_query = """
                    SELECT data as DATA, sorgente as SORGENTE, 
                           COALESCE(descrizione, '') as DESCRIZIONE,
                           fornitore as FORNITORE,
                           importo_netto as `IMPORTO NETTO`,
                           NULL as `NUMERO FORNITORE`,
                           NULL as `NUMERO OPERAZIONE POS`,
                           NULL as `IMPORTO LORDO POS`,
                           NULL as `COMMISSIONE POS`
                    FROM transactions 
                    ORDER BY data DESC
                """
                df = pd.read_sql_query(fallback_query, conn)
                return df.to_dict('records')
    
    def load_transactions_by_period(self, start_date, end_date):
        """Carica transazioni per un periodo specifico."""
        with sqlite3.connect(self.db_path) as conn:
            # Prima controlla quali colonne esistono nella tabella
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(transactions)")
            columns_info = cursor.fetchall()
            existing_columns = [col[1] for col in columns_info]
            
            # Costruisci la query dinamicamente basandoti sulle colonne esistenti
            select_clauses = [
                "data as DATA",
                "sorgente as SORGENTE"
            ]
            
            # Aggiungi DESCRIZIONE se esiste
            if "descrizione" in existing_columns:
                select_clauses.append("descrizione as DESCRIZIONE")
            else:
                select_clauses.append("NULL as DESCRIZIONE")
                
            # Aggiungi FORNITORE
            select_clauses.append("fornitore as FORNITORE")
            
            # Aggiungi colonne opzionali solo se esistono
            optional_columns = [
                ("numero_fornitore", "NUMERO FORNITORE"),
                ("numero_operazione_pos", "NUMERO OPERAZIONE POS"),
                ("importo_lordo_pos", "IMPORTO LORDO POS"),
                ("commissione_pos", "COMMISSIONE POS")
            ]
            
            for db_col, alias in optional_columns:
                if db_col in existing_columns:
                    select_clauses.append(f"{db_col} as `{alias}`")
                else:
                    # Aggiungi NULL come valore di default per colonne mancanti
                    select_clauses.append(f"NULL as `{alias}`")
            
            # La colonna importo_netto deve sempre esistere
            select_clauses.append("importo_netto as `IMPORTO NETTO`")
            
            query = f"""
                SELECT {', '.join(select_clauses)}
                FROM transactions 
                WHERE data BETWEEN ? AND ?
                ORDER BY data DESC
            """
            
            try:
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                return df.to_dict('records')
            except Exception as e:
                logger.error(f"Errore nel caricamento transazioni per periodo: {e}")
                # Fallback: carica solo le colonne essenziali
                fallback_query = """
                    SELECT data as DATA, sorgente as SORGENTE, fornitore as FORNITORE,
                           importo_netto as `IMPORTO NETTO`,
                           NULL as `DESCRIZIONE`,
                           NULL as `NUMERO FORNITORE`,
                           NULL as `NUMERO OPERAZIONE POS`,
                           NULL as `IMPORTO LORDO POS`,
                           NULL as `COMMISSIONE POS`
                    FROM transactions 
                    WHERE data BETWEEN ? AND ?
                    ORDER BY data DESC
                """
                df = pd.read_sql_query(fallback_query, conn, params=(start_date, end_date))
                return df.to_dict('records')
    
    def get_database_stats(self):
        """Ottieni statistiche del database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conteggio totale
            total = cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            
            # Prima e ultima data
            date_range = cursor.execute("""
                SELECT MIN(data) as min_date, MAX(data) as max_date 
                FROM transactions
            """).fetchone()
            
            # Dimensione database
            db_size = self.db_path.stat().st_size / 1024 / 1024  # MB
            
            return {
                'total_records': total,
                'date_range': date_range,
                'db_size_mb': round(db_size, 2)
            }