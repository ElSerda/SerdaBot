#!/bin/bash

set -e

echo "📦 Building review package..."

# Dossier de sortie
OUTDIR="serdabot_review"
mkdir -p $OUTDIR/src/core/commands
mkdir -p $OUTDIR/src/utils
mkdir -p $OUTDIR/tools

# Tableau des fichiers à copier avec leur chemin source
declare -A FILES=(
  ["src/core/commands/ask_command.py"]="$OUTDIR/src/core/commands/"
  ["src/core/commands/game_command.py"]="$OUTDIR/src/core/commands/"
  ["src/core/commands/trad_command.py"]="$OUTDIR/src/core/commands/"
  ["src/core/commands/chill_command.py"]="$OUTDIR/src/core/commands/"
  ["src/utils/ask_utils.py"]="$OUTDIR/src/utils/"
  ["src/utils/game_utils.py"]="$OUTDIR/src/utils/"
  ["src/utils/chill_utils.py"]="$OUTDIR/src/utils/"
  ["src/utils/translation.py"]="$OUTDIR/src/utils/"
  ["pyproject.toml"]="$OUTDIR/"
  ["config.sample.yaml"]="$OUTDIR/"
  ["PROJECT_STRUCTURE.md"]="$OUTDIR/"
  ["code_review_prompt.txt"]="$OUTDIR/"
)

# Copie conditionnelle
for filepath in "${!FILES[@]}"; do
  if [ -f "$filepath" ]; then
    cp "$filepath" "${FILES[$filepath]}"
    echo "✅ Copied: $filepath"
  else
    echo "⚠️ Missing: $filepath"
  fi
done

# Création de l'archive
zip -r serdabot_review_package.zip $OUTDIR > /dev/null
echo "✅ Archive created: serdabot_review_package.zip"
