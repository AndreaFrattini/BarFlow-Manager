@echo off
echo ===============================================
echo   AccountFlow - Launcher Build Script
echo ===============================================
echo.

REM Verifica esistenza del file PowerShell
if not exist "%~dp0build_installer.ps1" (
    echo ERRORE: File build_installer.ps1 non trovato!
    pause
    exit /b 1
)

REM Verifica esistenza ambiente virtuale
if not exist "%~dp0..\.venv\Scripts\Activate.ps1" (
    echo ERRORE: Ambiente virtuale .venv non trovato!
    echo Assicurati di aver creato l'ambiente virtuale con: python -m venv .venv
    pause
    exit /b 1
)

echo Avvio build script PowerShell...
echo.

REM Esegui lo script PowerShell
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0build_installer.ps1"

if %errorLevel% == 0 (
    echo.
    echo Build completato con successo.
) else (
    echo.
    echo ERRORE: Il build ha riscontrato problemi.
)

pause
