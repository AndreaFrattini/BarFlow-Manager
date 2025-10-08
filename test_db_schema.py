#!/usr/bin/env python3
"""
Script per testare che il database manager funzioni correttamente con lo schema aggiornato
"""
import sys
from pathlib import Path

# Aggiungi il path del progetto al sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from barflow.data.db_manager import DatabaseManager

def test_database_operations():
    """Testa le operazioni del database manager"""
    
    # Usa il database storico esistente
    db_manager = DatabaseManager("historical_data/barflow_history.db")
    
    print("=== TEST CARICAMENTO TRANSAZIONI ===")
    
    # Test caricamento di tutte le transazioni
    try:
        all_transactions = db_manager.load_all_transactions()
        print(f"✅ Caricate {len(all_transactions)} transazioni dal database")
        
        if all_transactions:
            # Mostra la prima transazione per verificare la struttura
            first_transaction = all_transactions[0]
            print("Prima transazione caricata:")
            for key, value in first_transaction.items():
                print(f"  {key}: {value}")
            
            # Verifica che abbia tutte le colonne attese
            expected_columns = [
                "DATA", "SORGENTE", "FORNITORE", "NUMERO FORNITORE",
                "NUMERO OPERAZIONE POS", "IMPORTO LORDO POS", "COMMISSIONE POS", "IMPORTO NETTO"
            ]
            
            missing_columns = []
            for col in expected_columns:
                if col not in first_transaction:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"❌ Colonne mancanti: {missing_columns}")
            else:
                print("✅ Tutte le colonne attese sono presenti")
        
    except Exception as e:
        print(f"❌ Errore nel caricamento delle transazioni: {e}")
        return False
    
    print("\n=== TEST STATISTICHE DATABASE ===")
    
    # Test statistiche
    try:
        stats = db_manager.get_database_stats()
        print(f"✅ Statistiche database:")
        print(f"  - Record totali: {stats['total_records']}")
        print(f"  - Intervallo date: {stats['date_range']}")
        print(f"  - Dimensione DB: {stats['db_size_mb']} MB")
    except Exception as e:
        print(f"❌ Errore nelle statistiche: {e}")
        return False
    
    print("\n=== TEST CARICAMENTO PER PERIODO ===")
    
    # Test caricamento per periodo
    try:
        period_transactions = db_manager.load_transactions_by_period("2025-01-01", "2025-01-31")
        print(f"✅ Caricate {len(period_transactions)} transazioni per Gennaio 2025")
    except Exception as e:
        print(f"❌ Errore nel caricamento per periodo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing database manager with updated schema...")
    success = test_database_operations()
    
    if success:
        print("\n🎉 Tutti i test sono passati! Il database storico ha ora lo stesso schema della sezione transazioni.")
    else:
        print("\n💥 Alcuni test sono falliti.")
        sys.exit(1)