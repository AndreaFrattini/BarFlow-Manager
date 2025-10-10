@echo off
setlocal enabledelayedexpansion
echo ===============================================
echo   AccountFlow - Disinstallazione Automatica
echo ===============================================
echo.

REM Verifica se lo script è eseguito come amministratore
fsutil dirty query %systemdrive% >nul 2>&1
if !errorLevel! == 0 (
    echo Privilegi di amministratore confermati.
    goto :run_uninstall
) else (
    echo Richiesti privilegi di amministratore...
    echo Riavvio automatico come amministratore...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b 0
)

:run_uninstall
echo.
echo Controllo presenza file PowerShell...

REM Verifica esistenza del file PowerShell
if not exist "%~dp0uninstall_accountflow.ps1" (
    echo ERRORE: File uninstall_accountflow.ps1 non trovato!
    echo Percorso cercato: %~dp0uninstall_accountflow.ps1
    goto :error_exit
)

echo File PowerShell trovato. Avvio disinstallazione...
echo.

REM Esegui lo script PowerShell con gestione errori
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0uninstall_accountflow.ps1"

if !errorLevel! == 0 (
    echo.
    echo Disinstallazione completata con successo.
) else (
    echo.
    echo ERRORE: La disinstallazione ha riscontrato problemi.
    echo Codice di errore: !errorLevel!
)

goto :end

:error_exit
echo.
echo La disinstallazione non può continuare.
pause
exit /b 1

:end
echo.
pause
exit /b 0