# 🚀 SerdaBot - Installation Guide

Ce guide t'explique comment installer et faire tourner SerdaBot dans un environnement propre (Linux / WSL2 conseillé).

---

## 📦 1. Prérequis

- Python 3.10+
- `git` installé
- Connexion internet (pour les dépendances)
- Accès au dépôt GitHub

---

## 🧱 2. Cloner le projet

```bash
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot
```

---

## 🐍 3. Créer et activer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ⚙️ 5. Configurer le bot

```bash
cp src/config/config.sample.yaml src/config/config.yaml
```

Modifie `config.yaml` selon ton besoin (modèle, endpoint, token Twitch...).

---

## 🧪 6. Vérifier que tout est prêt

```bash
PYTHONPATH=src python tools/test_env.py
```

---

## 🚀 7. Lancer les serveurs (IA + LibreTranslate)

```bash
./tools/start_servers.sh
```

---

## 🤖 8. Lancer le bot Twitch

```bash
python src/chat/twitch_bot.py
```

---

## 📓 Notes

- Les logs sont stockés dans `logs/`
- Le modèle `.gguf` doit être présent dans `src/model/`
- Le fichier `config.yaml` n’est **pas versionné** (ajoute-le toi-même)

---

## 🧼 Désinstaller proprement

```bash
./tools/uninstall_serdabot.sh
```

---

**SerdaBot v0.1.0** - Par ElSerda 🤖
