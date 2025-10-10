"""
Utility per la gestione dei percorsi dell'applicazione.
Garantisce che tutti i percorsi siano relativi alla directory di installazione dell'applicazione
o utilizzino directory dati utente appropriate quando necessario.
"""
import sys
import os
from pathlib import Path


def is_frozen_app() -> bool:
    """Determina se l'applicazione è stata impacchettata (frozen)"""
    # Controlli standard per applicazioni frozen
    if getattr(sys, 'frozen', False):
        return True
    
    # Controllo aggiuntivo per applicazioni Briefcase
    # Briefcase spesso mette l'applicazione in una struttura specifica
    executable_path = Path(sys.executable)
    
    # Se l'eseguibile è in una directory che contiene "app" nel percorso
    # e il nome dell'eseguibile è simile al nome dell'app, probabilmente è una app distribuita
    if ('app' in str(executable_path).lower() and 
        executable_path.suffix.lower() in ['.exe', ''] and
        'python' not in executable_path.name.lower()):
        return True
    
    return False


def is_writable_directory(path: Path) -> bool:
    """Verifica se una directory è scrivibile"""
    try:
        test_file = path / "test_write_permissions.tmp"
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError):
        return False


def get_application_directory() -> Path:
    """
    Ottiene la directory base dell'applicazione.
    
    Funziona sia in ambiente di sviluppo che in applicazione distribuita.
    """
    if is_frozen_app():
        # L'applicazione è stata impacchettata (es. con PyInstaller, Briefcase, etc.)
        executable_path = Path(sys.executable)
        
        # Per applicazioni Briefcase/MSI, l'eseguibile può essere in una sottodirectory
        # Cerca la directory principale dell'applicazione
        current_dir = executable_path.parent
        
        # Controlla se siamo in una struttura Briefcase tipica
        if current_dir.name in ['app', 'bin', 'Scripts']:
            # Sali di un livello per trovare la directory principale
            current_dir = current_dir.parent
        
        return current_dir
    else:
        # L'applicazione è in esecuzione in ambiente di sviluppo
        # Cerca main.py partendo dalla directory corrente
        current_dir = Path(__file__).parent
        
        # Naviga verso l'alto fino a trovare main.py o la directory barflow
        while current_dir.parent != current_dir:  # Non siamo alla radice del filesystem
            if (current_dir / 'main.py').exists():
                return current_dir
            elif current_dir.name == 'barflow' and (current_dir.parent / 'main.py').exists():
                return current_dir.parent
            current_dir = current_dir.parent
        
        # Fallback: usa la directory contenente questo file
        return Path(__file__).parent.parent.parent


def get_user_data_directory() -> Path:
    """
    Ottiene la directory dati utente appropriata per il sistema operativo.
    Questa è sempre scrivibile dall'utente corrente.
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    elif sys.platform == 'darwin':  # macOS
        base_dir = Path.home() / 'Library' / 'Application Support'
    else:  # Linux e altri Unix
        base_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    
    app_data_dir = base_dir / "AccountFlow"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir


def get_data_directory() -> Path:
    """
    Ottiene la directory per i dati dell'applicazione.
    
    Prova prima la directory dell'applicazione (per portabilità),
    poi fallback alla directory dati utente se non scrivibile.
    """
    # Prima prova la directory dell'applicazione (autocontenuta)
    app_dir = get_application_directory()
    data_dir = app_dir / "historical_data"
    
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        if is_writable_directory(data_dir):
            return data_dir
    except (PermissionError, OSError):
        pass
    
    # Fallback alla directory dati utente
    user_data_dir = get_user_data_directory()
    data_dir = user_data_dir / "historical_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_app_data_directory() -> Path:
    """
    Ottiene la directory per i dati persistenti dell'applicazione.
    
    Prova prima la directory dell'applicazione (per portabilità),
    poi fallback alla directory dati utente se non scrivibile.
    """
    # Prima prova la directory dell'applicazione (autocontenuta)
    app_dir = get_application_directory()
    app_data_dir = app_dir / "app_data"
    
    try:
        app_data_dir.mkdir(parents=True, exist_ok=True)
        if is_writable_directory(app_data_dir):
            return app_data_dir
    except (PermissionError, OSError):
        pass
    
    # Fallback alla directory dati utente
    user_data_dir = get_user_data_directory()
    app_data_dir = user_data_dir / "app_data"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir


def get_resources_directory() -> Path:
    """
    Ottiene la directory delle risorse dell'applicazione.
    Questa è sempre relativa alla directory di installazione.
    """
    app_dir = get_application_directory()
    
    # Possibili percorsi per le risorse in base alla struttura di packaging
    possible_resource_paths = [
        app_dir / "barflow" / "resources",  # Sviluppo
        app_dir / "resources",  # Packaging alternativo
        app_dir / "src" / "app" / "barflow" / "resources",  # Briefcase
        app_dir / "app" / "barflow" / "resources",  # Briefcase alternativo
        app_dir / "Contents" / "Resources" / "app" / "barflow" / "resources",  # macOS Bundle
    ]
    
    for resources_dir in possible_resource_paths:
        if resources_dir.exists():
            return resources_dir
    
    # Fallback: restituisce il primo percorso anche se non esiste
    # In questo caso stampa un warning per debug
    print(f"⚠️  Warning: Directory risorse non trovata. Percorsi tentati:")
    for path in possible_resource_paths:
        print(f"   - {path} (exists: {path.exists()})")
    
    return possible_resource_paths[0]


def get_output_directory() -> Path:
    """
    Ottiene la directory per i file di output dell'applicazione.
    
    Prova prima la directory dell'applicazione, poi fallback alla directory dati utente.
    """
    # Prima prova la directory dell'applicazione
    app_dir = get_application_directory()
    output_dir = app_dir / "output_data"
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if is_writable_directory(output_dir):
            return output_dir
    except (PermissionError, OSError):
        pass
    
    # Fallback alla directory dati utente
    user_data_dir = get_user_data_directory()
    output_dir = user_data_dir / "output_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_temp_directory() -> Path:
    """
    Ottiene la directory per i file temporanei dell'applicazione.
    
    Utilizza sempre la directory temporanea del sistema per i file temporanei.
    """
    import tempfile
    temp_base = Path(tempfile.gettempdir())
    temp_dir = temp_base / "AccountFlow"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir