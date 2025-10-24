![CI](https://github.com/ElSerda/SerdaBot/actions/workflows/ci.yml/badge.svg)

# 🚀 SerdaBot Repository - Now featuring KissBot V1

![Version](https://img.shields.io/badge/KissBot-V1.0.0-brightgreen)
![License](https://img.shields.io/badge/license-AGPL--v3-blue)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![KISS](https://img.shields.io/badge/architecture-KISS-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

## 🎯 **KissBot V1 - KISS Architecture Rewrite** ⭐ **RECOMMENDED**

**Ultra-lean Twitch bot with 73% code reduction - from 7,468 lines to 2,021 lines**

### 🔥 **Ready for Production:**
- ✅ **ONE-LINER Installation** (Linux/Windows)  
- ✅ **90-99% Game Lookup Reliability**  
- ✅ **Model-Specific Prompting** (Qwen, LLaMA, Mistral)  
- ✅ **Cascade Fallback System** (Local → Cloud → Static)  
- ✅ **Complete Documentation & Testing**  

**👉 [Go to KissBot V1](KissBot/) 👈**

---

## 📊 **Architecture Comparison**

| Feature | SerdaBot (Legacy) | **KissBot V1** |
|---------|------------------|---------------|
| **Lines of Code** | 7,468 | **2,021 (-73%)** |
| **Architecture** | Complex modules | **3-Pillar KISS** |
| **Installation** | Multi-step setup | **ONE-LINER** |
| **LLM Integration** | Single provider | **Model-specific prompts** |
| **Game Lookup** | Basic search | **Confidence scoring** |
| **Error Handling** | Basic | **Comprehensive fallbacks** |
| **Documentation** | Scattered | **Complete guides** |
| **Status** | Legacy/Archive | **✅ Production Ready** |

---

## 🎮 **KissBot V1 Features**

### 🤖 Commands
- `!gameinfo <name>` / `!gi` - Game info with 90-99% reliability
- `!gamecategory` / `!gc` - Auto-detect current stream game  
- `!ask <question>` - Ask LLM with smart fallbacks
- `!ping`, `!stats`, `!help`, `!cache` - Utility commands

### 🧠 Intelligence
- **Local LLM** (LM Studio/Ollama) → **OpenAI** → **Static responses**
- **Model detection** with optimized prompts per model type
- **Anti-hallucination** system for factual responses

### 🎯 **Get Started in 30 seconds:**
```bash
# Linux/Mac ONE-LINER
curl -fsSL https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/KissBot/quick-install.sh | bash

# Windows ONE-LINER  
iwr -Uri "https://raw.githubusercontent.com/ElSerda/SerdaBot/kissbot/KissBot/quick-install.ps1" | iex
```

---

## �️ **SerdaBot Legacy (Archive)**

<details>
<summary>📚 <strong>View Legacy SerdaBot Documentation</strong> (v0.1.0-alpha)</summary>

### Legacy Features
- `!ask <question>` - Smart routing system with LLM
- `!game <title>` - Basic game search via RAWG API  
- `!trad <message>` - Translation support
- Mention responses with geek humor

### Legacy Architecture  
- **7,468 lines** of complex modular code
- Multiple LLM providers with basic prompts
- Complex configuration system
- Multi-step installation process

**⚠️ Note:** Legacy SerdaBot is archived and no longer maintained. Please use **KissBot V1** for production deployments.

**📁 Legacy Structure:**
- `src/core/commands/` → Legacy command implementations
- `src/utils/` → Legacy shared helpers  
- `tools/` → Legacy scripts and utilities
- `config/` → Legacy YAML configuration
- [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) → Legacy architecture overview

</details>

---

## 🏗️ **Development & Architecture**

- **KissBot V1** follows KISS principles (Keep It Simple, Stupid)
- **3-Pillar Architecture:** Commands, Intelligence, Twitch
- **Model-Specific Prompting:** Automatic detection and optimization
- **Comprehensive Testing:** 100% KISS alignment validation

**📖 Documentation:**
- [KissBot README](KissBot/README.md) - Complete installation and usage
- [Commands Guide](KissBot/COMMANDS.md) - Detailed command documentation  
- [Production Checklist](KissBot/PRODUCTION_CHECKLIST.md) - Deployment validation
- [Linux/Ollama Setup](KissBot/OLLAMA_LINUX_SETUP.md) - Complete Linux guide

---

## 🤝 **Contributing**

We welcome contributions! Please:
1. **Use KissBot V1** as the base for new features
2. Follow KISS architecture principles  
3. Maintain comprehensive documentation
4. Test thoroughly before submitting PRs

**Development Setup:**
```bash
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot/KissBot
./quick-install.sh  # Sets up development environment
```

---

## ❤️ **Credits**

**Built by El Serda** ☕ — for streamers, by a streamer  
**Co-developed with AI Dream Team** (GPT & Claude) 🤖  

Fork it, remix it, improve it!  
**Want to support?** → [ko-fi.com/el_serda](https://ko-fi.com/el_serda)

---

## 📄 **License**

**AGPL-3.0** — because open AI tools should remain open.

**🚀 Ready to get started? [Jump to KissBot V1](KissBot/) and be running in 30 seconds!**
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
