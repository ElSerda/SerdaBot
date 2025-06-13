#!/bin/bash

# Nom du fichier ZIP (personnalisable)
ZIP_NAME="serdabot_light.zip"

echo "🧵 Création d'une archive allégée du projet..."

# Suppression précédente
rm -f $ZIP_NAME

# Zippage avec exclusions
zip -r $ZIP_NAME \
    ./src \
    ./tools \
    ./pyproject.toml \
    ./requirements.txt \
    ./install_project.sh \
    ./README.md \
    ./CHECKLIST.md \
    ./setup.cfg \
    -x "*.gguf" \
    -x "*.gguf:Zone.Identifier" \
    -x "venv/*" \
    -x "db/sessions/*" \
    -x "logs/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*.log"

# Résultat
if [ -f "$ZIP_NAME" ]; then
    echo "✅ Archive créée : $ZIP_NAME"
else
    echo "❌ Échec de la création de l'archive."
fi
