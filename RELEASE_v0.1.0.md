# 🚀 SerdaBot v0.1.0 — Initial Public Release

SerdaBot is now officially live, open-source, and ready to moderate, answer, translate and chill — **without requiring an LLM**.  
This version is designed for clean installation, reproducibility, and ease of contribution.

---

## ✨ Features

- 🎮 `!game` — Fetch game summaries (IGDB/Steam) with platform, release date, mode, and translation fallback (LibreTranslate)
- 🧠 `!ask` — Ask any question in natural language (via local LLM)
- 🧊 `!chill` — Generate relaxed, friendly banter from the bot
- 🌍 `!trad` — Translate messages from any language to French (no LLM required)

---

## 🔧 Technical

- Modular command system (`core/commands/`)
- Translation & fallback engine (`utils/translation_utils.py`)
- Custom prompt loading system for each command (`prompts/`)
- Web servers for LLM & LibreTranslate (`start_servers.sh`)
- Configurable YAML-based settings
- Local-only, privacy-friendly runtime
- Works under **Linux + WSL2**, tested on Python 3.12+

---

## 📦 Setup

Check [`INSTALL.md`](./INSTALL.md) to get started in 5 minutes.

---

## 🛣️ Next Steps

- Refactor `!game` summaries using the LLM as post-translator (optional)
- Add a `!system` command to monitor server stats locally
- Web dashboard for admins (v0.3.0+)
- Multi-language reply support

---

Thank you for testing, contributing, or just reading!
**Made with ⚙️, 💬, and 🧠 by ElSerda + ChatGPT (Mastercraft Mode)**.

## 📝 License
SerdaBot is licensed under the [GNU AGPLv3](./LICENSE).