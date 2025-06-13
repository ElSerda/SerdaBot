#!/bin/bash

echo "🧹 Bruteforce cleanup: removing non-essential files..."

# Liste des fichiers ou motifs à supprimer
FILES_TO_REMOVE=(
  "LIVE_TEST_TODO.md"
  "zip_light.sh"
  "ruff_output.txt"
  "code_review_prompt.txt"
  "vscode-settings-backup.json"
  "create_review_archive_fixed.sh"
  "PyLintreport.txt"
  "all_git_files.txt"
  "all_local_files.txt"
  "ghost_git_files.txt"
  "git_tracked.txt"
  "*.log"
  "*.bak"
  "*.zip"
  "*.Zone.Identifier"
  "*.DS_Store"
  "logs"
)

# Suppression brute
for pattern in "${FILES_TO_REMOVE[@]}"; do
  echo "🗑️ Removing: $pattern"
  find . -name "$pattern" -exec rm -rf {} + 2>/dev/null
done

echo "✅ Cleanup complete. Your project should now match the whitelist."
