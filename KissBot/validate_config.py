#!/usr/bin/env python3

"""
KissBot V1 - Validateur Configuration Python
===========================================
Usage: python3 validate_config.py
Vérifie que config.yaml est correctement configuré
"""

import sys
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    print("❌ PyYAML non installé. Lancez d'abord : pip install -r requirements.txt")
    sys.exit(1)

def print_colored(text, color=""):
    """Affichage coloré simple"""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m", 
        "yellow": "\033[1;33m",
        "blue": "\033[0;34m",
        "purple": "\033[0;35m",
        "cyan": "\033[0;36m",
        "nc": "\033[0m"
    }
    color_code = colors.get(color, "")
    reset = colors["nc"]
    print(f"{color_code}{text}{reset}")

def check_config_value(config, path, description, required=True):
    """Vérifie une valeur de config avec path type 'section.key'"""
    try:
        keys = path.split('.')
        value = config
        for key in keys:
            value = value[key]
        
        # Vérification valeur vide ou template
        if not value or str(value).startswith("VOTRE_") or "_ICI" in str(value):
            if required:
                print_colored(f"❌ {description} non configuré ({path})", "red")
                return False
            else:
                print_colored(f"⚠️  {description} non configuré ({path})", "yellow")
                return True
        else:
            print_colored(f"✅ {description} configuré", "green")
            return True
            
    except (KeyError, TypeError):
        if required:
            print_colored(f"❌ {description} manquant ({path})", "red")
            return False
        else:
            print_colored(f"⚠️  {description} optionnel manquant ({path})", "yellow")
            return True

def main():
    print_colored("🔍 ============================================", "cyan")
    print_colored("🔍   VALIDATION CONFIGURATION KISSBOT V1", "cyan")
    print_colored("🔍 ============================================", "cyan")
    print()
    
    # Vérification fichier config
    config_file = Path("config.yaml")
    if not config_file.exists():
        print_colored("❌ Fichier config.yaml manquant", "red")
        if Path("config.yaml.example").exists():
            print_colored("💡 Copiez le template : cp config.yaml.example config.yaml", "yellow")
        sys.exit(1)
    
    print_colored("✅ Fichier config.yaml trouvé", "green")
    
    # Chargement config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print_colored(f"❌ Erreur YAML : {e}", "red")
        sys.exit(1)
    except Exception as e:
        print_colored(f"❌ Erreur lecture fichier : {e}", "red")
        sys.exit(1)
    
    errors = 0
    
    # Tests configuration bot
    print()
    print_colored("🤖 Validation configuration bot...", "yellow")
    if not check_config_value(config, "bot.name", "Nom du bot"):
        errors += 1
    
    # Tests configuration Twitch
    print()
    print_colored("🎮 Validation configuration Twitch...", "yellow")
    
    if not check_config_value(config, "twitch.token", "Token Twitch"):
        print_colored("💡 Générez sur : https://twitchtokengenerator.com/", "blue")
        errors += 1
    
    if not check_config_value(config, "twitch.client_id", "Client ID"):
        print_colored("💡 Créez app sur : https://dev.twitch.tv/console/apps", "blue")
        errors += 1
    
    if not check_config_value(config, "twitch.bot_id", "Bot User ID"):
        print_colored("💡 Trouvez sur : https://www.streamweasels.com/twitch-tools/username-converter/", "blue")
        errors += 1
    
    # Vérification channels
    try:
        channels = config["twitch"]["channels"]
        if not channels or any("VOTRE_" in str(ch) for ch in channels):
            print_colored("❌ Channels non configurés", "red")
            print_colored("💡 Ajoutez votre channel dans twitch.channels", "blue")
            errors += 1
        else:
            print_colored(f"✅ Channels configurés: {channels}", "green")
    except (KeyError, TypeError):
        print_colored("❌ Section channels manquante", "red")
        print_colored("💡 Ajoutez channels: [\"votre_channel\"] dans la section twitch", "blue")
        errors += 1
    
    # Tests APIs optionnelles
    print()
    print_colored("🔑 Validation APIs (optionnelles)...", "yellow")
    
    if check_config_value(config, "apis.rawg_key", "Clé RAWG API", required=False):
        print_colored("💡 Commandes jeux (!gameinfo) activées", "blue")
    else:
        print_colored("⚠️  Commandes jeux désactivées (clé RAWG manquante)", "yellow")
        print_colored("💡 Gratuit sur : https://rawg.io/apidocs", "blue")
    
    if check_config_value(config, "apis.openai_key", "Clé OpenAI API", required=False):
        print_colored("✅ Clé OpenAI configurée (fallback LLM activé)", "green")
    else:
        print_colored("⚠️  Fallback OpenAI désactivé (clé manquante)", "yellow")
        print_colored("💡 Payant sur : https://platform.openai.com/api-keys", "blue")
    
    # Tests LLM
    print()
    print_colored("🧠 Validation configuration LLM...", "yellow")
    
    try:
        llm_enabled = config.get("llm", {}).get("enabled", False)
        if llm_enabled:
            print_colored("✅ LLM activé", "green")
            
            local_llm = config.get("llm", {}).get("local_llm", False)
            if local_llm:
                print_colored("✅ LLM local configuré", "green")
                print_colored("💡 Assurez-vous que LM Studio tourne sur port 1234", "blue")
            else:
                print_colored("⚠️  LLM local désactivé, utilise OpenAI uniquement", "yellow")
        else:
            print_colored("⚠️  LLM désactivé (bot en mode commandes simples uniquement)", "yellow")
    except Exception:
        print_colored("⚠️  Configuration LLM incomplète", "yellow")
    
    # Résumé final
    print()
    print_colored("📋 ============================================", "purple")
    if errors == 0:
        print_colored("🎊   CONFIGURATION VALIDE !", "green")
        print_colored("🎊 ============================================", "green")
        print()
        print_colored("🚀 Votre KissBot est prêt à être lancé !", "cyan")
        print_colored("💡 Commande de lancement : ./start_kissbot.sh", "blue")
        print()
        print_colored("🧪 Tests recommandés après lancement :", "yellow")
        print_colored("   !ping           # Test connectivité", "blue")
        print_colored("   @votre_bot hey  # Test LLM (si activé)", "blue")
        print_colored("   !gameinfo zelda # Test API jeux (si RAWG configuré)", "blue")
    else:
        print_colored("❌   CONFIGURATION INCOMPLÈTE", "red")
        print_colored("❌ ============================================", "red")
        print()
        print_colored(f"🔧 {errors} erreur(s) à corriger avant lancement", "yellow")
        print_colored("💡 Consultez TWITCH_SETUP_GUIDE.md pour aide détaillée", "blue")
        sys.exit(1)

if __name__ == "__main__":
    main()