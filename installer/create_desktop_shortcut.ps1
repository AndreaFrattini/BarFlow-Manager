# Script per creare collegamento desktop per AccountFlow
param(
    [string]$InstallPath = "$env:ProgramFiles\Andrea Frattini\AccountFlow - Gestione Finanziaria",
    [string]$ExecutableName = "AccountFlow - Gestione Finanziaria.exe"
)

try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = $WshShell.SpecialFolders("Desktop")
    $ShortcutPath = "$DesktopPath\AccountFlow - Gestione Finanziaria.lnk"
    
    # Crea il collegamento
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "$InstallPath\$ExecutableName"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "AccountFlow - Gestione Finanziaria"
    $Shortcut.IconLocation = "$InstallPath\$ExecutableName,0"
    $Shortcut.Save()
    
    Write-Host "✅ Collegamento desktop creato: $ShortcutPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Errore nella creazione del collegamento desktop: $($_.Exception.Message)" -ForegroundColor Red
}