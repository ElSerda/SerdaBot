#!/bin/bash
# Installation du système de traduction SerdaBot

echo "🌐 Installation du système de traduction"
echo "========================================"
echo ""

# 1. Activer l'environnement virtuel
echo "1️⃣ Activation de l'environnement virtuel..."
source venv/bin/activate

# 2. Installer deep-translator
echo ""
echo "2️⃣ Installation de deep-translator..."
pip install deep-translator==1.11.4

# 3. Créer le répertoire data si nécessaire
echo ""
echo "3️⃣ Création du répertoire data/..."
mkdir -p data

# 4. Tester l'installation
echo ""
echo "4️⃣ Test du système..."
python tools/test_translation.py

# 5. Résultat
echo ""
if [ $? -eq 0 ]; then
    echo "✅ Installation réussie !"
    echo ""
    echo "📝 Prochaines étapes :"
    echo "  1. Redémarrer le bot: bash tools/start_servers.sh"
    echo "  2. Tester: !adddev @TestUser"
    echo "  3. Documentation: docs/TRANSLATION.md"
else
    echo "❌ Installation échouée"
    echo "   Vérifier les erreurs ci-dessus"
fi
