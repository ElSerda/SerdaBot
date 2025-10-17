#!/bin/bash
# format_code.sh - Auto-format Python code with black and isort

set -e

echo "🎨 Formatage du code Python..."
echo ""

# Activer l'environnement virtuel si disponible
if [ -d "venv/bin" ]; then
    source venv/bin/activate
fi

# Vérifier que les outils sont installés
if ! command -v black &> /dev/null; then
    echo "⚠️  black non installé. Installation..."
    pip install black -q
fi

if ! command -v isort &> /dev/null; then
    echo "⚠️  isort non installé. Installation..."
    pip install isort -q
fi

echo "🔧 [1/3] Nettoyage des trailing whitespaces..."
find src/ tests/ -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

echo "📦 [2/3] Tri des imports avec isort..."
isort src/ tests/ --profile black --line-length 100

echo "🖤 [3/3] Formatage avec black..."
black src/ tests/ --line-length 100 --quiet

echo ""
echo "✅ Formatage terminé !"
echo "   Fichiers formatés : src/ tests/"
echo ""
echo "💡 Tip: Ajoute un pre-commit hook pour automatiser :"
echo "   pip install pre-commit"
echo "   pre-commit install"
