# AccountFlow - Script di Disinstallazione PowerShell
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   AccountFlow - Disinstallazione PowerShell" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Verifica privilegi amministratore
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        throw "Privilegi di amministratore richiesti per la disinstallazione."
    }

    Write-Host "Inizio disinstallazione AccountFlow..." -ForegroundColor Yellow
    
    # Termina processi AccountFlow se in esecuzione
    Write-Host "Terminazione processi AccountFlow..." -ForegroundColor Gray
    Get-Process | Where-Object {$_.ProcessName -like "*AccountFlow*" -or $_.ProcessName -like "*BarFlow*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Rimuovi dal registro (Uninstall)
    Write-Host "Rimozione voci di registro..." -ForegroundColor Gray
    $uninstallPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AccountFlow*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\AccountFlow*"
    )
    
    foreach ($path in $uninstallPaths) {
        Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Rimuovi cartelle applicazione
    Write-Host "Rimozione cartelle applicazione..." -ForegroundColor Gray
    $foldersToRemove = @(
        "$env:ProgramFiles\AccountFlow",
        "$env:ProgramFiles(x86)\AccountFlow",
        "$env:LOCALAPPDATA\AccountFlow",
        "$env:APPDATA\AccountFlow"
    )

    foreach ($folder in $foldersToRemove) {
        if (Test-Path $folder) {
            Write-Host "Rimozione: $folder" -ForegroundColor DarkGray
            Remove-Item -Path $folder -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Rimuovi collegamenti dal menu Start
    Write-Host "Rimozione collegamenti menu Start..." -ForegroundColor Gray
    $startMenuPaths = @(
        "$env:ALLUSERSPROFILE\Microsoft\Windows\Start Menu\Programs\AccountFlow*",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\AccountFlow*"
    )

    foreach ($path in $startMenuPaths) {
        Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Rimuovi collegamenti desktop
    Write-Host "Rimozione collegamenti desktop..." -ForegroundColor Gray
    Get-ChildItem -Path "$env:PUBLIC\Desktop\*AccountFlow*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path "$env:USERPROFILE\Desktop\*AccountFlow*" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "Disinstallazione AccountFlow completata con successo!" -ForegroundColor Green
    exit 0

} catch {
    Write-Host ""
    Write-Host "ERRORE durante la disinstallazione: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
