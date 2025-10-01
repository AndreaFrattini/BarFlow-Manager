@echo off
echo ========================================
echo        BarFlow - Avvio Applicazione
echo ========================================
echo.

REM Verifica se uv è installato
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRORE: uv non è installato
    echo Installa uv da: https://docs.astral.sh/uv/getting-started/installation/
    echo.
    echo Alternativamente, verifica se Python è disponibile...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRORE: Né uv né Python sono disponibili
        pause
        exit /b 1
    )
    echo Uso Python tradizionale come fallback...
    goto :python_fallback
)

REM Sincronizza dipendenze con uv
echo Sincronizzazione dipendenze con uv...
uv sync

REM Controlla se è la prima esecuzione
if not exist "src\database_created.flag" (
    echo Prima esecuzione rilevata!
    echo Vuoi creare dati di esempio per testare l'applicazione? [S/N]
    set /p choice="Inserisci S per Sì, N per No: "
    
    if /i "%choice%"=="S" (
        echo Creazione dati di esempio...
        uv run python main.py --sample-data
        echo. > src\database_created.flag
    )
)

echo.
echo Avvio BarFlow con uv...
echo.

REM Avvia l'applicazione con uv
uv run python main.py
goto :end

:python_fallback
REM Fallback per ambiente Python tradizionale
if not exist ".venv" (
    echo Creazione ambiente virtuale...
    python -m venv .venv
)

echo Attivazione ambiente virtuale...
call .venv\Scripts\activate.bat

echo Installazione dipendenze...
pip install -e .

if not exist "src\database_created.flag" (
    echo Prima esecuzione rilevata!
    echo Vuoi creare dati di esempio per testare l'applicazione? [S/N]
    set /p choice="Inserisci S per Sì, N per No: "
    
    if /i "%choice%"=="S" (
        echo Creazione dati di esempio...
        python main.py --sample-data
        echo. > src\database_created.flag
    )
)

echo Avvio BarFlow...
python main.py

:end
REM Mantieni la finestra aperta in caso di errori
if %errorlevel% neq 0 (
    echo.
    echo ERRORE: L'applicazione è terminata con errori
    pause
)