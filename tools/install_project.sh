#!/bin/bash

echo -e "\n🛠️  [SerdaBot] Installation interactive du projet..."
echo "---------------------------------------------"

# Chemins
PYTHON_BIN="./venv/bin/python3"
REQUIREMENTS="requirements.txt"
API_URL="http://127.0.0.1:8000/chat"
DEBUG=false
AUTO=false

# Parse des arguments
for arg in "$@"; do
    case $arg in
        --debug)
            DEBUG=true
            ;;
        --auto)
            AUTO=true
            ;;
    esac
done

# Fonction de log si debug activé
log_debug() {
    $DEBUG && echo -e "🐛 $1"
}

# Fonction pour vérifier un port
check_port() {
    local port=$1
    if lsof -i :$port | grep LISTEN > /dev/null; then
        pid=$(lsof -i :$port | grep LISTEN | awk '{print $2}' | head -n 1)
        process=$(ps -p "$pid" -o comm=)
        echo "⚠️  Port $port utilisé par $process (PID $pid)"
        return 1
    else
        echo "✅ Port $port disponible"
        return 0
    fi
}

# Vérifie venv
if [ ! -x "$PYTHON_BIN" ]; then
    echo "❌ Python venv introuvable. Lancez : python -m venv venv"
    exit 1
fi

echo "🔍 Python détecté : $($PYTHON_BIN -c 'import sys; print(sys.executable)')"

# Phase d'installation
echo "📦 Installation / mise à jour des dépendances..."
pip install -r "$REQUIREMENTS" 2>&1 | tee /tmp/install_log.txt

# Correction des RECORD manquants
if grep -q "uninstall-no-record-file" /tmp/install_log.txt; then
    echo "⚠️ Problème détecté lors de la désinstallation de certains paquets (RECORD manquant)."
    echo "🔁 Tentative de correction via --force-reinstall sur les paquets concernés..."

    grep "hint:.*pip install --force-reinstall" /tmp/install_log.txt | while read -r line; do
        fix=$(echo "$line" | grep -o "pip install --force-reinstall --no-deps [^ ]*")
        if [ -n "$fix" ]; then
            echo "   ➜ Correction du paquet : ${fix##* }"
            eval "$fix"
        fi
    done
fi

echo -e "\n🔍 [Phase 1] Vérification initiale des ports..."
check_port 8000
PORT_8000_FREE=$?
check_port 5000
PORT_5000_FREE=$?

# Confirmation ou auto
if $AUTO; then
    echo -e "\n🚀 [AUTO] Lancement automatique des serveurs..."
    CONFIRM="y"
else
    read -rp $'\n🚀 Lancer les serveurs (uvicorn + libretranslate) ? [y/N] ' CONFIRM
fi

# Démarrage des serveurs
if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
    echo "🔁 [SerdaBot] Lancement des serveurs..."

    if [ $PORT_8000_FREE -eq 0 ]; then
        echo "🚀 Démarrage du serveur IA..."
        nohup $PYTHON_BIN src/core/server/api_server.py > logs/api_server.log 2>&1 &
        sleep 2
        curl --max-time 5 "$API_URL" -s -o /dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Serveur IA démarré et joignable."
        else
            echo "❌ Le serveur IA n’est pas joignable. Test annulé."
        fi
    else
        echo "⏭️ Uvicorn déjà actif, démarrage ignoré."
    fi

    if [ $PORT_5000_FREE -eq 0 ]; then
        echo "🌍 Démarrage de LibreTranslate..."
        nohup libretranslate > logs/libretranslate.log 2>&1 &
        sleep 2
        echo "✅ LibreTranslate démarré et joignable."
    else
        echo "⏭️ LibreTranslate déjà en cours, démarrage ignoré."
    fi
fi

# Phase test
if $AUTO; then
    echo -e "\n🧪 [AUTO] Test de validation en cours..."
    python tools/test_chat_api.py $($DEBUG && echo "--debug") > /tmp/test_output.log
    if grep -q "Echo:" /tmp/test_output.log; then
        echo "⚠️  Le modèle IA ne semble pas actif. Réponse fallback détectée."
        echo "💡 Assurez-vous que le modèle est bien chargé via config.yaml → model_path / use_gpu / gpu_layers"
    fi
    cat /tmp/test_output.log
else
    read -rp $'\n🧪 Lancer un test de validation (test_chat_api.py) ? [y/N] ' TESTCONF
    if [[ $TESTCONF == "y" || $TESTCONF == "Y" ]]; then
        python tools/test_chat_api.py
    fi
fi

echo -e "\n🎉 Installation terminée ! SerdaBot est prêt à l’usage."
