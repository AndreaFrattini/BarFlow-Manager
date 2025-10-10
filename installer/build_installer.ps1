# Build Script per AccountFlow
Write-Host "===============================================" -ForegroundColor Green
Write-Host "    AccountFlow - Build Script Automatico" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Cambia alla directory del progetto (parent directory)
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

# Verifica esistenza ambiente virtuale
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "ERRORE: Ambiente virtuale .venv non trovato!" -ForegroundColor Red
    Write-Host "Assicurati di aver creato l'ambiente virtuale con: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

# Attiva l'ambiente virtuale
Write-Host "Attivazione ambiente virtuale..." -ForegroundColor Gray
& .\.venv\Scripts\Activate.ps1

# Verifica che briefcase sia disponibile
try {
    & briefcase --version | Out-Null
} catch {
    Write-Host "ERRORE: Briefcase non trovato nell'ambiente virtuale!" -ForegroundColor Red
    Write-Host "Installa briefcase con: pip install briefcase" -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

Write-Host "[1/6] Pulizia build precedenti..." -ForegroundColor Yellow
# Rimuovi directory build se esiste
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "Directory build rimossa." -ForegroundColor Gray
}
Write-Host ""

Write-Host "[2/6] Verifica e correzione icona..." -ForegroundColor Yellow
& python fix_icon.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRORE: Impossibile creare l'icona .ico!" -ForegroundColor Red
    Read-Host "Premi Enter per uscire"
    exit 1
}
Write-Host ""

Write-Host "[3/6] Aggiornamento codice applicazione..." -ForegroundColor Yellow
briefcase update
Write-Host ""

Write-Host "[4/6] Build applicazione..." -ForegroundColor Yellow
briefcase build
Write-Host ""

Write-Host "[5/6] Creazione package MSI..." -ForegroundColor Yellow
briefcase package --adhoc-sign
Write-Host ""

Write-Host "[6/6] Build completato!" -ForegroundColor Green
Write-Host ""
Write-Host "Il tuo installer e' disponibile in: dist\AccountFlow - Gestione Finanziaria-1.0.0.msi" -ForegroundColor Cyan
Write-Host ""

Read-Host "Premi Enter per continuare"