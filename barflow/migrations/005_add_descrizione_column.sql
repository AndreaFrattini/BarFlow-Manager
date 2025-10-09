-- Migrazione per aggiungere la colonna DESCRIZIONE alla tabella transactions
-- Versione: 5

ALTER TABLE transactions ADD COLUMN descrizione TEXT;