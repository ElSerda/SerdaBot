![CI](https://github.com/ElSerda/SerdaBot/actions/workflows/ci.yml/badge.svg)

# 🤖 SerdaBot – Twitch AI Assistant (v0.1.0-alpha)

![Version](https://img.shields.io/badge/version-v0.1.0--alpha-orange)
![License](https://img.shields.io/badge/license-AGPL--v3-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Status](https://img.shields.io/badge/status-Alpha-yellow)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

SerdaBot is a lightweight, multilingual Twitch chat assistant powered by Qwen 2.5-3B (local LLM via LM Studio). Designed for simplicity, extensibility, and fun.

---

## ⚙️ Features

| Command | Description |
|--------|-------------|
| `!ask <question>` | **NEW:** Smart routing system - Game questions use RAWG data (0% hallucinations), general questions use LLM. 20,000x faster for game facts. **Works without LLM** (fallback mode). |
| `!game <title>` | Search for a video game and get detailed info: developers, publishers, platforms, ratings (via RAWG API with cache). |
| `!trad <message>` | Translate a message into the stream's language (default: French). |
| Mention bot name | Trigger a casual/fun response with geek humor (`!chill` behavior). **Works without LLM** (fallback mode). |

**🤖 LLM Optional** : SerdaBot works perfectly with or without a local LLM. See [LLM Fallback](docs/LLM_FALLBACK.md) for details.

---

## 🧠 Powered by

- **Qwen 2.5-3B-Instruct-Q4_K_M** (local via LM Studio) - Upgraded from 1.5B for better quality — **OPTIONAL**
- **Automatic fallback** - Bot works perfectly without LLM (pre-defined responses)
- **RAWG API** - Primary source for game data (100% factual, zero hallucinations)
- **Intelligent routing** - RAWG for game facts, Wikipedia for context, LLM for general questions
- Optimized prompts (SYSTEM_CHILL_FINAL: geek humor, anti-hallucination rules)
- LibreTranslate (local or remote) for multilingual support
- TwitchIO for real-time chat integration
- **Performance**: 0.2ms (RAWG cache) to 6000ms (LLM), 20,000x improvement on game questions

---

## 📁 Project Structure

- `src/core/commands/` → Each command (`ask`, `game`, `trad`, `chill`)
- `src/utils/` → Shared helpers (`llm`, `game_utils`, `translation`, etc.)
- `tools/` → Scripts to start/stop servers, test locally
- `config/` → YAML-based config system
- [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) → Full architecture overview

---

## 🚀 Quick Start

### Première installation

```bash
# 1. Cloner le repo
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot

# 2. Créer le workspace local (hors Git)
mkdir -p ../SerdaBot-local/config

# 3. Copier et remplir la config
cp src/config/config.example.yaml ../SerdaBot-local/config/config.yaml
nano ../SerdaBot-local/config/config.yaml  # Remplacer les XXXXXXX par tes vraies clés

# 4. Installer les dépendances
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Lancer le bot
./start_bot.sh  # Détecte automatiquement ../SerdaBot-local/config/config.yaml
```

### Lancement rapide (après installation)

```bash
# Linux / macOS
./start_bot.sh

# Windows
.\start_bot.ps1
```

📖 **Guides détaillés :**
- [CONFIG_SETUP.md](docs/CONFIG_SETUP.md) — Configuration et sécurité
- [INSTALL.md](INSTALL.md) — Installation complète (Linux/macOS)
- [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) — Installation Windows 10/11

---

## 📁 Structure du projet

```
/home/ton_user/
├── SerdaBot/              # Repo Git (public, partageable)
│   ├── src/               # Code source
│   ├── config/
│   │   ├── config.example.yaml  # Template anonymisé
│   │   └── config.sample.yaml   # Config minimale (tests/CI)
│   └── start_bot.sh       # Détecte config locale automatiquement
│
└── SerdaBot-local/        # Workspace privé (JAMAIS dans Git)
    ├── config/
    │   └── config.yaml    # TA config avec tokens réels
    ├── personnal/         # Notes, TODOs
    └── test-archives/     # Tests one-shot
```

**Philosophie :** Séparation stricte code public (Git) ↔ données personnelles (hors Git).  
Aucun risque de leak de tokens, 100% fork-friendly. 🔒

---

## 🤖 LLM Optional Mode

**SerdaBot works with or without a local LLM!**

- ✅ **With LLM** (LM Studio): Full AI-powered responses
- ✅ **Without LLM**: Automatic fallback to pre-defined fun responses
- ✅ **CI/CD Ready**: Tests pass without requiring GPU
- ✅ **Fork-Friendly**: Clone → run → works immediately

**Detection**: Automatic at startup (checks `http://localhost:1234/v1/models`)  
**Fallback**: Randomized responses keeping the bot's personality  
**Override**: `export LLM_MODE=disabled` to force fallback mode

See [docs/LLM_FALLBACK.md](docs/LLM_FALLBACK.md) for full documentation.

## ❤️ Credit

Built by El Serda ☕ — for streamers, by a streamer.  
**Co-developed with AI Dream Team (GPT & Claude)** 🤖  
Fork it, remix it, improve it.  
Want to support? → [ko-fi.com/el_serda](https://ko-fi.com/el_serda)

---

## 📄 License

AGPL-3.0 — because open AI tools should remain open.
