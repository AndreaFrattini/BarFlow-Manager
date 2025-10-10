-- Migrazione per aggiungere la colonna DESCRIZIONE alla tabella transactions
-- Versione: 5

-- Verifica se la colonna non esiste già prima di aggiungerla
ALTER TABLE transactions ADD COLUMN descrizione TEXT DEFAULT NULL;