# AccountFlow - Gestione Finanziaria per Bar e Ristoranti

**Versione 1.0.0** | **Stato: Pronta per Distribuzione**

AccountFlow è un'applicazione desktop sviluppata per aiutare i proprietari di bar e ristoranti a centralizzare, analizzare e ottenere insights dai propri dati finanziari. L'applicazione offre un'interfaccia utente moderna e intuitiva basata su PySide6, visualizzazioni interattive con Plotly, un database SQLite integrato per archiviare dati flessibili (tramite campi JSON) da diverse fonti (esportazioni POS, fatture digitali, inserimento manuale) e un motore di parsing intelligente (Pandas per Excel, lxml per XML) supportato da un wizard di mapping user-friendly.

## 🚀 Caratteristiche Principali

✅ **Implementato e Funzionante:**
- ✅ Interfaccia moderna con PySide6
- ✅ Dashboard interattiva con metriche chiave
- ✅ Gestione completa delle transazioni
- ✅ Import intelligente da file Excel con mapping automatico
- ✅ Database SQLite con supporto JSON per metadati
- ✅ Sistema di categorie personalizzabili (Bevande, Cibo, Personale)
- ✅ Calcolo automatico di profitto lordo e netto
- ✅ Export report in Excel con grafici
- ✅ Verifica coerenza granularità dati
- ✅ Supporto per importi sempre positivi con campo tipo entrata/uscita
- ✅ Gestione periodo di default (ultimo mese chiuso)
- ✅ Interfaccia completamente in italiano
- ✅ Gestione duplicati con opzioni multiple (skip, update, duplicate)
- ✅ Sistema di configurazione avanzato

## 🛠️ Requisiti Tecnici

### Requisiti di Sistema
- **Sistema Operativo**: Windows 10/11 (testato), macOS, Linux
- **Python**: 3.8 o superiore
- **Memoria RAM**: Minimo 4GB (consigliato 8GB)
- **Spazio Disco**: 500MB per l'applicazione + spazio per database

### Dipendenze Python
```
PySide6>=6.5.0          # Framework GUI
plotly>=5.15.0          # Visualizzazioni interattive
pandas>=2.0.0           # Elaborazione dati
openpyxl>=3.1.0         # Gestione file Excel
xlsxwriter>=3.1.0       # Export Excel avanzato
lxml>=4.9.0             # Parsing XML
pyinstaller>=5.13.0     # Packaging per distribuzione
```

## 📦 Installazione e Avvio

### Distribuzione su iPad / iOS
L'applicazione può essere preparata anche per dispositivi iPad tramite packaging iOS, ma la distribuzione reale su iPad non avviene come un semplice installer Windows.

Per Apple, il percorso consigliato è uno di questi:
- **TestFlight** per test interni o beta;
- **App Store** per distribuzione pubblica;
- **Distribuzione ad hoc** solo con provisioning Apple dedicato.

Per preparare il build iOS locale, il progetto include ora una configurazione dedicata nel file [pyproject.toml](pyproject.toml) e uno script di supporto in [installer/build_ios.sh](installer/build_ios.sh).

### Metodo 1: Avvio Automatico con uv (Consigliato)
1. **Installa uv** (se non già presente):
   ```bash
   # Windows PowerShell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # O tramite pip
   pip install uv
   ```

2. **Scarica il progetto** nella cartella desiderata
3. **Doppio click** su `start_barflow.bat`
4. Il sistema sincronizzerà automaticamente le dipendenze
5. Al primo avvio, scegli se creare dati di esempio

### Metodo 2: Avvio Manuale con uv
```bash
# 1. Naviga nella cartella del progetto
cd AccountFlow

# 2. Sincronizza dipendenze
uv sync

# 3. Avvia l'applicazione
uv run python main.py

# Opzionale: Crea dati di esempio
uv run python main.py --sample-data
```

### Metodo 3: Installazione Manuale Python tradizionale
```bash
# Se uv non è disponibile, usa Python tradizionale
cd AccountFlow

# Crea ambiente virtuale
python -m venv .venv

# Attiva ambiente virtuale
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Installa il progetto
pip install -e .

# Avvia l'applicazione
python main.py
```

## 💼 Struttura dell'Applicazione

```
AccountFlow/
├── main.py                 # File principale per avviare l'applicazione
├── start_barflow.bat      # Script di avvio automatico per Windows
├── requirements.txt       # Dipendenze Python
├── README.md             # Documentazione
├── pyproject.toml        # Configurazione progetto
└── src/                  # Codice sorgente principale
    ├── ui/               # Interfaccia utente
    │   ├── main_window.py           # Finestra principale
    │   ├── dashboard_metrics_widget.py  # Widget metriche numeriche
    │   ├── dashboard_charts_widget.py   # Widget grafici e visualizzazioni
    │   ├── transactions_widget.py   # Gestione transazioni
    │   ├── import_widget.py         # Wizard importazione
    │   ├── reports_widget.py        # Generazione report
    │   └── settings_widget.py       # Configurazioni
    ├── database/         # Gestione database
    │   └── database_manager.py      # Manager SQLite
    ├── parsers/          # Parsing file
    │   └── file_parser.py           # Parser Excel/XML
    ├── reports/          # Generazione report
    │   └── report_generator.py      # Engine report
    └── utils/            # Utilità comuni
        └── common_utils.py          # Validazione, formattazione, ecc.
```

## 🎯 Funzionalità Dettagliate

### 📊 Dashboard
- **Metriche finanziarie in tempo reale**: Entrate, spese, profitto lordo/netto
- **Grafici interattivi**: Torte per categorie, trend temporali, confronti
- **Periodo personalizzabile**: Default ultimo mese chiuso, filtri flessibili
- **Indicatori performance**: Margini, media transazioni, trend
- **Cards animate**: Visualizzazione immediata dei KPI principali

### 💰 Gestione Transazioni
- **CRUD completo**: Aggiungi, modifica, elimina transazioni
- **Filtri avanzati**: Per data, categoria, tipo, ricerca testo
- **Validazione dati**: Controlli automatici su date e importi
- **Import/Export**: Da/verso Excel con mantenimento metadati
- **Categorizzazione intelligente**: Sistema categorie con COGS

### 📁 Import Dati
- **Wizard guidato**: Processo step-by-step per import file
- **Mapping automatico**: Rilevamento intelligente colonne
- **Anteprima dati**: Visualizzazione prima dell'import finale
- **Profili riutilizzabili**: Salva mapping per import futuri
- **Gestione duplicati**: Skip, update, duplicate con scelta utente
- **Verifica coerenza**: Controllo granularità temporale

### 📈 Report e Analisi
- **Report Excel completi**: Con grafici, tabelle, analisi
- **Confronti mensili**: Trend performance nel tempo
- **Analisi categorie**: Breakdown dettagliato spese/entrate
- **Export personalizzabili**: Scegli cosa includere nel report
- **Grafici interattivi**: Plotly per visualizzazioni avanzate

### ⚙️ Configurazioni
- **Impostazioni personalizzabili**: Valuta, formati, comportamenti
- **Backup/Restore**: Gestione sicurezza dati
- **Gestione database**: Ottimizzazione e manutenzione
- **Interfaccia adattabile**: Temi, dimensioni, preferenze
- **Logging avanzato**: Per debugging e supporto

## 🔒 Sicurezza e Privacy

- **Dati locali**: Tutto rimane sul computer dell'utente
- **Database crittografato**: SQLite con protezioni
- **Backup automatici**: Salvataggio periodico dati
- **Validazione input**: Controlli rigorosi sui dati
- **Log audit**: Tracciamento operazioni per debug

### Log e Debugging
- Log salvati in: `%LOCALAPPDATA%\AccountFlow\logs\`
- Database in: `%LOCALAPPDATA%\AccountFlow\barflow.db`
- Configurazioni: `%LOCALAPPDATA%\AccountFlow\config.json`

## 📄 Licenza e Credits

**Autore**: AccountFlow Team  
**Versione**: 1.0.0  
**Data**: Ottobre 2025  
**Licenza**: Proprietaria  

**Tecnologie utilizzate**:
- PySide6 (Qt for Python)
- Plotly (Visualizzazioni)
- Pandas (Data processing)
- SQLite (Database)
- PyInstaller (Packaging)

---

**🎉 AccountFlow è pronto per essere testato e utilizzato in ambiente di produzione!**

Per domande o supporto, contattare il team di sviluppo.
