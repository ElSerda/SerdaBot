# 📁 Project Structure – SerdaBot

This document describes the architecture of the project and the role of each main folder.

---

## 🔧 `core/` – Bot engine & Twitch logic

- `core/commands/` → All Twitch commands (e.g., `!ask`, `!game`, `!chill`, `!trad`)
- `core/server/` → FastAPI model API
- `core/igdb_api.py` → IGDB integration
- `core/rawg_api.py` → Future RAWG integration
- `core/helpers/` → Optional helpers for the core (currently unused)

---

## ⚙️ `utils/` – Shared utilities

- `llm.py` → Query the model and clean responses
- `translation.py` → Language detection and translation (LibreTranslate)
- `game_utils.py` → Game formatting tools (platforms, slugs, summaries)
- `ask_utils.py`, `chill_utils.py` → Prompt handling for specific commands

---

## 📡 `chat/` – Twitch interface

- `twitch_bot.py` → Main bot loop and event handling (TwitchIO)

---

## 🧪 `tools/` – Dev tools

- `start_servers.sh`, `stop_servers.sh` → Launch LLM & LibreTranslate
- `test_chat_api.py`, `test_igdb.py` → Test scripts for dev/debug

---

## ⚙️ Root-level files

- `config.yaml` → Private runtime config (not pushed)
- `config.sample.yaml` → Public example config
- `pyproject.toml` → Tooling setup (Black, Ruff, Pylint)
- `.gitignore` → Ignore models, logs, configs
- `README.md` → Main project doc
- `PROJECT_STRUCTURE.md` → This file
