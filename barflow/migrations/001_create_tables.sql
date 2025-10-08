-- Creazione tabella principale transazioni
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
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_data ON transactions(data);
CREATE INDEX IF NOT EXISTS idx_sorgente ON transactions(sorgente);
CREATE INDEX IF NOT EXISTS idx_hash ON transactions(hash_record);