-- Migrazione per correggere errori di schema
-- Verifica e corregge le colonne mancanti

-- Crea una tabella temporanea con lo schema corretto
CREATE TABLE IF NOT EXISTS transactions_temp (
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

-- Copia i dati esistenti nella nuova tabella usando solo colonne che esistono sicuramente
INSERT OR IGNORE INTO transactions_temp (
    data, sorgente, fornitore, importo_netto, data_inserimento, file_origine
)
SELECT 
    data, 
    sorgente, 
    fornitore,
    importo_netto,
    data_inserimento,
    file_origine
FROM transactions;

-- Sostituisci la vecchia tabella con quella nuova
DROP TABLE transactions;
ALTER TABLE transactions_temp RENAME TO transactions;

-- Ricrea gli indici
CREATE INDEX IF NOT EXISTS idx_data ON transactions(data);
CREATE INDEX IF NOT EXISTS idx_sorgente ON transactions(sorgente);
CREATE INDEX IF NOT EXISTS idx_hash ON transactions(hash_record);