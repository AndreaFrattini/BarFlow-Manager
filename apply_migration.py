#!/usr/bin/env python3
"""
Script per applicare la migrazione dello schema al database storico esistente
"""
import sys
import os
from pathlib import Path

# Aggiungi il path del progetto al sys.path per poter importare i moduli
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from barflow.data.py_sqlite_migrator import PySQLiteMigrator
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_migration_to_historical_db():
    """Applica le migrazioni al database storico esistente"""
    
    # Percorso del database storico
    historical_db_path = "historical_data/barflow_history.db"
    
    if not Path(historical_db_path).exists():
        logger.error(f"Database storico non trovato: {historical_db_path}")
        return False
    
    try:
        logger.info(f"Applicando migrazioni al database: {historical_db_path}")
        
        # Crea il migrator e applica le migrazioni
        migrator = PySQLiteMigrator(historical_db_path, "barflow.migrations")
        migrator.apply_migrations()
        
        logger.info("Migrazioni applicate con successo!")
        return True
        
    except Exception as e:
        logger.error(f"Errore durante l'applicazione delle migrazioni: {e}")
        return False

if __name__ == "__main__":
    success = apply_migration_to_historical_db()
    if success:
        print("✅ Migrazione completata con successo!")
        
        # Verifica lo schema dopo la migrazione
        print("\n=== VERIFICA SCHEMA POST-MIGRAZIONE ===")
        import sqlite3
        with sqlite3.connect("historical_data/barflow_history.db") as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(transactions)")
            columns = cursor.fetchall()
            
            print("Colonne nella tabella transactions (dopo migrazione):")
            for col in columns:
                print(f"  {col[1]} - {col[2]} - {'NOT NULL' if col[3] else 'NULL'}")
            
            # Verifica che i dati siano stati preservati
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            print(f"Numero di record preservati: {count}")
    else:
        print("❌ Migrazione fallita!")
        sys.exit(1)