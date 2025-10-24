# ============================================
# KissBot V1 - INSTALLEUR AUTOMATIQUE WINDOWS
# ============================================
# Usage: 
# 1. PowerShell en Admin
# 2. Set-ExecutionPolicy RemoteSigned
# 3. .\install.ps1
# ============================================
# - Télécharge KissBot depuis GitHub
# - Installe toutes les dépendances
# - Configure l'environnement
# - Guide l'utilisateur pour la config finale
# ============================================

# Configuration
$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/ElSerda/SerdaBot"
$Branch = "kissbot"
$InstallDir = "KissBot-V1"
$KissBotDir = "KissBot"

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
Write-ColorOutput Cyan "🚀   INSTALLEUR KISSBOT V1 - TWITCH BOT"
Write-ColorOutput Cyan "============================================"
Write-Host ""

# Détection OS
$OS = "Windows $((Get-WmiObject Win32_OperatingSystem).Caption)"
Write-ColorOutput Blue "🖥️  Système détecté: $OS"
Write-Host ""

# Vérification des prérequis
Write-ColorOutput Yellow "🔍 Vérification des prérequis..."

# Git
try {
    $gitVersion = git --version 2>$null
    Write-ColorOutput Green "✅ Git: $gitVersion"
} catch {
    Write-ColorOutput Red "❌ Git non trouvé."
    Write-ColorOutput Yellow "💡 Installez Git depuis: https://git-scm.com/"
    Write-ColorOutput Yellow "💡 Ou avec Chocolatey: choco install git"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

# Python
try {
    $pythonVersion = python --version 2>$null
    Write-ColorOutput Green "✅ Python: $pythonVersion"
} catch {
    Write-ColorOutput Red "❌ Python non trouvé."
    Write-ColorOutput Yellow "💡 Installez Python 3.8+ depuis: https://python.org"
    Write-ColorOutput Yellow "💡 Cochez 'Add Python to PATH' lors de l'installation"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

# Pip
try {
    $pipVersion = pip --version 2>$null
    Write-ColorOutput Green "✅ Pip disponible"
} catch {
    Write-ColorOutput Red "❌ Pip non trouvé."
    Write-ColorOutput Yellow "💡 Réinstallez Python avec pip inclus"
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host ""
Write-ColorOutput Magenta "🎯 Tous les prérequis sont OK !"
Write-Host ""

# Téléchargement
Write-ColorOutput Yellow "📥 Téléchargement de KissBot V1..."

if (Test-Path $InstallDir) {
    Write-ColorOutput Yellow "⚠️  Le dossier $InstallDir existe déjà."
    $choice = Read-Host "Voulez-vous le supprimer et recommencer ? (y/N)"
    if ($choice -match "^[Yy]$") {
        Remove-Item $InstallDir -Recurse -Force
        Write-ColorOutput Green "✅ Dossier nettoyé"
    } else {
        Write-ColorOutput Red "❌ Installation annulée"
        Read-Host "Appuyez sur Entrée pour fermer"
        exit 1
    }
}

Write-ColorOutput Blue "🔄 Clonage du repository..."
git clone -b $Branch $RepoUrl $InstallDir

# Navigation vers KissBot
Set-Location "$InstallDir\$KissBotDir"

Write-ColorOutput Green "✅ KissBot téléchargé avec succès !"
Write-Host ""

# Installation des dépendances
Write-ColorOutput Yellow "📦 Installation des dépendances Python..."

# Création environnement virtuel
Write-ColorOutput Blue "🔧 Création de l'environnement virtuel..."
python -m venv kissbot-venv

# Activation
Write-ColorOutput Blue "🔧 Activation de l'environnement..."
& "kissbot-venv\Scripts\Activate.ps1"

# Installation requirements
Write-ColorOutput Blue "📋 Installation des packages..."
pip install -r requirements.txt

Write-ColorOutput Green "✅ Toutes les dépendances installées !"
Write-Host ""

# Configuration
Write-ColorOutput Magenta "⚙️  CONFIGURATION FINALE"
Write-ColorOutput Magenta "========================"
Write-Host ""

# Copie du template config
if (-not (Test-Path "config.yaml")) {
    if (Test-Path "config.yaml.example") {
        Copy-Item "config.yaml.example" "config.yaml"
        Write-ColorOutput Green "✅ Fichier config.yaml créé depuis le template"
    } else {
        Write-ColorOutput Red "❌ Template de configuration manquant"
        Read-Host "Appuyez sur Entrée pour fermer"
        exit 1
    }
}

Write-ColorOutput Cyan "🎮 Configuration de votre bot Twitch:"
Write-Host ""

# Guide utilisateur
Write-ColorOutput Yellow "📝 ÉTAPES SUIVANTES:"
Write-Host ""
Write-Host "1. Configurez votre bot dans le fichier config.yaml:"
Write-Host "   - Nom de votre bot (ex: mon_bot)"
Write-Host "   - Channel à rejoindre (ex: votre_pseudo)"
Write-Host "   - Token Twitch (générez sur https://twitchtokengenerator.com/)"
Write-Host "   - Clés API (RAWG, OpenAI optionnel)"
Write-Host ""
Write-ColorOutput Cyan "2. Modifiez la configuration:"
Write-ColorOutput Cyan "   notepad config.yaml"
Write-Host ""
Write-ColorOutput Cyan "3. Lancez votre bot:"
Write-ColorOutput Cyan "   .\start_kissbot.ps1"
Write-Host ""

Write-ColorOutput Green "✅ Installation terminée avec succès !"
Write-Host ""
Write-ColorOutput Magenta "📂 Votre bot est installé dans: $(Get-Location)"
Write-ColorOutput Magenta "🚀 Prêt à lancer avec .\start_kissbot.ps1"
Write-Host ""
Write-ColorOutput Cyan "🎊 Bienvenue dans KissBot V1 - Keep It Simple, Stupid!"
Write-Host ""

Read-Host "Appuyez sur Entrée pour fermer"