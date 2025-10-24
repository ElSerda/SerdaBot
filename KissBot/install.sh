#!/bin/bash

# ============================================
# KissBot V1 - INSTALLEUR AUTOMATIQUE
# ============================================
# Usage: curl -sSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/install.sh | bash
# - Télécharge KissBot depuis GitHub
# - Installe toutes les dépendances
# - Configure l'environnement
# - Guide l'utilisateur pour la config finale
# ============================================

set -e  # Exit on error

# Configuration
REPO_URL="https://github.com/ElSerda/SerdaBot"
BRANCH="kissbot"
INSTALL_DIR="KissBot-V1"
KISSBOT_DIR="KissBot"

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🚀   INSTALLEUR KISSBOT V1 - TWITCH BOT${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Vérification OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows (Git Bash)"
else
    OS="Inconnu"
fi

echo -e "${BLUE}🖥️  Système détecté: $OS${NC}"
echo ""

# Vérification des prérequis
echo -e "${YELLOW}🔍 Vérification des prérequis...${NC}"

# Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git non trouvé.${NC}"
    echo -e "${YELLOW}💡 Installez Git:${NC}"
    echo -e "   Ubuntu/Debian: sudo apt install git"
    echo -e "   macOS: brew install git"
    echo -e "   Windows: https://git-scm.com/"
    exit 1
fi
echo -e "${GREEN}✅ Git: $(git --version)${NC}"

# Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 non trouvé.${NC}"
    echo -e "${YELLOW}💡 Installez Python 3.8+:${NC}"
    echo -e "   Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo -e "   macOS: brew install python3"
    echo -e "   Windows: https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"

# Pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}❌ Pip non trouvé.${NC}"
    echo -e "${YELLOW}💡 Installez pip: sudo apt install python3-pip${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Pip disponible${NC}"

echo ""
echo -e "${PURPLE}🎯 Tous les prérequis sont OK !${NC}"
echo ""

# Téléchargement
echo -e "${YELLOW}📥 Téléchargement de KissBot V1...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Le dossier $INSTALL_DIR existe déjà.${NC}"
    read -p "Voulez-vous le supprimer et recommencer ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}✅ Dossier nettoyé${NC}"
    else
        echo -e "${RED}❌ Installation annulée${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}🔄 Clonage du repository...${NC}"
git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"

# Navigation vers KissBot
cd "$INSTALL_DIR/$KISSBOT_DIR"

echo -e "${GREEN}✅ KissBot téléchargé avec succès !${NC}"
echo ""

# Installation des dépendances
echo -e "${YELLOW}📦 Installation des dépendances Python...${NC}"

# Création environnement virtuel
echo -e "${BLUE}🔧 Création de l'environnement virtuel...${NC}"
python3 -m venv kissbot-venv

# Activation
echo -e "${BLUE}🔧 Activation de l'environnement...${NC}"
source kissbot-venv/bin/activate

# Installation requirements
echo -e "${BLUE}📋 Installation des packages...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✅ Toutes les dépendances installées !${NC}"
echo ""

# Configuration
echo -e "${PURPLE}⚙️  CONFIGURATION FINALE${NC}"
echo -e "${PURPLE}========================${NC}"
echo ""

# Copie du template config
if [ ! -f "config.yaml" ]; then
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo -e "${GREEN}✅ Fichier config.yaml créé depuis le template${NC}"
    else
        echo -e "${RED}❌ Template de configuration manquant${NC}"
        exit 1
    fi
fi

echo -e "${CYAN}🎮 Configuration de votre bot Twitch:${NC}"
echo ""

# Rendre les scripts exécutables
chmod +x start_kissbot.sh

# Détection OS et proposition LLM local
echo ""
echo -e "${PURPLE}🤖 CONFIGURATION LLM LOCAL (OPTIONNEL)${NC}"
echo -e "${PURPLE}====================================${NC}"

# Détecter l'OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${CYAN}🐧 Linux détecté - Ollama recommandé !${NC}"
    echo ""
    echo -e "${YELLOW}💡 Voulez-vous installer Ollama maintenant ? (y/N)${NC}"
    read -p ">>> " install_ollama
    
    if [[ $install_ollama =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}📥 Installation d'Ollama...${NC}"
        
        # Installation Ollama
        if curl -fsSL https://ollama.ai/install.sh | sh; then
            echo -e "${GREEN}✅ Ollama installé avec succès !${NC}"
            
            # Démarrer Ollama en service
            echo -e "${BLUE}🔧 Configuration du service Ollama...${NC}"
            sudo systemctl start ollama 2>/dev/null || true
            sudo systemctl enable ollama 2>/dev/null || true
            
            # Attendre que le service démarre
            sleep 3
            
            # Télécharger modèle recommandé
            echo -e "${BLUE}📦 Téléchargement du modèle Qwen 7B (recommandé)...${NC}"
            echo -e "${YELLOW}⏳ Cela peut prendre quelques minutes...${NC}"
            
            if ollama pull qwen2.5:7b-instruct; then
                echo -e "${GREEN}✅ Modèle Qwen 7B installé !${NC}"
                
                # Mise à jour automatique config.yaml pour Ollama
                echo -e "${BLUE}⚙️  Configuration automatique pour Ollama...${NC}"
                
                # Backup config original
                cp config.yaml config.yaml.backup
                
                # Mise à jour de l'endpoint pour Ollama
                sed -i 's|model_endpoint: "http://127.0.0.1:1234/v1/chat/completions"|model_endpoint: "http://127.0.0.1:11434/v1/chat/completions"|g' config.yaml
                sed -i 's|model_name: "llama-3.2-3b-instruct"|model_name: "qwen2.5:7b-instruct"|g' config.yaml
                
                echo -e "${GREEN}✅ Configuration Ollama appliquée !${NC}"
                echo -e "${CYAN}📝 Endpoint: http://127.0.0.1:11434 (port Ollama)${NC}"
                echo -e "${CYAN}🤖 Modèle: qwen2.5:7b-instruct${NC}"
            else
                echo -e "${YELLOW}⚠️  Erreur téléchargement modèle - configurez manuellement${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  Erreur installation Ollama - utilisez LM Studio ou OpenAI${NC}"
        fi
    else
        echo -e "${CYAN}💡 Pas de problème ! Vous pouvez :${NC}"
        echo -e "${CYAN}- Installer LM Studio (Windows/Mac): https://lmstudio.ai${NC}"
        echo -e "${CYAN}- Installer Ollama plus tard: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
        echo -e "${CYAN}- Utiliser uniquement OpenAI (config dans config.yaml)${NC}"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo -e "${CYAN}🪟 Windows détecté - LM Studio recommandé !${NC}"
    echo -e "${CYAN}📥 Téléchargez LM Studio: https://lmstudio.ai${NC}"
    echo -e "${CYAN}🤖 Modèle recommandé: Qwen 7B ou LLaMA 8B${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${CYAN}🍎 macOS détecté - LM Studio ou Ollama${NC}"
    echo -e "${CYAN}📥 LM Studio: https://lmstudio.ai (GUI)${NC}"
    echo -e "${CYAN}📥 Ollama: curl -fsSL https://ollama.ai/install.sh | sh (CLI)${NC}"
fi

echo ""

# Guide utilisateur
echo -e "${YELLOW}📝 ÉTAPES SUIVANTES:${NC}"
echo ""
echo -e "${BLUE}1.${NC} Consultez le guide complet APIs & Tokens:"
echo -e "   ${CYAN}cat COMPLETE_API_SETUP_GUIDE.md${NC}  # Guide détaillé TOUT"
echo -e "   ${CYAN}cat OLLAMA_LINUX_SETUP.md${NC}      # Guide Linux/Ollama complet"
echo ""
echo -e "${BLUE}2.${NC} Configuration EXPRESS (10 min max) :"
echo -e "   - Token Twitch : https://twitchtokengenerator.com/"
echo -e "   - App Twitch : https://dev.twitch.tv/console/apps"
echo -e "   - RAWG API (gratuit) : https://rawg.io/apidocs"
echo -e "   - OpenAI (optionnel) : https://platform.openai.com/"
echo ""
echo -e "${BLUE}3.${NC} Modifiez la configuration:"
echo -e "   ${CYAN}nano config.yaml${NC}  # ou votre éditeur préféré"
echo ""
echo -e "${BLUE}4.${NC} Validez votre configuration:"
echo -e "   ${CYAN}python3 validate_config.py${NC}  # Vérification automatique YAML"
echo ""
echo -e "${BLUE}5.${NC} Lancez votre bot:"
echo -e "   ${CYAN}./start_kissbot.sh${NC}"
echo ""

echo -e "${GREEN}✅ Installation terminée avec succès !${NC}"
echo ""
echo -e "${PURPLE}📂 Votre bot est installé dans: $(pwd)${NC}"
echo -e "${PURPLE}🚀 Prêt à lancer avec ./start_kissbot.sh${NC}"
echo ""
echo -e "${CYAN}🎊 Bienvenue dans KissBot V1 - Keep It Simple, Stupid!${NC}"