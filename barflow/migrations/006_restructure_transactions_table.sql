-- Migrazione per riorganizzare la tabella transactions con la colonna descrizione nella posizione corretta
-- Versione: 6

-- Crea una tabella temporanea con la struttura corretta
CREATE TABLE transactions_temp (
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
);

-- Copia i dati dalla tabella originale alla temporanea
INSERT INTO transactions_temp (
    id, data, sorgente, descrizione, fornitore, numero_fornitore, numero_operazione_pos, 
    importo_lordo_pos, commissione_pos, importo_netto, hash_record, data_inserimento, file_origine
)
SELECT 
    id, data, sorgente, descrizione, fornitore, numero_fornitore, numero_operazione_pos, 
    importo_lordo_pos, commissione_pos, importo_netto, hash_record, data_inserimento, file_origine
FROM transactions;

-- Elimina la tabella originale
DROP TABLE transactions;

-- Rinomina la tabella temporanea
ALTER TABLE transactions_temp RENAME TO transactions;