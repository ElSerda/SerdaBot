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

# === Verifier la configuration ===
if (-Not (Test-Path "src\config\config.yaml")) {
    Write-Host "[WARNING] config.yaml manquant. Creation depuis config.sample.yaml..." -ForegroundColor Yellow
    Copy-Item "src\config\config.sample.yaml" "src\config\config.yaml"
    Write-Host "[INFO] config.yaml cree ! Edite-le avec tes tokens avant de continuer." -ForegroundColor Cyan
    Write-Host "       Chemin: src\config\config.yaml" -ForegroundColor Gray
    Write-Host ""
    $response = Read-Host "Appuie sur ENTREE pour continuer ou CTRL+C pour arreter"
}

# === Lancer le bot ===
Write-Host "[OK] Demarrage du bot Twitch..." -ForegroundColor Green
$env:PYTHONPATH = ".;src"
python src/chat/twitch_bot.py

# === Fin ===
Write-Host "[OK] SerdaBot arrete proprement." -ForegroundColor Green
