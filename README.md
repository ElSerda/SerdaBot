
# 🤖 SerdaBot – Twitch AI Assistant (v0.1.0)

![Version](https://img.shields.io/badge/version-v0.1.0-green)
![License](https://img.shields.io/badge/license-AGPL--v3-blue)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Status](https://img.shields.io/badge/status-Stable-brightgreen)

SerdaBot is a lightweight, multilingual Twitch chat assistant powered by a local Mistral-based language model and FastAPI. Designed for simplicity, extensibility, and fun.

---

## ⚙️ Features

| Command | Description |
|--------|-------------|
| `!ask <question>` | Ask a direct question to the bot and get a concise, tagged answer. |
| `!game <title>` | Search for a video game and get a localized summary (via IGDB + Steam). |
| `!trad <message>` | Translate a message into the stream’s language (default: French). |
| Mention bot name | Trigger a casual/fun response (`!chill` behavior). |

---

## 🧠 Powered by

- Mistral-7B (Quantized GGUF) loaded via `ctransformers`
- FastAPI local endpoint (`/chat`)
- LibreTranslate (local or remote) for multilingual support
- TwitchIO for real-time chat integration

---

## 📁 Project Structure

- `src/core/commands/` → Each command (`ask`, `game`, `trad`, `chill`)
- `src/utils/` → Shared helpers (`llm`, `game_utils`, `translation`, etc.)
- `tools/` → Scripts to start/stop servers, test locally
- `config/` → YAML-based config system
- [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) → Full architecture overview

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start servers (model + libretranslate)
bash tools/start_servers.sh

# Run the bot
python src/chat/twitch_bot.py
```

---

## 🔒 Before Git Push

- [x] Anonymize `config.yaml` → replace with `config.sample.yaml`
- [x] Add `.gitignore` for `.gguf`, `config.yaml`, and logs
- [x] Black + Ruff + Pylint clean
- [x] Confirm commands work: `!ask`, `!game`, `!trad`, `mention`
- [x] Include bilingual `README.md` if targeting FR/EN streamers (optional)

---

## ❤️ Credit

Built by El Serda ☕ — for streamers, by a streamer.
Fork it, remix it, improve it.  
Want to support? → [ko-fi.com/el_serda](https://ko-fi.com/el_serda)

---

## 📄 License

AGPL-3.0 — because open AI tools should remain open.
