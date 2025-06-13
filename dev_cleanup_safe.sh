#!/bin/bash

echo "🧼 Cleaning development residue for SerdaBot (no code or model loss)"

# Dossiers et fichiers temporaires à supprimer
CLEAN_PATHS=(
  "__pycache__"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  ".vscode"
  ".idea"
  "*.log"
  "*.pyc"
  "*.pyo"
  "*.DS_Store"
  "Thumbs.db"
  "*.code-workspace"
  "*.zip"
  "*.bak"
  "*~"
  ".coverage"
  "coverage.xml"
  "*Zone.Identifier"
)

echo "📦 Removing development clutter..."

for pattern in "${CLEAN_PATHS[@]}"; do
  find . -name "$pattern" -exec rm -rf {} + 2>/dev/null
done

echo "✅ Done. Your project folder is clean and intact."
