# Post-Install Script per AccountFlow
# Esegui questo script come Amministratore dopo aver installato AccountFlow

Write-Host "===============================================" -ForegroundColor Green
Write-Host "  AccountFlow - Post-Install Configuration" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Verifica se AccountFlow è installato
$DefaultInstallPath = "$env:ProgramFiles\Andrea Frattini\AccountFlow - Gestione Finanziaria"
$ExecutablePath = "$DefaultInstallPath\AccountFlow - Gestione Finanziaria.exe"

if (-not (Test-Path $ExecutablePath)) {
    Write-Host "❌ AccountFlow non sembra essere installato in: $DefaultInstallPath" -ForegroundColor Red
    Write-Host "Verifica che l'installazione sia completata correttamente." -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

Write-Host "✅ AccountFlow trovato in: $DefaultInstallPath" -ForegroundColor Green
Write-Host ""

# Crea collegamento desktop
Write-Host "Creazione collegamento desktop..." -ForegroundColor Yellow
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = $WshShell.SpecialFolders("Desktop")
    $ShortcutPath = "$DesktopPath\AccountFlow.lnk"
    
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $ExecutablePath
    $Shortcut.WorkingDirectory = $DefaultInstallPath
    $Shortcut.Description = "AccountFlow - Gestione Finanziaria"
    $Shortcut.IconLocation = "$ExecutablePath,0"
    $Shortcut.Save()
    
    Write-Host "✅ Collegamento desktop creato: $ShortcutPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Errore nella creazione del collegamento desktop: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Configurazione completata!" -ForegroundColor Green
Write-Host ""
Write-Host "Ora puoi:" -ForegroundColor Cyan
Write-Host "• Avviare AccountFlow dal collegamento desktop" -ForegroundColor Gray
Write-Host "• Trovare AccountFlow nel menu Start" -ForegroundColor Gray
Write-Host "• Usare l'applicazione per gestire i tuoi dati finanziari" -ForegroundColor Gray
Write-Host ""

Read-Host "Premi Enter per uscire"