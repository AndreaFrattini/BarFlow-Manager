"""
Modulo per la gestione del database SQLite di BarFlow
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class DatabaseManager:
    """Gestisce tutte le operazioni del database SQLite"""
    
    def __init__(self, db_path: str = None):
        """
        Inizializza il gestore del database
        
        Args:
            db_path: Percorso del file database. Se None, usa il percorso di default.
        """
        if db_path is None:
            # Usa directory AppData per Windows
            app_data = Path.home() / "AppData" / "Local" / "BarFlow"
            app_data.mkdir(parents=True, exist_ok=True)
            db_path = app_data / "barflow.db"
        
        self.db_path = str(db_path)
        self._init_database()
        self._init_default_categories()
    
    def _init_database(self):
        """Inizializza il database creando le tabelle necessarie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Abilita supporto JSON (SQLite 3.38+)
            cursor.execute("PRAGMA compile_options")
            
            # Tabella Categories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    is_cogs BOOLEAN NOT NULL DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabella SourceProfiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS source_profiles (
                    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    file_type TEXT NOT NULL,
                    mapping_schema_json TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabella ImportedSources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS imported_sources (
                    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_hash TEXT NOT NULL,
                    source_profile_id INTEGER,
                    granularity TEXT NOT NULL,
                    FOREIGN KEY (source_profile_id) REFERENCES source_profiles (profile_id)
                )
            """)
            
            # Tabella Transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_date DATE NOT NULL,
                    description TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    is_income BOOLEAN NOT NULL,
                    category_id INTEGER NOT NULL,
                    source_id INTEGER,
                    metadata_json TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (category_id),
                    FOREIGN KEY (source_id) REFERENCES imported_sources (source_id)
                )
            """)
            
            # Indici per prestazioni
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source_id)")
            
            conn.commit()
    
    def _init_default_categories(self):
        """Inizializza le categorie predefinite"""
        default_categories = [
            ("Bevande", True),   # COGS
            ("Cibo", True),      # COGS  
            ("Personale", False) # Spesa operativa
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for name, is_cogs in default_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, is_cogs) 
                    VALUES (?, ?)
                """, (name, is_cogs))
            
            conn.commit()
    
    def add_category(self, name: str, is_cogs: bool = False) -> int:
        """
        Aggiunge una nuova categoria
        
        Args:
            name: Nome della categoria
            is_cogs: Se True, la categoria è considerata Cost of Goods Sold
            
        Returns:
            ID della categoria creata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, is_cogs) 
                VALUES (?, ?)
            """, (name, is_cogs))
            conn.commit()
            return cursor.lastrowid
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Ottiene tutte le categorie"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category_id, name, is_cogs, created_date 
                FROM categories 
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def add_source_profile(self, name: str, file_type: str, mapping_schema: Dict[str, Any]) -> int:
        """
        Aggiunge un nuovo profilo sorgente
        
        Args:
            name: Nome del profilo
            file_type: Tipo di file (xlsx, xml)
            mapping_schema: Schema di mappatura dei campi
            
        Returns:
            ID del profilo creato
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO source_profiles (name, file_type, mapping_schema_json) 
                VALUES (?, ?, ?)
            """, (name, file_type, json.dumps(mapping_schema)))
            conn.commit()
            return cursor.lastrowid
    
    def get_source_profiles(self, file_type: str = None) -> List[Dict[str, Any]]:
        """
        Ottiene i profili sorgente, opzionalmente filtrati per tipo
        
        Args:
            file_type: Tipo di file da filtrare (opzionale)
            
        Returns:
            Lista dei profili sorgente
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if file_type:
                cursor.execute("""
                    SELECT profile_id, name, file_type, mapping_schema_json, created_date 
                    FROM source_profiles 
                    WHERE file_type = ?
                    ORDER BY name
                """, (file_type,))
            else:
                cursor.execute("""
                    SELECT profile_id, name, file_type, mapping_schema_json, created_date 
                    FROM source_profiles 
                    ORDER BY name
                """)
            
            profiles = []
            for row in cursor.fetchall():
                profile = dict(row)
                profile['mapping_schema'] = json.loads(profile['mapping_schema_json'])
                del profile['mapping_schema_json']
                profiles.append(profile)
            
            return profiles
    
    def add_imported_source(self, filename: str, file_hash: str, source_profile_id: int = None, granularity: str = "monthly") -> int:
        """
        Registra un nuovo file importato
        
        Args:
            filename: Nome del file
            file_hash: Hash del file per evitare duplicati
            source_profile_id: ID del profilo usato (opzionale)
            granularity: Granularità dei dati (daily, weekly, monthly)
            
        Returns:
            ID della sorgente creata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO imported_sources (filename, file_hash, source_profile_id, granularity) 
                VALUES (?, ?, ?, ?)
            """, (filename, file_hash, source_profile_id, granularity))
            conn.commit()
            return cursor.lastrowid
    
    def check_file_already_imported(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se un file è già stato importato
        
        Args:
            file_hash: Hash del file da verificare
            
        Returns:
            Informazioni del file se già importato, None altrimenti
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM imported_sources 
                WHERE file_hash = ?
            """, (file_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """
        Aggiunge multiple transazioni
        
        Args:
            transactions: Lista di dizionari con i dati delle transazioni
            
        Returns:
            Numero di transazioni inserite
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for transaction in transactions:
                metadata_json = json.dumps(transaction.get('metadata', {})) if transaction.get('metadata') else None
                
                cursor.execute("""
                    INSERT INTO transactions 
                    (transaction_date, description, amount, is_income, category_id, source_id, metadata_json) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction['transaction_date'],
                    transaction['description'],
                    transaction['amount'],
                    transaction['is_income'],
                    transaction['category_id'],
                    transaction.get('source_id'),
                    metadata_json
                ))
            
            conn.commit()
            return len(transactions)
    
    def get_transactions(self, start_date: str = None, end_date: str = None, 
                        category_id: int = None) -> List[Dict[str, Any]]:
        """
        Ottiene le transazioni con filtri opzionali
        
        Args:
            start_date: Data di inizio (formato YYYY-MM-DD)
            end_date: Data di fine (formato YYYY-MM-DD)
            category_id: ID categoria da filtrare
            
        Returns:
            Lista delle transazioni
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT t.*, c.name as category_name, c.is_cogs,
                       s.filename as source_filename
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.category_id
                LEFT JOIN imported_sources s ON t.source_id = s.source_id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND t.transaction_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND t.transaction_date <= ?"
                params.append(end_date)
            
            if category_id:
                query += " AND t.category_id = ?"
                params.append(category_id)
            
            query += " ORDER BY t.transaction_date DESC"
            
            cursor.execute(query, params)
            
            transactions = []
            for row in cursor.fetchall():
                transaction = dict(row)
                if transaction['metadata_json']:
                    transaction['metadata'] = json.loads(transaction['metadata_json'])
                del transaction['metadata_json']
                transactions.append(transaction)
            
            return transactions
    
    def get_financial_summary(self, start_date: str, end_date: str) -> Dict[str, float]:
        """
        Calcola il riepilogo finanziario per un periodo
        
        Args:
            start_date: Data di inizio (formato YYYY-MM-DD)
            end_date: Data di fine (formato YYYY-MM-DD)
            
        Returns:
            Dizionario con totali entrate, uscite, COGS e profitto lordo
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Entrate totali
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_income
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? 
                AND is_income = 1
            """, (start_date, end_date))
            total_income = cursor.fetchone()[0]
            
            # Uscite totali
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_expenses
                FROM transactions 
                WHERE transaction_date BETWEEN ? AND ? 
                AND is_income = 0
            """, (start_date, end_date))
            total_expenses = cursor.fetchone()[0]
            
            # COGS (Cost of Goods Sold)
            cursor.execute("""
                SELECT COALESCE(SUM(t.amount), 0) as total_cogs
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE t.transaction_date BETWEEN ? AND ? 
                AND t.is_income = 0 
                AND c.is_cogs = 1
            """, (start_date, end_date))
            total_cogs = cursor.fetchone()[0]
            
            # Profitto lordo = Entrate - COGS
            gross_profit = total_income - total_cogs
            
            # Profitto netto = Entrate - Tutte le uscite
            net_profit = total_income - total_expenses
            
            return {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'total_cogs': float(total_cogs),
                'gross_profit': float(gross_profit),
                'net_profit': float(net_profit)
            }
    
    def check_data_granularity_consistency(self) -> Tuple[bool, List[str]]:
        """
        Verifica la coerenza della granularità dei dati importati
        
        Returns:
            Tupla (is_consistent, list_of_granularities)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT granularity 
                FROM imported_sources 
                ORDER BY granularity
            """)
            granularities = [row[0] for row in cursor.fetchall()]
            
            is_consistent = len(granularities) <= 1
            return is_consistent, granularities
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Elimina una transazione
        
        Args:
            transaction_id: ID della transazione da eliminare
            
        Returns:
            True se eliminata con successo, False altrimenti
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_transaction(self, transaction_id: int, **kwargs) -> bool:
        """
        Aggiorna una transazione
        
        Args:
            transaction_id: ID della transazione da aggiornare
            **kwargs: Campi da aggiornare
            
        Returns:
            True se aggiornata con successo, False altrimenti
        """
        if not kwargs:
            return False
        
        valid_fields = ['transaction_date', 'description', 'amount', 'is_income', 'category_id', 'metadata']
        
        # Filtra solo i campi validi
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return False
        
        # Gestisci metadata separatamente
        if 'metadata' in updates:
            updates['metadata_json'] = json.dumps(updates.pop('metadata'))
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [transaction_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE transactions 
                SET {set_clause}
                WHERE transaction_id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0