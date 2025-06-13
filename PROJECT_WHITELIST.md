# ✅ SerdaBot — Project Whitelist

This document lists all **essential files and folders** that must be kept in the repository.
Everything else should be excluded, ignored, or moved to a dev-specific area (`tools/`, `.gitignore`, etc.)

---

## 📚 Documentation
- `README.md`
- `PROJECT_STRUCTURE.md`
- `LICENSE` (optional)

## 🔧 Project Configuration
- `pyproject.toml`
- `.gitignore`
- `.pylintrc`
- `config.sample.yaml`

## ⚙️ Source Code (in `src/`)
- `src/chat/`
- `src/core/`
- `src/utils/`
- `src/prompts/`
- `src/config/`
- `src/model/` (optional, for local models)
- `__init__.py` files in all submodules

## 🧪 Tests
- `tests/` directory with unit tests

## 🛠️ Dev Tools (keepers only)
- `tools/start_servers.sh`
- `tools/stop_servers.sh`
- `tools/reload_servers.sh`
- `tools/install_project.sh`
- `tools/uninstall_serdabot.sh` (optional)
- `tools/test_*.py` (optional dev test files)

## 🚀 Entry Point
- `start_bot.sh`

---

## ❌ To Be Removed or Ignored
- `LIVE_TEST_TODO.md`, `zip_light.sh`
- `.DS_Store`, `*.bak`, `*.Zone.Identifier`
- `ruff_output.txt`, `*.log`, `*.zip`
- `code_review_prompt.txt`, `*_files.txt`, `ghost_git_files.txt`
- IDE cache/configs (`.vscode-settings-backup.json`, `.idea/`, `.vscode/`)

---

Keep it clean. Keep it public-ready. 💡
