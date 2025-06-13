#!/bin/bash
echo "🔁 [SerdaBot] Lancement des serveurs..."

mkdir -p logs

echo "🚀 Démarrage du serveur IA..."
PYTHONPATH=src uvicorn src.core.server.api_server:app --port 8000 >> logs/api_server.log 2>&1 &

echo "🌍 Vérification de LibreTranslate..."
if command -v libretranslate &> /dev/null; then
    echo "🌍 Lancement de LibreTranslate (CLI)..."
    libretranslate --host 127.0.0.1 --port 5000 >> logs/translate.log 2>&1 &
else
    echo "⚠️ LibreTranslate CLI non trouvé, tentative via Python module..."
    python3 -m libretranslate >> logs/translate.log 2>&1 &
fi

echo "✅ Serveurs lancés. Vérifie les logs si besoin."
