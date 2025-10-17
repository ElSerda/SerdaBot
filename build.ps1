# build.ps1 - Script de build Windows pour SerdaBot

param(
    [switch]$Clean,
    [switch]$Test,
    [string]$Version = "0.1.0-alpha"
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " SerdaBot Build Script (Windows)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# === Nettoyage ===
if ($Clean) {
    Write-Host "[1/5] Nettoyage des anciens builds..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, *.spec
    Write-Host "      OK - Dossiers nettoyes" -ForegroundColor Green
} else {
    Write-Host "[1/5] Nettoyage... SKIP (utilise -Clean pour forcer)" -ForegroundColor Gray
}

# === Tests ===
if ($Test) {
    Write-Host "[2/5] Execution des tests..." -ForegroundColor Yellow
    & pytest tests/ -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      ERREUR - Tests echoues !" -ForegroundColor Red
        exit 1
    }
    Write-Host "      OK - Tous les tests passent" -ForegroundColor Green
} else {
    Write-Host "[2/5] Tests... SKIP (utilise -Test pour executer)" -ForegroundColor Gray
}

# === Verification PyInstaller ===
Write-Host "[3/5] Verification de PyInstaller..." -ForegroundColor Yellow
$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Host "      PyInstaller non installe. Installation..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      ERREUR - Installation de PyInstaller echouee !" -ForegroundColor Red
        exit 1
    }
}
Write-Host "      OK - PyInstaller pret" -ForegroundColor Green

# === Build ===
Write-Host "[4/5] Build de l'executable..." -ForegroundColor Yellow
Write-Host "      Ceci peut prendre plusieurs minutes..." -ForegroundColor Gray

pyinstaller `
    --onefile `
    --name "SerdaBot" `
    --add-data "src/prompts;prompts" `
    --add-data "src/config/config.sample.yaml;config" `
    --hidden-import twitchio `
    --hidden-import twitchio.ext.commands `
    --hidden-import httpx `
    --hidden-import deep_translator `
    --hidden-import langdetect `
    --hidden-import yaml `
    --hidden-import bs4 `
    --hidden-import requests `
    --clean `
    src/chat/twitch_bot.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERREUR - Build echoue !" -ForegroundColor Red
    exit 1
}
Write-Host "      OK - Build termine" -ForegroundColor Green

# === Package ===
Write-Host "[5/5] Creation de l'archive..." -ForegroundColor Yellow

$archiveName = "SerdaBot-v$Version-win64.zip"
$filesToZip = @(
    "dist\SerdaBot.exe",
    "src\config\config.sample.yaml",
    "README.md",
    "INSTALL_WINDOWS.md",
    "LICENSE"
)

Compress-Archive -Path $filesToZip -DestinationPath $archiveName -Force
Write-Host "      OK - Archive creee: $archiveName" -ForegroundColor Green

# === Résumé ===
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Build Complete !" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Executable : dist\SerdaBot.exe" -ForegroundColor White
Write-Host "Archive    : $archiveName" -ForegroundColor White
Write-Host ""

$exeSize = (Get-Item "dist\SerdaBot.exe").Length / 1MB
Write-Host "Taille EXE : $([math]::Round($exeSize, 2)) MB" -ForegroundColor Gray

Write-Host ""
Write-Host "Pour tester :" -ForegroundColor Yellow
Write-Host "  cd dist" -ForegroundColor Gray
Write-Host "  .\SerdaBot.exe" -ForegroundColor Gray
Write-Host ""
