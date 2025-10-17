# start_bot.ps1 - Lanceur PowerShell pour SerdaBot

Write-Host "🤖 [SerdaBot] Lancement du bot Twitch..." -ForegroundColor Cyan

# === Vérifier l'environnement virtuel ===
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Aucun environnement virtuel trouvé." -ForegroundColor Red
    Write-Host "   Lance : python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# === Activer l'environnement virtuel ===
Write-Host "📦 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# === Lancer le bot ===
Write-Host "🚀 Démarrage du bot Twitch..." -ForegroundColor Green
$env:PYTHONPATH = "."
python src/chat/twitch_bot.py

# === Fin ===
Write-Host "✅ SerdaBot arrêté proprement." -ForegroundColor Green
