#!/bin/bash

echo "🤖 [SerdaBot] Lancement du bot Twitch..."

# === Détection de la configuration locale ===
if [ -f "../SerdaBot-local/config/config.yaml" ]; then
    export SERDABOT_CONFIG="../SerdaBot-local/config/config.yaml"
    echo "✅ Utilisation de la config locale (SerdaBot-local/config/config.yaml)"
elif [ -f "src/config/config.yaml" ]; then
    export SERDABOT_CONFIG="src/config/config.yaml"
    echo "⚠️  Config locale non trouvée → utilisation de src/config/config.yaml"
else
    export SERDABOT_CONFIG="src/config/config.sample.yaml"
    echo "⚠️  Aucune config trouvée → utilisation de config.sample.yaml (mode exemple)"
fi

# === Détection du fichier .env ===
if [ -f "../SerdaBot-local/.env" ]; then
    export DOTENV_PATH="../SerdaBot-local/.env"
    echo "✅ Variables d'environnement depuis SerdaBot-local/.env"
elif [ -f ".env" ]; then
    export DOTENV_PATH=".env"
    echo "⚠️  .env local non trouvé → utilisation de .env (racine du repo)"
else
    echo "ℹ️  Aucun fichier .env détecté (optionnel)"
fi

# === Activer l'environnement virtuel ===
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
