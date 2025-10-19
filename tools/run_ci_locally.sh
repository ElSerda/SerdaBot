#!/bin/bash
# Simule le workflow GitHub Actions CI en local

set -e  # Exit on error

echo "🔬 Simulation du CI GitHub Actions..."
echo ""

# Activate venv if it exists and not already activated
if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "🐍 Activation du venv..."
    source venv/bin/activate
fi

# Test
echo "📋 Step 1: Run tests (pytest)"
pytest
echo "✅ Tests passed!"
echo ""

# Lint (optionnel - pas dans le CI actuel mais utile)
# echo "🔍 Step 2: Lint with flake8"
# flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503
# echo "✅ Lint passed!"
# echo ""

echo "🎉 CI simulation completed successfully!"
