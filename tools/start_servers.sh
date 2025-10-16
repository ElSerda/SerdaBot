#!/bin/bash

export PYTHONPATH=src

echo "🔁 [SerdaBot] Lancement des serveurs..."

# Créer le dossier de logs si absent
mkdir -p logs

# === Lancer le serveur FastAPI (LLM proxy) ===
echo "🚀 Démarrage du serveur IA..."
nohup uvicorn src.core.server.api_server:app --host 127.0.0.1 --port 8000 >> logs/api_server.log 2>&1 &


# === Lancer LibreTranslate ===
echo "🌍 Vérification de LibreTranslate..."
if command -v libretranslate &> /dev/null; then
    echo "🌍 Lancement de LibreTranslate (CLI)..."
    libretranslate --host 127.0.0.1 --port 5000 >> logs/translate.log 2>&1 &
else
    echo "⚠️ LibreTranslate CLI non trouvé, tentative via Python module..."
    python3 -m libretranslate >> logs/translate.log 2>&1 &
fi

# === Fin ===
echo "✅ Serveurs lancés. Consulte les logs dans ./logs/ pour les détails."
