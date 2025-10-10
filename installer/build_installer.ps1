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

# Copia l'icona personalizzata nella directory di build
Write-Host "🎨 Aggiornamento icona applicazione..." -ForegroundColor Yellow
$IconSource = "barflow\resources\icons\icon.ico"
$IconDestination = "build\barflow\windows\app\icon.ico"
if (Test-Path $IconSource) {
    Copy-Item -Path $IconSource -Destination $IconDestination -Force
    Write-Host "✅ Icona personalizzata applicata: $IconDestination" -ForegroundColor Green
} else {
    Write-Host "⚠️  Icona sorgente non trovata: $IconSource" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[5/6] Aggiunta collegamento desktop..." -ForegroundColor Yellow

# Modifica il file WiX per aggiungere il desktop shortcut
$WixFile = "build\barflow\windows\app\barflow.wxs"
if (Test-Path $WixFile) {
    Write-Host "🔧 Aggiunta desktop shortcut al file WiX..." -ForegroundColor Yellow
    
    # Leggi il contenuto del file
    $WixContent = Get-Content $WixFile -Raw
    
    # Crea il desktop shortcut XML da inserire dopo ProgramMenuFolder
    $DesktopShortcut = @"

        <StandardDirectory Id="DesktopFolder">
            <Component Id="DesktopShortcuts">
                <Shortcut
                    Id="DesktopShortcut1"
                    Name="AccountFlow"
                    Icon="ProductIcon"
                    Description="AccountFlow - Gestione Finanziaria"
                    Target="[INSTALLFOLDER]AccountFlow - Gestione Finanziaria.exe" />
                <RegistryValue
                    Root="HKMU"
                    Key="Software\Andrea Frattini\AccountFlow - Gestione Finanziaria"
                    Name="desktop_shortcut"
                    Type="integer"
                    Value="1"
                    KeyPath="yes" />
            </Component>
        </StandardDirectory>
"@
    
    # Cerca il pattern dopo la chiusura di ProgramMenuFolder
    $ProgramMenuEndPattern = "</StandardDirectory>\s*\s*<Feature"
    if ($WixContent -match $ProgramMenuEndPattern) {
        $WixContent = $WixContent -replace $ProgramMenuEndPattern, ("</StandardDirectory>" + $DesktopShortcut + "`r`n`r`n        <Feature")
        
        # Aggiungi il riferimento al componente nella Feature
        $FeaturePattern = '            <ComponentRef Id="ApplicationShortcuts" />'
        $DesktopComponentRef = $FeaturePattern + "`r`n            <ComponentRef Id=""DesktopShortcuts"" />"
        $WixContent = $WixContent -replace [regex]::Escape($FeaturePattern), $DesktopComponentRef
        
        # Salva il file modificato
        $WixContent | Set-Content $WixFile -Encoding UTF8
        Write-Host "✅ Desktop shortcut aggiunto al file WiX" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Pattern non trovato nel file WiX - shortcut desktop non aggiunto" -ForegroundColor Yellow
        Write-Host "📄 Debug: cerca pattern di chiusura:" -ForegroundColor Gray
        $WixContent -split "`n" | Where-Object { $_ -match "</StandardDirectory>|<Feature" } | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkGray }
    }
}
Write-Host ""

Write-Host "[6/7] Creazione package MSI..." -ForegroundColor Yellow
briefcase package --adhoc-sign
Write-Host ""

Write-Host "[7/7] Build completato!" -ForegroundColor Green
Write-Host ""
Write-Host "Il tuo installer e' disponibile in: dist\AccountFlow - Gestione Finanziaria-1.0.0.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ L'installer crea automaticamente:" -ForegroundColor Green
Write-Host "   • Collegamento nel menu Start con icona" -ForegroundColor Gray
Write-Host "   • Collegamento sul desktop con icona" -ForegroundColor Gray
Write-Host ""

Read-Host "Premi Enter per continuare"