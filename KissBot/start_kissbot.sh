#!/bin/bash

# ============================================
# KissBot V1 - Lanceur Linux/WSL SÉCURISÉ
# ============================================
# Usage: ./start_kissbot.sh
# - Auto-détection et création venv si absent
# - Installation auto des dépendances
# - Lance KissBot avec console interactive
# - Gestion d'erreurs complète
# ============================================

set -e  # Exit on error

echo "🚀 ============================================"
echo "🚀   LANCEMENT KISSBOT V1 - TWITCH BOT"
echo "🚀 ============================================"
echo ""

# Répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Répertoire de travail: $SCRIPT_DIR"
echo ""

# Vérification Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé. Installez Python 3.8+ d'abord."
    echo "💡 Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "💡 Autres: https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
echo "✅ Python trouvé: $(python3 --version)"

# Auto-création venv si absent
if [ ! -d "kissbot-venv" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv kissbot-venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel trouvé"
fi

# Vérification config
if [ ! -f "config.yaml" ]; then
    echo "❌ Fichier config.yaml manquant."
    if [ -f "config.yaml.example" ]; then
        echo "💡 Copiez config.yaml.example vers config.yaml et configurez vos tokens:"
        echo "   cp config.yaml.example config.yaml"
        echo "   nano config.yaml  # ou votre éditeur préféré"
    else
        echo "💡 Créez un fichier config.yaml avec votre configuration"
    fi
    exit 1
fi

echo "🔧 Activation environnement virtuel..."
source kissbot-venv/bin/activate

echo "✅ Environnement activé: $(which python3)"
echo ""

# Vérification requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ Fichier requirements.txt manquant."
    exit 1
fi

echo "🎯 Vérification et installation des dépendances..."
pip install -r requirements.txt

echo "✅ Dépendances installées"
echo ""

# Vérification main.py
if [ ! -f "main.py" ]; then
    echo "❌ Fichier main.py manquant."
    exit 1
fi

echo "🚀 Lancement KissBot V1..."
echo "📝 Logs en temps réel (Ctrl+C pour arrêter proprement)"
echo "🔧 Modèle détecté automatiquement, prompts optimisés"
echo "----------------------------------------"

# Lancement avec gestion d'erreur et trap pour cleanup
trap 'echo ""; echo "🛑 Arrêt demandé par utilisateur"; exit 0' INT

python3 main.py

echo ""
echo "🛑 KissBot arrêté normalement."
echo "📋 Vérifiez les logs pour plus d'infos."