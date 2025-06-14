# 🗂️ Project Structure – SerdaBot

This document outlines the architecture of the SerdaBot repository.
It is designed to help new contributors and users understand the purpose of each folder and file.

---

## 🌳 Directory Overview

```
SerdaBot/
├── config/                    # Bot configuration loading system
├── core/
│   ├── commands/              # All Twitch chat command handlers (!ask, !game, etc.)
│   ├── server/                # FastAPI server (LLM proxy endpoint)
│   ├── igdb_api.py            # IGDB API interactions
│   └── rawg_api.py            # (Optional) RAWG API fallback
├── utils/                     # Utility modules: translation, LLM interface, logging
├── model/                     # Local .gguf model files (ignored in Git)
├── chat/
│   └── twitch_bot.py          # TwitchIO bot core (message routing & logic)
├── prompts/                   # Prompt templates used for LLM queries
├── tools/                     # Scripts to manage the bot and services
├── tests/                     # (Optional) Test files (if using pytest or custom)
├── LICENSE                    # AGPLv3 license file
├── README.md                  # Main documentation
├── INSTALL.md                # Setup instructions for users
├── RELEASE_v0.1.0.md         # Release notes for v0.1.0
├── requirements.txt           # Minimal dependency list
├── pyproject.toml             # Project & tool configuration (Black, Ruff, Pylint)
└── .gitignore                 # Ignore secrets, models, logs, venv, etc.
```

---

## 🧠 Folder Details

### `config/`
Contains:
- `config.py`: loads and validates YAML config
- `config.sample.yaml`: template to copy as `config.yaml`

### `core/commands/`
Implements:
- `ask_command.py`: answers questions using LLM
- `game_command.py`: fetches game details (IGDB, Steam, etc.)
- `chill_command.py`: relaxed prompts for casual responses
- `trad_command.py`: language detection & translation

### `utils/`
Grouped logic helpers:
- `llm.py`: handles prompt formatting and model queries
- `translation.py`: interface with LibreTranslate
- `translation_postprocess.py`: cleanup logic after translation
- `translation_utils.py`, `log.py`, `clean.py`, etc.

### `model/`
Place your local `.gguf` LLM model here.
Make sure `.gitignore` excludes this folder.

### `chat/twitch_bot.py`
Main TwitchIO bot logic:
- Handles commands
- Sends messages
- Integrates all modules

### `prompts/`
Text prompts used to format LLM input (`prompt_game_fr.txt`, etc.)

### `tools/`
Scripts to control:
- `start_servers.sh`, `stop_servers.sh`, `reload_servers.sh`
- `install_project.sh`: post-clone helper script
- `test_env.py`: checks environment, model, and endpoints

---

## 📝 Notes

- All entry points use relative imports (managed via `PYTHONPATH=src`)
- You can run the bot using:
  ```bash
  ./start_bot.sh
  ```
- Model API runs via FastAPI at `http://localhost:8000/chat`

---

💡 For development or contribution tips, check out `CONTRIBUTING.md` (coming soon).