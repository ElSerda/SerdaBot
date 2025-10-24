# ============================================
# KissBot V1 - Lanceur Windows PowerShell SÉCURISÉ
# ============================================
# Usage: .\start_kissbot.ps1
# - Auto-détection et création venv si absent
# - Installation auto des dépendances
# - Lance KissBot avec console interactive
# - Gestion d'erreurs complète
# ============================================

# Configuration
$ErrorActionPreference = "Stop"

Write-Host "🚀 ============================================" -ForegroundColor Cyan
Write-Host "🚀   LANCEMENT KISSBOT V1 - TWITCH BOT" -ForegroundColor Cyan  
Write-Host "🚀 ============================================" -ForegroundColor Cyan
Write-Host ""

# Répertoire du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📂 Répertoire de travail: $ScriptDir" -ForegroundColor Gray
Write-Host ""

# Vérification Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Installez Python 3.8+ d'abord." -ForegroundColor Red
    Write-Host "💡 Téléchargez sur: https://python.org" -ForegroundColor Yellow
    Write-Host "💡 Cochez 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

# Auto-création venv si absent
if (-not (Test-Path "kissbot-venv")) {
    Write-Host "🔧 Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv kissbot-venv
    Write-Host "✅ Environnement virtuel créé" -ForegroundColor Green
} else {
    Write-Host "✅ Environnement virtuel trouvé" -ForegroundColor Green
}

# Vérification config
if (-not (Test-Path "config.yaml")) {
    Write-Host "❌ Fichier config.yaml manquant." -ForegroundColor Red
    if (Test-Path "config.yaml.example") {
        Write-Host "💡 Copiez config.yaml.example vers config.yaml et configurez vos tokens:" -ForegroundColor Yellow
        Write-Host "   copy config.yaml.example config.yaml" -ForegroundColor Yellow
        Write-Host "   notepad config.yaml" -ForegroundColor Yellow
    } else {
        Write-Host "💡 Créez un fichier config.yaml avec votre configuration" -ForegroundColor Yellow
    }
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "🔧 Activation environnement virtuel..." -ForegroundColor Yellow

# Vérification du script d'activation
if (-not (Test-Path "kissbot-venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Script d'activation venv non trouvé." -ForegroundColor Red
    Write-Host "💡 Recréez le venv: Remove-Item kissbot-venv -Recurse; python -m venv kissbot-venv" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

& "kissbot-venv\Scripts\Activate.ps1"
Write-Host "✅ Environnement activé" -ForegroundColor Green
Write-Host ""

# Vérification requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Fichier requirements.txt manquant." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "🎯 Vérification et installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✅ Dépendances installées" -ForegroundColor Green
Write-Host ""

# Vérification main.py
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Fichier main.py manquant." -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour fermer"
    exit 1
}

Write-Host "🚀 Lancement KissBot V1..." -ForegroundColor Cyan
Write-Host "📝 Logs en temps réel (Ctrl+C pour arrêter proprement)" -ForegroundColor Gray
Write-Host "🔧 Modèle détecté automatiquement, prompts optimisés" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor Gray

# Lancement avec gestion d'erreur et trap
try {
    python main.py
} catch {
    Write-Host ""
    Write-Host "❌ Erreur lors du lancement:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "🛑 KissBot arrêté." -ForegroundColor Yellow
    Write-Host "📋 Vérifiez les logs pour plus d'infos." -ForegroundColor Gray
    Read-Host "Appuyez sur Entrée pour fermer"
}