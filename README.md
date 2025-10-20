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
| `!ask <question>` | **NEW:** Smart routing system - Game questions use RAWG data (0% hallucinations), general questions use LLM. 20,000x faster for game facts. |
| `!game <title>` | Search for a video game and get detailed info: developers, publishers, platforms, ratings (via RAWG API with cache). |
| `!trad <message>` | Translate a message into the stream's language (default: French). |
| Mention bot name | Trigger a casual/fun response with geek humor (`!chill` behavior). |

---

## 🧠 Powered by

- **Qwen 2.5-3B-Instruct-Q4_K_M** (local via LM Studio) - Upgraded from 1.5B for better quality
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

### Linux / macOS

```bash
# Install dependencies
pip install -r requirements.txt

# Start servers (model + libretranslate)
bash tools/start_servers.sh

# Run the bot
./start_bot.sh
```

### Windows

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the bot
.\start_bot.ps1
```

📖 **Full installation guides:**
- [INSTALL.md](INSTALL.md) — Linux/macOS
- [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) — Windows 10/11

## ❤️ Credit

Built by El Serda ☕ — for streamers, by a streamer.  
**Co-developed with AI Dream Team (GPT & Claude)** 🤖  
Fork it, remix it, improve it.  
Want to support? → [ko-fi.com/el_serda](https://ko-fi.com/el_serda)

---

## 📄 License

AGPL-3.0 — because open AI tools should remain open.
