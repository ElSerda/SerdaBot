# ============================================
# KissBot V1 - ULTRA-INSTALLEUR ONE-LINER WINDOWS
# ============================================
# Usage: 
# PowerShell en Admin:
# irm https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/quick-install.ps1 | iex
# ============================================
# - Télécharge l'installeur principal
# - Lance l'installation complète  
# - Suivi console temps réel de TOUT
# ============================================

$ErrorActionPreference = "Stop"

# Configuration
$InstallScriptUrl = "https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/install.ps1"
$TempInstaller = "$env:TEMP\kissbot_installer.ps1"

# Fonctions d'affichage colorées
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan "============================================"
Write-ColorOutput Cyan "🚀   KISSBOT V1 - ULTRA-INSTALLEUR"
Write-ColorOutput Cyan "============================================"
Write-ColorOutput Yellow "📱 Installation ONE-LINER en cours..."
Write-Host ""

# Vérification connexion internet
Write-ColorOutput Blue "🌐 Vérification connexion internet..."
try {
    $testConnection = Test-NetConnection -ComputerName "github.com" -Port 443 -InformationLevel Quiet
    if (-not $testConnection) {
        throw "Connexion échouée"
    }
    Write-ColorOutput Green "✅ Connexion internet OK"
} catch {
    Write-ColorOutput Red "❌ Pas de connexion internet détectée"
    Write-ColorOutput Yellow "💡 Vérifiez votre connexion et réessayez"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

# Vérification PowerShell version
$psVersion = $PSVersionTable.PSVersion.Major
if ($psVersion -lt 3) {
    Write-ColorOutput Red "❌ PowerShell version trop ancienne ($psVersion)"
    Write-ColorOutput Yellow "💡 Installez PowerShell 5.1+ ou PowerShell Core"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}
Write-ColorOutput Green "✅ PowerShell $psVersion OK"

Write-Host ""
Write-ColorOutput Magenta "📥 Téléchargement de l'installeur principal..."

# Téléchargement de l'installeur
try {
    Invoke-WebRequest -Uri $InstallScriptUrl -OutFile $TempInstaller -UseBasicParsing
    
    if (-not (Test-Path $TempInstaller)) {
        throw "Fichier non créé"
    }
    
    Write-ColorOutput Green "✅ Installeur téléchargé avec succès"
} catch {
    Write-ColorOutput Red "❌ Échec du téléchargement de l'installeur"
    Write-ColorOutput Red "Erreur: $($_.Exception.Message)"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host ""
Write-ColorOutput Cyan "🚀 Lancement de l'installation complète..."
Write-ColorOutput Yellow "📺 Suivez le processus en temps réel :"
Write-ColorOutput Yellow "----------------------------------------"

# Lancer l'installeur principal avec suivi complet
try {
    & $TempInstaller
} catch {
    Write-ColorOutput Red "❌ Erreur lors de l'installation:"
    Write-ColorOutput Red $_.Exception.Message
} finally {
    # Nettoyage
    if (Test-Path $TempInstaller) {
        Remove-Item $TempInstaller -Force
    }
}

Write-Host ""
Write-ColorOutput Green "🎊 Installation ONE-LINER terminée !"
Write-ColorOutput Magenta "🎯 KissBot V1 est prêt à l'emploi !"
Write-Host ""

Read-Host "Appuyez sur Entrée pour fermer"