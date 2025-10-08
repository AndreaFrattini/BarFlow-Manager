-- Migrazione per aggiornare lo schema delle transazioni
-- Rinomina la vecchia tabella
ALTER TABLE transactions RENAME TO transactions_old;

-- Crea la nuova tabella con lo schema aggiornato
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    sorgente TEXT NOT NULL,
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

-- Migra i dati esistenti dalla vecchia struttura alla nuova
INSERT INTO transactions (
    id, data, sorgente, fornitore, numero_fornitore, numero_operazione_pos, 
    importo_lordo_pos, commissione_pos, importo_netto, hash_record, 
    data_inserimento, file_origine
)
SELECT 
    id, 
    data, 
    sorgente, 
    fornitore,
    NULL as numero_fornitore,
    NULL as numero_operazione_pos,
    NULL as importo_lordo_pos,
    NULL as commissione_pos,
    importo as importo_netto,
    hash_record,
    data_inserimento,
    file_origine
FROM transactions_old;

-- Elimina la vecchia tabella
DROP TABLE transactions_old;

-- Ricrea gli indici
CREATE INDEX IF NOT EXISTS idx_data ON transactions(data);
CREATE INDEX IF NOT EXISTS idx_sorgente ON transactions(sorgente);
CREATE INDEX IF NOT EXISTS idx_hash ON transactions(hash_record);