"""
Utilità comuni per l'applicazione BarFlow
"""
import hashlib
import os
from typing import List, Tuple, Optional
from datetime import datetime
import re


class ValidationUtils:
    """Utilità per la validazione dei dati"""
    
    @staticmethod
    def validate_date(date_string: str) -> bool:
        """
        Valida se una stringa è una data valida
        
        Args:
            date_string: Stringa da validare
            
        Returns:
            True se valida, False altrimenti
        """
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_amount(amount) -> bool:
        """
        Valida se un valore è un importo numerico valido
        
        Args:
            amount: Valore da validare
            
        Returns:
            True se valido, False altrimenti
        """
        try:
            float_val = float(amount)
            return float_val >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Rimuove caratteri non validi da un nome file
        
        Args:
            filename: Nome file da sanitizzare
            
        Returns:
            Nome file sanitizzato
        """
        # Rimuovi caratteri non validi per Windows
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Rimuovi spazi multipli e caratteri di controllo
        filename = re.sub(r'\s+', ' ', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        return filename.strip()


class FileUtils:
    """Utilità per la gestione dei file"""
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """
        Calcola l'hash MD5 di un file
        
        Args:
            file_path: Percorso del file
            
        Returns:
            Hash MD5 del file
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return ""
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Ottiene la dimensione di un file in bytes
        
        Args:
            file_path: Percorso del file
            
        Returns:
            Dimensione in bytes
        """
        try:
            return os.path.getsize(file_path)
        except (IOError, OSError):
            return 0
    
    @staticmethod
    def is_file_accessible(file_path: str) -> bool:
        """
        Verifica se un file è accessibile
        
        Args:
            file_path: Percorso del file
            
        Returns:
            True se accessibile, False altrimenti
        """
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
            return True
        except (IOError, OSError, PermissionError):
            return False
    
    @staticmethod
    def get_safe_file_path(directory: str, filename: str) -> str:
        """
        Genera un percorso file sicuro evitando sovrascritture
        
        Args:
            directory: Directory di destinazione
            filename: Nome file desiderato
            
        Returns:
            Percorso file sicuro
        """
        base_name, ext = os.path.splitext(filename)
        counter = 1
        
        file_path = os.path.join(directory, filename)
        
        while os.path.exists(file_path):
            new_filename = f"{base_name}_{counter}{ext}"
            file_path = os.path.join(directory, new_filename)
            counter += 1
        
        return file_path


class FormatUtils:
    """Utilità per la formattazione"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "€") -> str:
        """
        Formatta un importo come valuta
        
        Args:
            amount: Importo da formattare
            currency: Simbolo valuta
            
        Returns:
            Stringa formattata
        """
        return f"{currency}{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Formatta un valore come percentuale
        
        Args:
            value: Valore da formattare (es. 0.15 per 15%)
            decimals: Numero di decimali
            
        Returns:
            Stringa formattata
        """
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_date_italian(date_string: str) -> str:
        """
        Formatta una data in formato italiano
        
        Args:
            date_string: Data in formato YYYY-MM-DD
            
        Returns:
            Data in formato DD/MM/YYYY
        """
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            return date_string
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formatta una dimensione file in formato leggibile
        
        Args:
            size_bytes: Dimensione in bytes
            
        Returns:
            Stringa formattata (es. "1.5 MB")
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


class MessageUtils:
    """Utilità per i messaggi utente"""
    
    ERROR_MESSAGES = {
        'file_not_found': 'File non trovato: {filename}',
        'file_not_accessible': 'Impossibile accedere al file: {filename}',
        'invalid_file_format': 'Formato file non supportato: {filename}',
        'duplicate_file': 'File già importato: {filename}',
        'empty_file': 'Il file è vuoto: {filename}',
        'invalid_data': 'Dati non validi rilevati nel file',
        'granularity_mismatch': 'I dati hanno granularità temporali diverse. Non è possibile continuare.',
        'database_error': 'Errore nel database: {error}',
        'export_error': 'Errore durante l\'esportazione: {error}',
        'import_error': 'Errore durante l\'importazione: {error}',
        'validation_error': 'Errore di validazione: {error}'
    }
    
    SUCCESS_MESSAGES = {
        'file_imported': 'File importato con successo: {count} transazioni aggiunte',
        'data_exported': 'Dati esportati con successo in: {filename}',
        'transaction_added': 'Transazione aggiunta con successo',
        'transaction_updated': 'Transazione aggiornata con successo',
        'transaction_deleted': 'Transazione eliminata con successo',
        'category_added': 'Categoria aggiunta con successo',
        'profile_saved': 'Profilo di importazione salvato con successo'
    }
    
    @classmethod
    def get_error_message(cls, key: str, **kwargs) -> str:
        """
        Ottiene un messaggio di errore formattato
        
        Args:
            key: Chiave del messaggio
            **kwargs: Parametri per la formattazione
            
        Returns:
            Messaggio formattato
        """
        message = cls.ERROR_MESSAGES.get(key, f'Errore sconosciuto: {key}')
        return message.format(**kwargs)
    
    @classmethod
    def get_success_message(cls, key: str, **kwargs) -> str:
        """
        Ottiene un messaggio di successo formattato
        
        Args:
            key: Chiave del messaggio
            **kwargs: Parametri per la formattazione
            
        Returns:
            Messaggio formattato
        """
        message = cls.SUCCESS_MESSAGES.get(key, f'Successo: {key}')
        return message.format(**kwargs)


class ConfigUtils:
    """Utilità per la configurazione dell'applicazione"""
    
    DEFAULT_CONFIG = {
        'database_path': None,  # Usa default se None
        'default_currency': 'EUR',
        'date_format': 'DD/MM/YYYY',
        'decimal_separator': ',',
        'thousands_separator': '.',
        'default_granularity': 'monthly',
        'auto_backup': True,
        'backup_frequency': 'weekly',
        'export_format': 'xlsx',
        'language': 'it',
        'theme': 'default'
    }
    
    @classmethod
    def get_app_data_dir(cls) -> str:
        """
        Ottiene la directory dei dati dell'applicazione
        
        Returns:
            Percorso della directory
        """
        from pathlib import Path
        
        app_data_dir = Path.home() / "AppData" / "Local" / "BarFlow"
        app_data_dir.mkdir(parents=True, exist_ok=True)
        
        return str(app_data_dir)
    
    @classmethod
    def get_config_file_path(cls) -> str:
        """
        Ottiene il percorso del file di configurazione
        
        Returns:
            Percorso del file config.json
        """
        return os.path.join(cls.get_app_data_dir(), "config.json")
    
    @classmethod
    def load_config(cls) -> dict:
        """
        Carica la configurazione dal file
        
        Returns:
            Dizionario con la configurazione
        """
        import json
        
        config_file = cls.get_config_file_path()
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Merge con configurazione di default
                config = cls.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
                
            except (json.JSONDecodeError, IOError):
                pass
        
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save_config(cls, config: dict) -> bool:
        """
        Salva la configurazione nel file
        
        Args:
            config: Dizionario con la configurazione
            
        Returns:
            True se salvata con successo
        """
        import json
        
        try:
            config_file = cls.get_config_file_path()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (IOError, OSError):
            return False


class DataConsistencyChecker:
    """Controlli di coerenza dei dati"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def check_granularity_consistency(self) -> Tuple[bool, List[str], str]:
        """
        Verifica la coerenza della granularità dei dati
        
        Returns:
            Tupla (is_consistent, granularities_found, error_message)
        """
        is_consistent, granularities = self.db_manager.check_data_granularity_consistency()
        
        if not is_consistent:
            error_msg = f"Rilevate granularità temporali diverse: {', '.join(granularities)}. "
            error_msg += "Per continuare, tutti i dati devono avere la stessa granularità "
            error_msg += "(giornaliera, settimanale o mensile)."
            
            return False, granularities, error_msg
        
        return True, granularities, ""
    
    def check_date_ranges(self) -> Tuple[bool, str]:
        """
        Verifica che i range di date siano ragionevoli
        
        Returns:
            Tupla (is_valid, error_message)
        """
        transactions = self.db_manager.get_transactions()
        
        if not transactions:
            return True, ""
        
        dates = [datetime.strptime(t['transaction_date'], '%Y-%m-%d') for t in transactions]
        min_date = min(dates)
        max_date = max(dates)
        
        # Verifica che le date non siano troppo nel futuro
        if max_date > datetime.now():
            return False, "Rilevate transazioni con date future"
        
        # Verifica che le date non siano troppo nel passato (oltre 10 anni)
        ten_years_ago = datetime.now().replace(year=datetime.now().year - 10)
        if min_date < ten_years_ago:
            return False, "Rilevate transazioni con date troppo vecchie (oltre 10 anni)"
        
        return True, ""
    
    def check_amounts_validity(self) -> Tuple[bool, str]:
        """
        Verifica la validità degli importi
        
        Returns:
            Tupla (is_valid, error_message)
        """
        transactions = self.db_manager.get_transactions()
        
        if not transactions:
            return True, ""
        
        # Verifica importi negativi o zero
        invalid_amounts = [t for t in transactions if t['amount'] <= 0]
        if invalid_amounts:
            return False, f"Rilevate {len(invalid_amounts)} transazioni con importi non validi (≤ 0)"
        
        # Verifica importi eccessivamente alti (oltre 1 milione)
        high_amounts = [t for t in transactions if t['amount'] > 1000000]
        if high_amounts:
            return False, f"Rilevate {len(high_amounts)} transazioni con importi eccessivamente alti (> €1.000.000)"
        
        return True, ""