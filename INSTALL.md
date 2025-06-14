# INSTALL.md — SerdaBot v0.1.0

## 1. Prerequisites

- Python 3.10+
- Git
- `libretranslate` (CLI or install via `pip`)
- Optional: virtual environment (`venv`)

---

## 2. Prepare Your Workspace

```bash
mkdir serdabot-test && cd serdabot-test
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot
```

---

## 3. Create & Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configuration

```bash
cp src/config/config.sample.yaml src/config/config.yaml
```

---

## 6. Install with Script (Optional, Auto Mode)

```bash
bash tools/install_project.sh --auto
```

This script installs dependencies, checks ports, launches servers, and runs a test.

---

## 7. Environment Check (Manual)

```bash
PYTHONPATH=src python tools/test_env.py
```

---

## 8. Server Management

### Start the servers

```bash
bash tools/start_servers.sh
```

### Reload the servers

```bash
bash tools/reload_servers.sh
```

### Stop the servers

```bash
bash tools/stop_servers.sh
```

---

## 9. Start the Bot

```bash
PYTHONPATH=src python src/chat/twitch_bot.py
```

---

## 10. Uninstall (Clean Exit)

```bash
bash tools/uninstall_serdabot.sh
```

---

## Notes

- Logs are stored in `./logs/`
- GGUF models should be placed in `src/model/`
- Ports used:
  - 8000 → IA Server (uvicorn)
  - 5000 → LibreTranslate

---

## License

This project is licensed under the AGPLv3 — see [LICENSE](LICENSE) for details.
