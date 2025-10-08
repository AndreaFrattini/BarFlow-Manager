#!/usr/bin/env python3
"""
Script per controllare lo schema della tabella transactions nel database storico
"""
import sqlite3
from pathlib import Path

def check_schema():
    # Percorsi dei database
    historical_db = Path("historical_data/barflow_history.db")
    initial_db = Path("barflow/migrations/initial_db.sqlite")
    
    print("=== CONTROLLO SCHEMA DATABASE STORICO ===")
    print()
    
    # Controlla database storico esistente
    if historical_db.exists():
        print(f"Database storico trovato: {historical_db}")
        with sqlite3.connect(historical_db) as conn:
            cursor = conn.cursor()
            
            # Ottieni info schema
            cursor.execute("PRAGMA table_info(transactions)")
            columns = cursor.fetchall()
            
            print("Colonne nella tabella transactions (storico):")
            for col in columns:
                print(f"  {col[1]} - {col[2]} - {'NOT NULL' if col[3] else 'NULL'}")
            
            # Conta record
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            print(f"Numero di record: {count}")
            
            # Mostra qualche sample se ci sono dati
            if count > 0:
                print("\nPrimi 3 record:")
                cursor.execute("SELECT * FROM transactions LIMIT 3")
                records = cursor.fetchall()
                for i, record in enumerate(records):
                    print(f"  Record {i+1}: {record}")
    else:
        print(f"Database storico non trovato: {historical_db}")
    
    print()
    print("=== CONTROLLO DATABASE INIZIALE ===")
    
    # Controlla database template iniziale
    if initial_db.exists():
        print(f"Database template trovato: {initial_db}")
        with sqlite3.connect(initial_db) as conn:
            cursor = conn.cursor()
            
            # Ottieni info schema
            cursor.execute("PRAGMA table_info(transactions)")
            columns = cursor.fetchall()
            
            print("Colonne nella tabella transactions (template):")
            for col in columns:
                print(f"  {col[1]} - {col[2]} - {'NOT NULL' if col[3] else 'NULL'}")
    else:
        print(f"Database template non trovato: {initial_db}")
    
    print()
    print("=== SCHEMA ATTESO (DALLE UI) ===")
    expected_columns = [
        "DATA", "SORGENTE", "FORNITORE", "NUMERO FORNITORE", 
        "NUMERO OPERAZIONE POS", "IMPORTO LORDO POS", "COMMISSIONE POS", "IMPORTO NETTO"
    ]
    print("Colonne attese dalla UI TransactionsWidget:")
    for col in expected_columns:
        print(f"  {col}")

if __name__ == "__main__":
    check_schema()