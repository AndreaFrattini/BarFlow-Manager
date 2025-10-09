"""
Manager per il database temporaneo delle transazioni
"""
import sqlite3
import hashlib
import pandas as pd
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def get_temp_db_path() -> Path:
    """Ottieni il percorso del database temporaneo nella cartella historical_data dell'applicazione"""
    # Trova la root dell'applicazione (dove si trova il file main.py)
    current_dir = Path(__file__).parent.parent.parent  # Da barflow/data/ torna alla root
    historical_data_dir = current_dir / "historical_data"
    
    # Crea la cartella se non esiste
    historical_data_dir.mkdir(parents=True, exist_ok=True)
    
    return historical_data_dir / "temporary_transactions.db"

class TemporaryDatabaseManager:
    """Manager per il database temporaneo delle transazioni importate dall'utente."""
    
    def __init__(self, db_path=None):
        # Usa il path specifico per il database temporaneo
        self.db_path = Path(db_path) if db_path else get_temp_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inizializza il database temporaneo con le tabelle necessarie."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporary_transactions (
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
                    import_timestamp REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_temp_data ON temporary_transactions(data);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_temp_sorgente ON temporary_transactions(sorgente);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_temp_hash ON temporary_transactions(hash_record);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_temp_import_timestamp ON temporary_transactions(import_timestamp);
            """)
    
    def _generate_record_hash(self, record):
        """Genera un hash univoco per il record per evitare duplicati."""
        key = f"{record['DATA']}{record['SORGENTE']}{record.get('DESCRIZIONE', '')}{record.get('FORNITORE', '')}{record.get('NUMERO FORNITORE', '')}{record.get('NUMERO OPERAZIONE POS', '')}{record['IMPORTO NETTO']}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def add_transactions(self, transactions_data, import_timestamp):
        """Aggiunge le transazioni al database temporaneo."""
        added_count = 0
        duplicate_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for record in transactions_data:
                record_hash = self._generate_record_hash(record)
                
                try:
                    conn.execute("""
                        INSERT INTO temporary_transactions 
                        (data, sorgente, descrizione, fornitore, numero_fornitore, numero_operazione_pos, 
                         importo_lordo_pos, commissione_pos, importo_netto, hash_record, import_timestamp)
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
                        import_timestamp
                    ))
                    added_count += 1
                except sqlite3.IntegrityError:
                    # Record duplicato
                    duplicate_count += 1
        
        return added_count, duplicate_count
    
    def load_all_temporary_transactions(self):
        """Carica tutte le transazioni temporanee dal database."""
        with sqlite3.connect(self.db_path) as conn:
            try:
                query = """
                    SELECT data as DATA,
                           sorgente as SORGENTE,
                           descrizione as DESCRIZIONE,
                           fornitore as FORNITORE,
                           numero_fornitore as 'NUMERO FORNITORE',
                           numero_operazione_pos as 'NUMERO OPERAZIONE POS',
                           importo_lordo_pos as 'IMPORTO LORDO POS',
                           commissione_pos as 'COMMISSIONE POS',
                           importo_netto as 'IMPORTO NETTO',
                           import_timestamp as '_IMPORT_TIMESTAMP'
                    FROM temporary_transactions 
                    ORDER BY import_timestamp DESC, data DESC
                """
                
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
            except Exception as e:
                logger.error(f"Errore nel caricamento transazioni temporanee: {e}")
                return []
    
    def get_temporary_transactions_count(self):
        """Restituisce il numero di transazioni temporanee."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            count = cursor.execute("SELECT COUNT(*) FROM temporary_transactions").fetchone()[0]
            return count
    
    def clear_all_temporary_transactions(self):
        """Pulisce completamente tutte le transazioni temporanee (mantiene lo schema)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM temporary_transactions")
            # Reset dell'autoincrement per ricominciare da 1
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='temporary_transactions'")
            conn.commit()
        
        logger.info("Database temporaneo pulito completamente")
    
    def get_temporary_database_stats(self):
        """Ottieni statistiche del database temporaneo."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conteggio totale
            total = cursor.execute("SELECT COUNT(*) FROM temporary_transactions").fetchone()[0]
            
            if total == 0:
                return {
                    'total_records': 0,
                    'date_range': (None, None),
                    'db_size_mb': 0
                }
            
            # Prima e ultima data
            date_range = cursor.execute("""
                SELECT MIN(data) as min_date, MAX(data) as max_date 
                FROM temporary_transactions
            """).fetchone()
            
            # Dimensione database
            db_size = self.db_path.stat().st_size / 1024 / 1024  # MB
            
            return {
                'total_records': total,
                'date_range': date_range,
                'db_size_mb': round(db_size, 2)
            }
    
    def database_exists(self):
        """Verifica se il database temporaneo esiste."""
        return self.db_path.exists()
    
    def delete_database(self):
        """Elimina completamente il file del database temporaneo."""
        try:
            if self.db_path.exists():
                self.db_path.unlink()
                logger.info(f"Database temporaneo eliminato: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Errore nell'eliminazione del database temporaneo: {e}")
            return False