#!/usr/bin/env python3
"""
Script per migrare il progetto esistente alla nuova struttura
"""
import shutil
from pathlib import Path

def migrate_project():
    """Migra la struttura del progetto"""
    
    # Crea la nuova struttura
    Path("barflow").mkdir(exist_ok=True)
    Path("barflow/ui").mkdir(exist_ok=True)
    Path("barflow/data").mkdir(exist_ok=True)
    Path("barflow/migrations").mkdir(exist_ok=True)
    Path("barflow/resources").mkdir(exist_ok=True)
    
    # Sposta i file UI
    src_ui = Path("src/ui")
    if src_ui.exists():
        for file in src_ui.glob("*.py"):
            if file.name != "__pycache__":
                shutil.copy2(file, f"barflow/ui/{file.name}")
    
    # Sposta le risorse
    if Path("logo").exists():
        shutil.copytree("logo", "barflow/resources/logo", dirs_exist_ok=True)
    
    # Crea file __init__.py
    Path("barflow/__init__.py").touch()
    Path("barflow/ui/__init__.py").touch()
    Path("barflow/data/__init__.py").touch()
    Path("barflow/migrations/__init__.py").touch()
    
    print("✅ Migrazione completata!")
    print("📁 Nuova struttura creata in /barflow")
    print("⚠️  Ricorda di aggiornare gli import nei file UI")

if __name__ == "__main__":
    migrate_project()