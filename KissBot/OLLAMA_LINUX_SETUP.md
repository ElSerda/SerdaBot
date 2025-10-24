# 🐧 KissBot Linux + Ollama Setup Guide

**Installation complète KissBot sur Linux avec Ollama - Alternative open source à LM Studio**

---

## 🎯 Quick Setup (Linux ONE-LINER)

```bash
# Installation complète automatique
curl -fsSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/KissBot/quick-install.sh | bash
```

**⚡ Ce script fait TOUT :**
- ✅ Installe Python 3.12+ et pip
- ✅ Clone KissBot repository
- ✅ Crée virtual environment automatiquement  
- ✅ Installe dependencies Python
- ✅ **Installe Ollama automatiquement**
- ✅ **Télécharge modèle Qwen 7B**
- ✅ Configure config.yaml avec Ollama
- ✅ Lance le bot immédiatement

---

## 🔧 Installation Manuelle Détaillée

### 1. Prérequis Linux

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3.12 python3.12-venv python3-pip git curl

# Fedora/RHEL
sudo dnf install -y python3.12 python3-pip git curl

# Arch Linux
sudo pacman -S python python-pip git curl
```

### 2. Installation Ollama

**Option A: Script officiel (Recommandé)**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Option B: Package managers**
```bash
# Ubuntu/Debian (via snap)
sudo snap install ollama

# Arch Linux (AUR)
yay -S ollama-bin

# Fedora (via copr)
sudo dnf copr enable ganto/ollama
sudo dnf install ollama
```

### 3. Démarrage Ollama en service

```bash
# Démarrer le service Ollama
sudo systemctl start ollama
sudo systemctl enable ollama

# Vérifier que ça fonctionne
curl http://localhost:11434/api/version
# Doit retourner: {"version":"0.x.x"}
```

### 4. Téléchargement des modèles

**Qwen 7B (Recommandé - Excellent pour français):**
```bash
ollama pull qwen2.5:7b-instruct
```

**Alternatives selon votre RAM:**
```bash
# RAM < 8GB - Modèle léger
ollama pull qwen2.5:3b-instruct

# RAM > 16GB - Modèle performant
ollama pull qwen2.5:14b-instruct

# Alternative LLaMA
ollama pull llama3.1:8b-instruct
```

**Vérification:**
```bash
# Lister les modèles installés
ollama list

# Tester le modèle
ollama run qwen2.5:7b-instruct
>>> Hello! How are you?
>>> /bye
```

### 5. Installation KissBot

```bash
# Clone repository
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot/KissBot

# Virtual environment
python3.12 -m venv kissbot-venv
source kissbot-venv/bin/activate

# Dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configuration KissBot pour Ollama

**Éditer `config.yaml`:**
```yaml
twitch:
  token: "oauth:YOUR_TWITCH_TOKEN"
  client_id: "YOUR_TWITCH_CLIENT_ID"
  channels: ["votre_channel"]

llm:
  enabled: true
  local_llm: true
  provider: "local"
  model_endpoint: "http://127.0.0.1:11434/v1/chat/completions"  # Port Ollama
  model_name: "qwen2.5:7b-instruct"  # Modèle téléchargé
  max_tokens: 400
  temperature: 0.7

apis:
  rawg_key: "YOUR_RAWG_KEY"
  openai_key: ""  # Optionnel (fallback)
```

### 7. Validation et Tests

```bash
# Valider configuration
python validate_config.py

# Test Ollama connection
curl -X POST http://127.0.0.1:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b-instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# Lancer KissBot
python main.py
```

---

## ⚡ Performance Ollama vs LM Studio

| Aspect | Ollama | LM Studio |
|--------|---------|-----------|
| **Installation** | 1 commande | Interface graphique |
| **RAM Usage** | 🟢 Optimisé | 🟡 Plus lourd |
| **CPU Usage** | 🟢 Efficace | 🟡 Moyen |
| **Models** | CLI simple | Interface drag & drop |
| **API** | Port 11434 | Port 1234 |
| **Logs** | `journalctl -u ollama` | Interface GUI |
| **Updates** | `ollama pull model` | Auto via GUI |

**Verdict:** Ollama = 🐧 **Perfect pour Linux/Serveurs**, LM Studio = 🖥️ **Perfect pour Windows/Desktop**

---

## 🔧 Troubleshooting Linux + Ollama

### Ollama ne démarre pas

```bash
# Vérifier le service
sudo systemctl status ollama
sudo systemctl restart ollama

# Vérifier les logs
journalctl -u ollama -f

# Permissions utilisateur
sudo usermod -a -G ollama $USER
newgrp ollama
```

### Port 11434 occupé

```bash
# Tuer les processus Ollama
sudo pkill ollama

# Vérifier le port
sudo ss -tlnp | grep 11434

# Redémarrer proprement
sudo systemctl restart ollama
```

### Modèle ne répond pas

```bash
# Réinstaller le modèle
ollama rm qwen2.5:7b-instruct
ollama pull qwen2.5:7b-instruct

# Test direct
ollama run qwen2.5:7b-instruct "Dis bonjour"
```

### KissBot ne trouve pas Ollama

**Config.yaml - Vérifier l'endpoint:**
```yaml
llm:
  model_endpoint: "http://127.0.0.1:11434/v1/chat/completions"  # Ollama
  # PAS: "http://127.0.0.1:1234/v1/chat/completions"  # LM Studio
```

### RAM insuffisante

```bash
# Modèle plus léger
ollama pull qwen2.5:3b-instruct

# Ou configuration quantized
ollama pull qwen2.5:7b-instruct-q4_0
```

---

## 🚀 Scripts de Démarrage Linux

### Service Systemd pour KissBot

**Créer `/etc/systemd/system/kissbot.service`:**
```ini
[Unit]
Description=KissBot Twitch Bot
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=serda
WorkingDirectory=/home/serda/SerdaBot/KissBot
Environment=PATH=/home/serda/SerdaBot/KissBot/kissbot-venv/bin
ExecStart=/home/serda/SerdaBot/KissBot/kissbot-venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Activer:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable kissbot
sudo systemctl start kissbot

# Vérifier
sudo systemctl status kissbot
journalctl -u kissbot -f
```

### Script de mise à jour automatique

**Créer `update_kissbot.sh`:**
```bash
#!/bin/bash
cd /home/serda/SerdaBot/KissBot

# Stop bot
sudo systemctl stop kissbot

# Update code
git pull origin kissbot

# Update dependencies
source kissbot-venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Ollama models
ollama pull qwen2.5:7b-instruct

# Restart
sudo systemctl start kissbot

echo "✅ KissBot updated and restarted!"
```

---

## 📊 Monitoring Ollama + KissBot

### Resources monitoring

```bash
# RAM/CPU usage
htop
watch -n 1 'ps aux | grep -E "(ollama|python.*main.py)"'

# GPU usage (si NVIDIA)
nvidia-smi -l 1

# Ollama metrics
curl http://localhost:11434/api/ps
```

### Logs centralisés

```bash
# Suivre tous les logs
journalctl -u ollama -u kissbot -f

# Logs par service
journalctl -u ollama --since "1 hour ago"
journalctl -u kissbot --since "1 hour ago"
```

---

## 🎯 Conclusion

**Linux + Ollama = Configuration idéale pour :**
- ✅ **Serveurs dédiés** (VPS, home server)
- ✅ **Performance** (moins de overhead)
- ✅ **Stabilité** (services systemd)
- ✅ **Cost-effectiveness** (pas de licence)
- ✅ **Automation** (scripts, crontabs)

**Windows + LM Studio = Idéal pour :**
- ✅ **Desktop development** 
- ✅ **GUI preference**
- ✅ **Drag & drop models**

**KissBot supporte les DEUX parfaitement !** 🎯

---

*Questions ? Join el_serda's stream ou open GitHub issue !* 🎮✨