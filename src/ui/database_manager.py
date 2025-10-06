import sqlite3
import pandas as pd
from pathlib import Path
import hashlib
from datetime import datetime

class DatabaseManager:
    """Manager per la gestione del database SQLite delle transazioni."""
    
    def __init__(self, db_path="historical_data/barflow_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inizializza il database con le tabelle necessarie."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    sorgente TEXT NOT NULL,
                    prodotto TEXT,
                    fornitore TEXT,
                    categoria TEXT,
                    quantita REAL,
                    importo REAL NOT NULL,
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
        key = f"{record['DATA']}{record['SORGENTE']}{record['PRODOTTO']}{record['IMPORTO']}"
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
                        (data, sorgente, prodotto, fornitore, categoria, quantita, importo, hash_record, file_origine)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['DATA'],
                        record['SORGENTE'],
                        record.get('PRODOTTO'),
                        record.get('FORNITORE'),
                        record.get('CATEGORIA'),
                        record.get("QUANTITA'"),
                        float(record['IMPORTO']),
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
            df = pd.read_sql_query("""
                SELECT data as DATA, sorgente as SORGENTE, prodotto as PRODOTTO, 
                       fornitore as FORNITORE, categoria as CATEGORIA, 
                       quantita as `QUANTITA'`, importo as IMPORTO
                FROM transactions 
                ORDER BY data DESC
            """, conn)
        
        return df.to_dict('records')
    
    def load_transactions_by_period(self, start_date, end_date):
        """Carica transazioni per un periodo specifico."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("""
                SELECT data as DATA, sorgente as SORGENTE, prodotto as PRODOTTO, 
                       fornitore as FORNITORE, categoria as CATEGORIA, 
                       quantita as `QUANTITA'`, importo as IMPORTO
                FROM transactions 
                WHERE data BETWEEN ? AND ?
                ORDER BY data DESC
            """, conn, params=(start_date, end_date))
        
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