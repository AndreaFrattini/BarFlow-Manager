import sqlite3
import os
import re
import importlib.resources
from pathlib import Path
import logging
import sys

logger = logging.getLogger(__name__)

class PySQLiteMigrator:
    def __init__(self, db_path: str, migrations_package: str):
        self.db_path = db_path
        self.migrations_package = migrations_package
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_db_version(self, cursor: sqlite3.Cursor) -> int:
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER)")
            cursor.execute("SELECT version FROM _schema_version LIMIT 1")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                # Inserisci versione iniziale
                cursor.execute("INSERT INTO _schema_version (version) VALUES (0)")
                return 0
        except sqlite3.Error as e:
            logger.error(f"Failed to get DB version: {e}")
            raise

    def _set_db_version(self, cursor: sqlite3.Cursor, version: int):
        try:
            # Prima cancella tutte le versioni esistenti, poi inserisci la nuova
            cursor.execute("DELETE FROM _schema_version")
            cursor.execute("INSERT INTO _schema_version (version) VALUES (?)", (version,))
        except sqlite3.Error as e:
            logger.error(f"Failed to set DB version to {version}: {e}")
            raise

    def _get_migration_scripts(self) -> list:
        scripts = []
        try:
            # Usa importlib.resources per accedere ai file nelle migrazioni
            files = importlib.resources.files(self.migrations_package)
            for file_ref in files.iterdir():
                if file_ref.is_file():
                    match = re.match(r"^(\d+)_([a-zA-Z0-9_]+)\.(py|sql)$", file_ref.name)
                    if match:
                        scripts.append((int(match.group(1)), file_ref, match.group(2)))
        except Exception as e:
            logger.warning(f"No migration scripts found: {e}")
        return sorted(scripts, key=lambda x: x[0])

    def apply_migrations(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            current_version = self._get_db_version(cursor)
            migrations = self._get_migration_scripts()

            for version, script_ref, name in migrations:
                if version > current_version:
                    logger.info(f"Applying migration: {name} (v{version})")
                    try:
                        # Non usiamo BEGIN/COMMIT esplicite, lasciamo che SQLite gestisca
                        # le transazioni automaticamente
                        if script_ref.name.endswith(".sql"):
                            cursor.executescript(script_ref.read_text(encoding="utf-8"))
                        elif script_ref.name.endswith(".py"):
                            module_name = f"{self.migrations_package}.{script_ref.stem}"
                            migration_module = importlib.import_module(module_name)
                            if hasattr(migration_module, 'upgrade'):
                                migration_module.upgrade(cursor)

                        self._set_db_version(cursor, version)
                        conn.commit()  # Commit esplicito dopo ogni migrazione
                        current_version = version
                        logger.info(f"Successfully applied migration: {name}")
                    except Exception as e:
                        conn.rollback()
                        logger.error(f"Error applying migration {name}: {e}")
                        raise

            logger.info(f"Database schema up-to-date (version {current_version})")
        finally:
            if conn:
                conn.close()