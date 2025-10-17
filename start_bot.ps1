# start_bot.ps1 - Lanceur PowerShell pour SerdaBot

Write-Host "[SerdaBot] Lancement du bot Twitch..." -ForegroundColor Cyan

# === Verifier l'environnement virtuel ===
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERREUR] Aucun environnement virtuel trouve." -ForegroundColor Red
    Write-Host "   Lance : python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# === Activer l'environnement virtuel ===
Write-Host "[INFO] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# === Lancer le bot ===
Write-Host "[OK] Demarrage du bot Twitch..." -ForegroundColor Green
$env:PYTHONPATH = "."
python src/chat/twitch_bot.py

# === Fin ===
Write-Host "[OK] SerdaBot arrete proprement." -ForegroundColor Green
