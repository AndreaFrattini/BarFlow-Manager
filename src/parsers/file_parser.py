"""
Modulo per il parsing dei file Excel e XML
"""
import pandas as pd
import numpy as np
from lxml import etree
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re


class FileParser:
    """Classe base per il parsing dei file"""
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Calcola l'hash MD5 di un file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def detect_date_format(date_string: str) -> Optional[str]:
        """
        Rileva il formato di una data
        
        Args:
            date_string: Stringa contenente la data
            
        Returns:
            Formato della data o None se non rilevato
        """
        common_formats = [
            '%Y-%m-%d',      # 2023-12-31
            '%d/%m/%Y',      # 31/12/2023
            '%m/%d/%Y',      # 12/31/2023
            '%d-%m-%Y',      # 31-12-2023
            '%Y/%m/%d',      # 2023/12/31
            '%d.%m.%Y',      # 31.12.2023
            '%Y%m%d'         # 20231231
        ]
        
        for fmt in common_formats:
            try:
                datetime.strptime(str(date_string), fmt)
                return fmt
            except (ValueError, TypeError):
                continue
        
        return None
    
    @staticmethod
    def parse_amount(amount_str: str) -> Optional[float]:
        """
        Converte una stringa in importo numerico
        
        Args:
            amount_str: Stringa contenente l'importo
            
        Returns:
            Valore numerico o None se non convertibile
        """
        if pd.isna(amount_str) or amount_str == '':
            return None
        
        # Rimuovi spazi e caratteri comuni
        amount_str = str(amount_str).strip()
        
        # Rimuovi simboli di valuta comuni
        amount_str = re.sub(r'[€$£¥₹]', '', amount_str)
        
        # Gestisci separatori decimali (virgola vs punto)
        # Se ci sono sia virgole che punti, assume che l'ultimo sia il decimale
        if ',' in amount_str and '.' in amount_str:
            # Formato: 1.234,56 o 1,234.56
            if amount_str.rfind(',') > amount_str.rfind('.'):
                # L'ultima virgola è il decimale: 1.234,56
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                # L'ultimo punto è il decimale: 1,234.56
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Solo virgole - potrebbero essere migliaia o decimali
            # Se ci sono più di 2 cifre dopo l'ultima virgola, probabilmente è per migliaia
            parts = amount_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Probabilmente decimale: 123,45
                amount_str = amount_str.replace(',', '.')
            else:
                # Probabilmente migliaia: 1,234,567
                amount_str = amount_str.replace(',', '')
        
        # Rimuovi altri caratteri non numerici tranne punto e segno meno
        amount_str = re.sub(r'[^\d.-]', '', amount_str)
        
        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return None


class ExcelParser(FileParser):
    """Parser per file Excel"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_hash = self.get_file_hash(file_path)
        self._df = None
        self._sheets = None
    
    def get_sheets(self) -> List[str]:
        """Ottiene la lista dei fogli nel file Excel"""
        if self._sheets is None:
            try:
                excel_file = pd.ExcelFile(self.file_path)
                self._sheets = excel_file.sheet_names
            except Exception as e:
                raise ValueError(f"Errore nell'apertura del file Excel: {str(e)}")
        return self._sheets
    
    def load_sheet(self, sheet_name: str = None, header_row: int = 0) -> pd.DataFrame:
        """
        Carica un foglio Excel
        
        Args:
            sheet_name: Nome del foglio (se None, carica il primo)
            header_row: Riga dell'intestazione (0-based)
            
        Returns:
            DataFrame con i dati del foglio
        """
        try:
            if sheet_name is None:
                sheet_name = self.get_sheets()[0]
            
            self._df = pd.read_excel(
                self.file_path, 
                sheet_name=sheet_name, 
                header=header_row,
                engine='openpyxl'
            )
            
            # Pulisci i nomi delle colonne
            self._df.columns = [str(col).strip() for col in self._df.columns]
            
            return self._df
            
        except Exception as e:
            raise ValueError(f"Errore nel caricamento del foglio '{sheet_name}': {str(e)}")
    
    def get_preview_data(self, max_rows: int = 10) -> Dict[str, Any]:
        """
        Ottiene un'anteprima dei dati
        
        Args:
            max_rows: Numero massimo di righe da mostrare
            
        Returns:
            Dizionario con informazioni di anteprima
        """
        if self._df is None:
            raise ValueError("Nessun foglio caricato. Usa load_sheet() prima.")
        
        preview_df = self._df.head(max_rows)
        
        return {
            'columns': list(self._df.columns),
            'data': preview_df.to_dict('records'),
            'total_rows': len(self._df),
            'sample_data': self._get_column_samples()
        }
    
    def _get_column_samples(self) -> Dict[str, List[str]]:
        """Ottiene campioni di dati per ogni colonna"""
        samples = {}
        for col in self._df.columns:
            # Prendi i primi 5 valori non nulli
            non_null_values = self._df[col].dropna().head(5)
            samples[col] = [str(val) for val in non_null_values.tolist()]
        return samples
    
    def suggest_column_mapping(self) -> Dict[str, str]:
        """
        Suggerisce una mappatura automatica delle colonne
        
        Returns:
            Dizionario con suggerimenti di mappatura
        """
        if self._df is None:
            raise ValueError("Nessun foglio caricato. Usa load_sheet() prima.")
        
        suggestions = {}
        columns = [col.lower() for col in self._df.columns]
        
        # Mappature comuni per POS
        date_keywords = ['data', 'date', 'giorno', 'day', 'periodo']
        description_keywords = ['descrizione', 'description', 'dettaglio', 'detail', 'prodotto', 'item']
        amount_keywords = ['importo', 'amount', 'totale', 'total', 'prezzo', 'price', 'valore', 'value']
        income_keywords = ['entrata', 'income', 'ricavo', 'revenue', 'vendita', 'sale']
        expense_keywords = ['uscita', 'expense', 'spesa', 'cost', 'costo']
        
        for i, col in enumerate(self._df.columns):
            col_lower = col.lower()
            
            # Cerca corrispondenze per data
            if any(keyword in col_lower for keyword in date_keywords):
                suggestions['transaction_date'] = col
            
            # Cerca corrispondenze per descrizione
            elif any(keyword in col_lower for keyword in description_keywords):
                suggestions['description'] = col
            
            # Cerca corrispondenze per importo
            elif any(keyword in col_lower for keyword in amount_keywords):
                suggestions['amount'] = col
            
            # Cerca corrispondenze per tipo (entrata/uscita)
            elif any(keyword in col_lower for keyword in income_keywords):
                suggestions['is_income_indicator'] = col
            elif any(keyword in col_lower for keyword in expense_keywords):
                suggestions['is_expense_indicator'] = col
        
        return suggestions
    
    def parse_with_mapping(self, mapping: Dict[str, str], default_category_id: int = 1) -> List[Dict[str, Any]]:
        """
        Analizza i dati usando la mappatura fornita
        
        Args:
            mapping: Dizionario con la mappatura colonne -> campi
            default_category_id: ID categoria di default
            
        Returns:
            Lista di transazioni pronte per il database
        """
        if self._df is None:
            raise ValueError("Nessun foglio caricato. Usa load_sheet() prima.")
        
        transactions = []
        errors = []
        
        for index, row in self._df.iterrows():
            try:
                transaction = self._parse_row(row, mapping, default_category_id, index)
                if transaction:
                    transactions.append(transaction)
            except Exception as e:
                errors.append(f"Errore riga {index + 1}: {str(e)}")
        
        if errors:
            print(f"Errori durante il parsing: {len(errors)} righe saltate")
            for error in errors[:5]:  # Mostra solo i primi 5 errori
                print(f"  - {error}")
        
        return transactions
    
    def _parse_row(self, row: pd.Series, mapping: Dict[str, str], default_category_id: int, row_index: int) -> Optional[Dict[str, Any]]:
        """Analizza una singola riga"""
        transaction = {}
        metadata = {}
        
        # Data della transazione
        if 'transaction_date' in mapping:
            date_val = row[mapping['transaction_date']]
            if pd.isna(date_val):
                return None
            
            # Prova a convertire la data
            if isinstance(date_val, datetime):
                transaction['transaction_date'] = date_val.strftime('%Y-%m-%d')
            else:
                date_format = self.detect_date_format(str(date_val))
                if date_format:
                    parsed_date = datetime.strptime(str(date_val), date_format)
                    transaction['transaction_date'] = parsed_date.strftime('%Y-%m-%d')
                else:
                    raise ValueError(f"Formato data non riconosciuto: {date_val}")
        else:
            raise ValueError("Mappatura data mancante")
        
        # Descrizione
        if 'description' in mapping:
            desc_val = row[mapping['description']]
            transaction['description'] = str(desc_val) if not pd.isna(desc_val) else f"Transazione riga {row_index + 1}"
        else:
            transaction['description'] = f"Transazione riga {row_index + 1}"
        
        # Importo
        if 'amount' in mapping:
            amount_val = row[mapping['amount']]
            parsed_amount = self.parse_amount(str(amount_val))
            if parsed_amount is None or parsed_amount == 0:
                return None
            transaction['amount'] = abs(parsed_amount)  # Sempre positivo come richiesto
        else:
            raise ValueError("Mappatura importo mancante")
        
        # Determina se è entrata o uscita
        transaction['is_income'] = self._determine_income_type(row, mapping, parsed_amount)
        
        # Categoria (usa quella di default per ora)
        transaction['category_id'] = default_category_id
        
        # Salva tutti gli altri campi in metadata
        for col in row.index:
            if col not in mapping.values() and not pd.isna(row[col]):
                metadata[col] = str(row[col])
        
        if metadata:
            transaction['metadata'] = metadata
        
        return transaction
    
    def _determine_income_type(self, row: pd.Series, mapping: Dict[str, str], amount: float) -> bool:
        """Determina se una transazione è un'entrata o un'uscita"""
        
        # Se c'è un campo specifico per il tipo
        if 'is_income_indicator' in mapping:
            indicator = str(row[mapping['is_income_indicator']]).lower()
            return 'entrata' in indicator or 'income' in indicator or 'ricavo' in indicator
        
        if 'is_expense_indicator' in mapping:
            indicator = str(row[mapping['is_expense_indicator']]).lower()
            return not ('uscita' in indicator or 'expense' in indicator or 'spesa' in indicator)
        
        # Se l'importo originale era negativo, probabilmente è un'uscita
        if amount < 0:
            return False
        
        # Default: considera come entrata (tipico per dati POS)
        return True
    
    def detect_granularity(self) -> str:
        """
        Rileva la granularità dei dati basandosi sulle date
        
        Returns:
            Una tra: 'daily', 'weekly', 'monthly'
        """
        if self._df is None:
            raise ValueError("Nessun foglio caricato. Usa load_sheet() prima.")
        
        # Trova la colonna data
        date_columns = []
        for col in self._df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['data', 'date', 'giorno']):
                date_columns.append(col)
        
        if not date_columns:
            return 'monthly'  # Default
        
        # Analizza la prima colonna data trovata
        date_col = date_columns[0]
        dates = []
        
        for val in self._df[date_col].dropna().head(20):  # Analizza le prime 20 date
            if isinstance(val, datetime):
                dates.append(val)
            else:
                date_format = self.detect_date_format(str(val))
                if date_format:
                    try:
                        parsed_date = datetime.strptime(str(val), date_format)
                        dates.append(parsed_date)
                    except:
                        continue
        
        if len(dates) < 2:
            return 'monthly'
        
        # Calcola le differenze tra date consecutive
        dates.sort()
        differences = []
        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i-1]).days
            differences.append(diff)
        
        avg_diff = sum(differences) / len(differences)
        
        # Classifica in base alla differenza media
        if avg_diff <= 2:
            return 'daily'
        elif avg_diff <= 10:
            return 'weekly'
        else:
            return 'monthly'


class XMLParser(FileParser):
    """Parser per file XML - implementazione base per future estensioni"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_hash = self.get_file_hash(file_path)
        self._tree = None
        self._root = None
    
    def load_xml(self) -> etree._Element:
        """Carica il file XML"""
        try:
            self._tree = etree.parse(self.file_path)
            self._root = self._tree.getroot()
            return self._root
        except Exception as e:
            raise ValueError(f"Errore nell'apertura del file XML: {str(e)}")
    
    def get_structure_preview(self) -> Dict[str, Any]:
        """Ottiene un'anteprima della struttura XML"""
        if self._root is None:
            self.load_xml()
        
        def element_to_dict(element, max_depth=3, current_depth=0):
            if current_depth > max_depth:
                return "..."
            
            result = {}
            if element.text and element.text.strip():
                result['_text'] = element.text.strip()
            
            for child in element[:5]:  # Limita ai primi 5 figli
                child_dict = element_to_dict(child, max_depth, current_depth + 1)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
            
            return result
        
        return {
            'root_tag': self._root.tag,
            'structure': element_to_dict(self._root)
        }