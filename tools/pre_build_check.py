#!/usr/bin/env python3
"""
pre_build_check.py - Vérifie que le projet est prêt pour un build
"""

import sys
from pathlib import Path

ISSUES = []
WARNINGS = []

def check_files_exist():
    """Vérifie que tous les fichiers requis existent"""
    required = [
        "src/chat/twitch_bot.py",
        "src/config/config.sample.yaml",
        "README.md",
        "LICENSE",
        "requirements.txt",
    ]
    
    for file in required:
        if not Path(file).exists():
            ISSUES.append(f"❌ Fichier manquant: {file}")
        else:
            print(f"✅ {file}")

def check_imports():
    """Vérifie que les imports principaux sont disponibles"""
    modules = [
        "twitchio",
        "httpx",
        "yaml",
        "deep_translator",
        "langdetect",
        "bs4",
        "requests",
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Module '{module}' importable")
        except ImportError:
            ISSUES.append(f"❌ Module manquant: {module}")

def check_structure():
    """Vérifie la structure des dossiers"""
    dirs = [
        "src/prompts",
        "src/config",
        "src/core/commands",
        "src/utils",
        "data",
        "logs",
    ]
    
    for dir_path in dirs:
        if not Path(dir_path).exists():
            WARNINGS.append(f"⚠️ Dossier manquant: {dir_path}")
        else:
            print(f"✅ {dir_path}/")

def check_prompts():
    """Vérifie que les prompts existent"""
    prompt_dir = Path("src/prompts")
    if not prompt_dir.exists():
        ISSUES.append("❌ Dossier src/prompts manquant")
        return
    
    required_prompts = [
        "prompt_ask_fr.txt",
        "prompt_ask_en.txt",
        "prompt_chill_fr.txt",
        "prompt_chill_en.txt",
        "prompt_game_fr.txt",
        "prompt_game_en.txt",
    ]
    
    for prompt in required_prompts:
        path = prompt_dir / prompt
        if not path.exists():
            ISSUES.append(f"❌ Prompt manquant: {prompt}")
        else:
            print(f"✅ {prompt}")

def check_secrets():
    """Vérifie qu'il n'y a pas de secrets dans le code"""
    sensitive_patterns = [
        ("config.yaml", "src/config/config.yaml"),
        ("tokens.json", ".tio.tokens.json"),
    ]
    
    for _, path in sensitive_patterns:
        if Path(path).exists():
            WARNINGS.append(f"⚠️ Fichier sensible présent: {path} (ne sera pas inclus dans build)")

def main():
    print("=" * 60)
    print("🔍 SerdaBot - Vérification Pré-Build")
    print("=" * 60)
    print()
    
    print("📁 Vérification des fichiers...")
    check_files_exist()
    print()
    
    print("📦 Vérification des modules Python...")
    check_imports()
    print()
    
    print("🗂️  Vérification de la structure...")
    check_structure()
    print()
    
    print("📝 Vérification des prompts...")
    check_prompts()
    print()
    
    print("🔐 Vérification des secrets...")
    check_secrets()
    print()
    
    print("=" * 60)
    
    if ISSUES:
        print("❌ PROBLÈMES CRITIQUES:")
        for issue in ISSUES:
            print(f"   {issue}")
        print()
        print("❌ Le build ne peut pas continuer !")
        return 1
    
    if WARNINGS:
        print("⚠️  AVERTISSEMENTS:")
        for warning in WARNINGS:
            print(f"   {warning}")
        print()
    
    print("✅ Tous les checks sont OK !")
    print("   Le projet est prêt pour le build.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
