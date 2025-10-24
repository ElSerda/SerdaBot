#!/bin/bash

# ============================================
# KissBot V1 - ULTRA-INSTALLEUR ONE-LINER
# ============================================
# Usage: curl -sSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/quick-install.sh | bash
# - Télécharge l'installeur principal
# - Lance l'installation complète
# - Suivi console temps réel de TOUT
# ============================================

set -e

# Configuration
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/install.sh"
TEMP_INSTALLER="/tmp/kissbot_installer.sh"

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🚀   KISSBOT V1 - ULTRA-INSTALLEUR${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "${YELLOW}📱 Installation ONE-LINER en cours...${NC}"
echo ""

# Vérification connexion internet
echo -e "${BLUE}🌐 Vérification connexion internet...${NC}"
if ! ping -c 1 github.com &> /dev/null; then
    echo -e "${RED}❌ Pas de connexion internet détectée${NC}"
    echo -e "${YELLOW}💡 Vérifiez votre connexion et réessayez${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Connexion internet OK${NC}"

# Vérification curl
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ curl non trouvé${NC}"
    echo -e "${YELLOW}💡 Installation curl...${NC}"
    
    # Tentative auto-install curl
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y curl
    elif command -v yum &> /dev/null; then
        sudo yum install -y curl
    elif command -v brew &> /dev/null; then
        brew install curl
    else
        echo -e "${RED}❌ Impossible d'installer curl automatiquement${NC}"
        echo -e "${YELLOW}💡 Installez curl manuellement et relancez${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ curl disponible${NC}"

echo ""
echo -e "${PURPLE}📥 Téléchargement de l'installeur principal...${NC}"

# Téléchargement de l'installeur
curl -fsSL "$INSTALL_SCRIPT_URL" -o "$TEMP_INSTALLER"

if [ ! -f "$TEMP_INSTALLER" ]; then
    echo -e "${RED}❌ Échec du téléchargement de l'installeur${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Installeur téléchargé avec succès${NC}"

# Rendre exécutable
chmod +x "$TEMP_INSTALLER"

echo ""
echo -e "${CYAN}🚀 Lancement de l'installation complète...${NC}"
echo -e "${YELLOW}📺 Suivez le processus en temps réel :${NC}"
echo -e "${YELLOW}----------------------------------------${NC}"

# Lancer l'installeur principal avec suivi complet
"$TEMP_INSTALLER"

# Nettoyage
rm -f "$TEMP_INSTALLER"

echo ""
echo -e "${GREEN}🎊 Installation ONE-LINER terminée !${NC}"
echo -e "${PURPLE}🎯 KissBot V1 est prêt à l'emploi !${NC}"