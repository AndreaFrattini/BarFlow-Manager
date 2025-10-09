"""
Utility functions comuni per i widget di analisi
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt

def parse_date_robust(date_str):
    """
    Parsing robusto delle date che supporta diversi formati.
    
    Args:
        date_str: Stringa data da parsare
        
    Returns:
        pd.Timestamp o pd.NaT se il parsing fallisce
    """
    if pd.isna(date_str):
        return pd.NaT
    try:
        # Prova prima con formato datetime completo
        return pd.to_datetime(date_str, format='%Y-%m-%d %H:%M:%S')
    except:
        try:
            # Poi con formato solo data
            return pd.to_datetime(date_str, format='%Y-%m-%d')
        except:
            # Infine lascia che pandas provi a interpretare automaticamente
            return pd.to_datetime(date_str, errors='coerce')

def create_metric_box(title, value, color):
    """
    Crea un box per una metrica specifica con stile uniforme.
    
    Args:
        title: Titolo della metrica
        value: Valore da visualizzare
        color: Colore di sfondo del box
        
    Returns:
        QFrame: Il widget del box della metrica
    """
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setFrameShadow(QFrame.Raised)
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {color};
            border-radius: 10px;
            border: none;
        }}
    """)
    
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(3)
    layout.setAlignment(Qt.AlignCenter)
    
    title_label = QLabel(title)
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setWordWrap(True)
    title_label.setStyleSheet("""
        color: white; 
        font-size: 10px;
        font-weight: bold;
        margin: 0px;
        padding: 2px;
    """)
    
    value_label = QLabel(value)
    value_label.setAlignment(Qt.AlignCenter)
    value_label.setWordWrap(True)
    value_label.setStyleSheet("""
        color: white; 
        font-size: 12px;
        font-weight: bold;
        margin: 0px;
        padding: 2px;
    """)
    value_label.setObjectName("value_label")
    
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    
    return frame

def create_chart_canvas(figsize=(8, 3)):
    """
    Crea un'area di disegno per un grafico Matplotlib con stile moderno uniforme.
    
    Args:
        figsize: Tupla con dimensioni della figura (width, height)
        
    Returns:
        FigureCanvas: Canvas per il grafico matplotlib
    """
    # Imposta lo stile moderno per matplotlib
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        try:
            plt.style.use('seaborn-whitegrid')
        except:
            plt.style.use('default')
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FFFFFF')
    
    # Rimuovi i bordi superiore e destro per un look più pulito
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    canvas = FigureCanvas(fig)
    canvas.setStyleSheet("""
        background-color: #FAFAFA; 
        border-radius: 15px;
        border: 1px solid #E0E0E0;
    """)
    return canvas

def style_empty_chart(ax):
    """
    Applica stile moderno ai grafici vuoti.
    
    Args:
        ax: Asse matplotlib da stilizzare
    """
    # Rimuovi i bordi superiore e destro per un look più pulito
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    # Rimuovi tick e etichette
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')

def prepare_dataframe_for_analysis(transactions_data):
    """
    Prepara un DataFrame dai dati delle transazioni con parsing robusto delle date.
    
    Args:
        transactions_data: Lista di dizionari con i dati delle transazioni
        
    Returns:
        pd.DataFrame: DataFrame pulito e processato, o None se non ci sono dati validi
    """
    if not transactions_data:
        return None
    
    df = pd.DataFrame(transactions_data)
    df['IMPORTO NETTO'] = pd.to_numeric(df['IMPORTO NETTO'], errors='coerce')
    
    # Applica parsing robusto delle date
    df['DATA'] = df['DATA'].apply(parse_date_robust)
    
    # Rimuovi righe con valori non validi
    df = df.dropna(subset=['IMPORTO NETTO', 'DATA'])
    
    return df if len(df) > 0 else None

def update_metric_box_value(metric_box, new_value):
    """
    Aggiorna il valore in un metric box.
    
    Args:
        metric_box: Il QFrame del metric box
        new_value: Il nuovo valore da visualizzare
    """
    value_label = metric_box.findChild(QLabel, "value_label")
    if value_label:
        value_label.setText(new_value)