#!/bin/bash

echo "🔁 [SerdaBot] Lancement des serveurs..."

# Démarrer l'API IA (serve_mistral.py via uvicorn)
echo "🚀 Démarrage du serveur IA..."
nohup uvicorn src.core.server.api_server:app --host 127.0.0.1 --port 8000 --log-level warning > logs/api_server.log 2>&1 &

# Optionnel : démarrer LibreTranslate si installé
if command -v libretranslate &> /dev/null; then
    echo "🌍 Démarrage de LibreTranslate..."
    nohup libretranslate --host 127.0.0.1 --port 5000 > logs/libretranslate.log 2>&1 &
else
    echo "⚠️ LibreTranslate non trouvé, ignoré."
fi

echo "✅ Serveurs lancés. Vérifie les logs si besoin."
