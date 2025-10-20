# 🔧 Configuration de SerdaBot

Ce guide explique comment configurer SerdaBot avec le nouveau système de configuration séparé.

---

## 🎯 Philosophie

**Principe :** Séparer strictement le code public (Git) des données personnelles (hors Git).

```
/home/ton_user/
├── SerdaBot/              # Repo Git (public, partageable)
│   ├── src/
│   ├── config/
│   │   ├── config.example.yaml  # Template anonymisé
│   │   └── config.sample.yaml   # Config minimale pour tests
│   └── start_bot.sh       # Détecte automatiquement la config locale
│
└── SerdaBot-local/        # Workspace privé (JAMAIS dans Git)
    ├── config/
    │   ├── config.yaml    # TA config avec tokens réels
    │   └── .env           # Variables d'environnement
    ├── personnal/         # Notes, TODOs
    ├── test-archives/     # Tests one-shot
    └── dumps/             # Exports, logs
```

---

## 🚀 Setup initial (première installation)

### 1. Créer le workspace local

```bash
# À la racine de ton dossier de projets
mkdir -p SerdaBot-local/config
```

### 2. Copier le template de config

```bash
# Depuis le dossier SerdaBot/
cp src/config/config.example.yaml ../SerdaBot-local/config/config.yaml
```

### 3. Remplir les vraies valeurs

Ouvre `../SerdaBot-local/config/config.yaml` et remplace :

```yaml
twitch:
  token: "oauth:XXXXXXX"          # Depuis twitchtokengenerator.com
  client_id: "XXXXXXX"            # Depuis dev.twitch.tv
  client_secret: "XXXXXXX"
  bot_id: "123456789"             # User ID de ton bot

rawg:
  api_key: "XXXXXXX"              # Depuis rawg.io/apidocs

openai:
  api_key: "sk-proj-XXXXXXX"      # Si tu utilises OpenAI (optionnel)
```

### 4. Créer un fichier .env (optionnel)

Si tu préfères utiliser des variables d'environnement :

```bash
# ../SerdaBot-local/.env
TWITCH_TOKEN=oauth:XXXXXXX
RAWG_API_KEY=XXXXXXX
OPENAI_API_KEY=sk-proj-XXXXXXX
```

### 5. Lancer le bot

```bash
./start_bot.sh
```

Le script détectera automatiquement `../SerdaBot-local/config/config.yaml` ✅

---

## 🔍 Ordre de priorité

Quand tu lances le bot, il cherche la config dans cet ordre :

1. **Variable d'environnement** `SERDABOT_CONFIG` (si définie)
2. **Config locale** : `../SerdaBot-local/config/config.yaml` ✅ (recommandé)
3. **Config repo** : `src/config/config.yaml`
4. **Config sample** : `src/config/config.sample.yaml` (fallback pour tests)

### Exemple : Override manuel

```bash
# Utiliser une config spécifique
export SERDABOT_CONFIG="/path/to/my-custom-config.yaml"
./start_bot.sh
```

---

## 📁 Structure complète de SerdaBot-local/

Voici une structure suggérée pour ton workspace local :

```
SerdaBot-local/
├── config/
│   ├── config.yaml          # Config principale (TOKENS RÉELS)
│   ├── config-staging.yaml  # Config de test (autre compte)
│   └── .env                 # Variables d'environnement
│
├── personnal/
│   ├── TODO.md              # Ta liste de tâches
│   ├── IDEAS.md             # Idées de features
│   └── notes/               # Notes diverses
│
├── test-archives/
│   ├── test_cache_v1.py     # Anciens tests one-shot
│   └── benchmark_llm.py
│
├── session-notes/
│   ├── SESSION_2025-01-15.md   # Récaps de debug
│   └── HOTFIX_cache_bug.md
│
├── dumps/
│   ├── cache_dump_2025-01.json
│   └── igdb_export.txt
│
└── scripts/
    └── migrate_old_cache.py    # Scripts perso
```

---

## 🛡️ Sécurité

### ✅ Ce qui est safe (dans Git)

- `src/config/config.example.yaml` — Template anonymisé
- `src/config/config.sample.yaml` — Config minimale pour tests
- `.gitignore` — Bloque `config.yaml`, `.env`, etc.

### ❌ Ce qui ne doit JAMAIS être dans Git

- `../SerdaBot-local/config/config.yaml` — Tokens réels
- `.env` — Variables d'environnement
- `data/devs.json` — Liste des admins
- `personnal/` — Notes perso

---

## 🧪 Pour les contributeurs / forks

Si quelqu'un clone le repo, voici ce qu'il doit faire :

```bash
# 1. Cloner le repo
git clone https://github.com/ElSerda/SerdaBot.git
cd SerdaBot

# 2. Créer le workspace local
mkdir -p ../SerdaBot-local/config

# 3. Copier le template
cp src/config/config.example.yaml ../SerdaBot-local/config/config.yaml

# 4. Remplir les vraies valeurs
nano ../SerdaBot-local/config/config.yaml

# 5. Installer les dépendances
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Lancer le bot
./start_bot.sh
```

✅ **Aucun fichier sensible dans Git, tout est reproductible !**

---

## 🔧 Troubleshooting

### Le bot ne trouve pas la config

**Symptôme :**
```
❌ Aucune config trouvée ! Vérifie que tu as bien :
  1. Créé ../SerdaBot-local/config/config.yaml OU
  2. Copié src/config/config.example.yaml → src/config/config.yaml
```

**Solution :**
```bash
# Vérifie que le fichier existe
ls -lh ../SerdaBot-local/config/config.yaml

# Si non, copie le template
cp src/config/config.example.yaml ../SerdaBot-local/config/config.yaml
```

### Le bot utilise la mauvaise config

**Solution :**
```bash
# Force une config spécifique
export SERDABOT_CONFIG="../SerdaBot-local/config/config.yaml"
./start_bot.sh
```

### J'ai commit par erreur ma config avec tokens

**Solution immédiate :**
```bash
# 1. Supprimer du commit
git rm --cached src/config/config.yaml

# 2. Ajouter au .gitignore (déjà fait normalement)
echo "src/config/config.yaml" >> .gitignore

# 3. Commit le fix
git add .gitignore
git commit -m "fix: Retrait config avec tokens"

# 4. IMPORTANT : Régénérer tous les tokens compromis !
# - Twitch OAuth : twitchtokengenerator.com
# - RAWG API : rawg.io/apidocs
# - OpenAI : platform.openai.com
```

---

## 📚 Ressources

- [README.md](../README.md) — Vue d'ensemble du projet
- [INSTALL.md](../INSTALL.md) — Guide d'installation complet
- [config.example.yaml](../src/config/config.example.yaml) — Template de config
