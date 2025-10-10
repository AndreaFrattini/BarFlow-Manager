# Build Script per AccountFlow
Write-Host "===============================================" -ForegroundColor Green
Write-Host "    AccountFlow - Build Script Automatico" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Attiva l'ambiente virtuale
& .\.venv\Scripts\Activate.ps1

Write-Host "[1/4] Pulizia build precedenti..." -ForegroundColor Yellow
briefcase package --clean
Write-Host ""

Write-Host "[2/4] Aggiornamento codice applicazione..." -ForegroundColor Yellow
briefcase update
Write-Host ""

Write-Host "[3/4] Creazione package MSI..." -ForegroundColor Yellow
briefcase package
Write-Host ""

Write-Host "[4/4] Build completato!" -ForegroundColor Green
Write-Host ""
Write-Host "Il tuo installer e' disponibile in: dist\AccountFlow - Gestione Finanziaria-1.0.0.msi" -ForegroundColor Cyan
Write-Host ""

Read-Host "Premi Enter per continuare"