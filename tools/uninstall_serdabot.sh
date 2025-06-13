#!/bin/bash

echo "🧹 Uninstalling SerdaBot..."

# Désactiver l'environnement virtuel s'il est actif
deactivate 2>/dev/null || true

# Supprimer les environnements virtuels locaux
rm -rf .venv venv

# Supprimer les fichiers générés
rm -rf __pycache__/ logs/ models/ .mypy_cache/ .pytest_cache/
rm -f config.yaml

# Supprimer les artefacts de test
rm -f .coverage .ruff_cache coverage.xml

echo "✅ SerdaBot has been cleaned up."
echo "🗑️  You can now delete the project folder if needed."
