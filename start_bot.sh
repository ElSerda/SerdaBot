#!/bin/bash

echo "🤖 [SerdaBot] Lancement du bot Twitch..."

# === Activer l’environnement virtuel ===
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Aucun environnement virtuel trouvé. Lance : python -m venv venv"
    exit 1
fi
source venv/bin/activate

# === Lancer le bot avec gestion propre des imports ===
echo "🚀 Démarrage du bot Twitch..."
PYTHONPATH=. python src/chat/twitch_bot.py

# === Fin ===
echo "✅ SerdaBot arrêté proprement."
