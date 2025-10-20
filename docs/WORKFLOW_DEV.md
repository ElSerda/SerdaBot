# 🧠 Workflow de développement — SerdaBot

Ce document explique le workflow de développement adopté pour garder le repo propre, sécurisé et facile à fork.

---

## 🎯 Philosophie

**Principe fondamental :** Séparer strictement le code public (Git) des données personnelles (hors Git).

### Avantages

✅ **Sécurité maximale** : Zéro risque de leak de tokens (ils sont hors Git physiquement)  
✅ **Fork-friendly** : Quelqu'un qui clone le repo a exactement ce qu'il faut  
✅ **Reproductible** : Pas de pollution avec des notes perso ou configs locales  
✅ **Scalable** : Facile de gérer plusieurs environnements (dev, staging, prod)  
✅ **Mental model clair** : SerdaBot/ = "ce que je partage", SerdaBot-local/ = "mon bazar"

---

## 📂 Structure des dossiers

```
/home/ton_user/
│
├── SerdaBot/                      # 🌐 Repo Git (public)
│   ├── src/                       # Code source
│   ├── tests/                     # Tests unitaires (pytest)
│   ├── config/
│   │   ├── config.example.yaml   # Template anonymisé (committé)
│   │   └── config.sample.yaml    # Config minimale pour CI/tests (committé)
│   ├── docs/                      # Documentation publique
│   ├── .gitignore                 # Bloque config.yaml, .env, etc.
│   ├── start_bot.sh               # Détecte config locale automatiquement
│   └── README.md
│
└── SerdaBot-local/                # 🧠 Workspace privé (JAMAIS dans Git)
    ├── config/
    │   ├── config.yaml            # Config avec tokens RÉELS
    │   ├── config-staging.yaml    # Config de test (autre compte)
    │   └── .env                   # Variables d'environnement
    │
    ├── personnal/
    │   ├── TODO.md                # Ta liste de tâches
    │   ├── IDEAS.md               # Idées de features
    │   └── notes/
    │
    ├── test-archives/
    │   ├── test_cache_v1.py       # Anciens tests one-shot
    │   └── benchmark_llm.py
    │
    ├── session-notes/
    │   ├── SESSION_2025-01-15.md  # Récaps de debug
    │   └── HOTFIX_cache_bug.md
    │
    ├── dumps/
    │   ├── cache_dump_2025-01.json
    │   └── igdb_export.txt
    │
    └── scripts/
        └── migrate_old_cache.py   # Scripts perso
```

---

## 🚀 Workflow quotidien

### 1. Développement d'une nouvelle feature

```bash
# 1. Créer une branche
cd SerdaBot/
git checkout -b feature/nouvelle-commande

# 2. Coder dans SerdaBot/ (code source)
nano src/core/commands/ma_commande.py

# 3. Tester localement (utilise config locale automatiquement)
./start_bot.sh

# 4. Noter les détails dans SerdaBot-local/
echo "✅ Feature X fonctionne, reste à gérer cas edge Y" >> ../SerdaBot-local/personnal/TODO.md

# 5. Commit uniquement le code
git add src/core/commands/ma_commande.py
git commit -m "feat: Ajout commande X"
git push origin feature/nouvelle-commande
```

### 2. Tests one-shot / expérimentations

```bash
# Test rapide dans SerdaBot-local/test-archives/
cd ../SerdaBot-local/test-archives/
nano test_nouvelle_api.py

# Exécuter le test
python test_nouvelle_api.py

# Si c'est OK, migrer le test vers SerdaBot/tests/
cp test_nouvelle_api.py ../../SerdaBot/tests/test_nouvelle_api.py
cd ../../SerdaBot/
git add tests/test_nouvelle_api.py
git commit -m "test: Ajout tests pour nouvelle API"
```

### 3. Debug / troubleshooting

```bash
# Créer une session note dans SerdaBot-local/
cd ../SerdaBot-local/session-notes/
nano SESSION_2025-01-20_bug_cache.md

# Y noter :
# - Symptômes observés
# - Hypothèses testées
# - Solution finale
# - Commits associés

# Une fois résolu, commit le fix dans SerdaBot/
cd ../../SerdaBot/
git add src/utils/cache_manager.py
git commit -m "fix: Correction bug cache HIT silencieux"
```

### 4. Gestion de plusieurs environnements

```bash
# Config dev (localhost)
export SERDABOT_CONFIG="../SerdaBot-local/config/config.yaml"
./start_bot.sh

# Config staging (autre compte Twitch)
export SERDABOT_CONFIG="../SerdaBot-local/config/config-staging.yaml"
./start_bot.sh

# Config prod (serveur distant)
export SERDABOT_CONFIG="/etc/serdabot/prod.yaml"
python src/chat/twitch_bot.py
```

---

## 🔒 Règles de sécurité

### ✅ Ce qui doit TOUJOURS être dans Git (SerdaBot/)

- Code source (`src/`)
- Tests unitaires (`tests/`)
- Documentation publique (`docs/`, `README.md`)
- Templates anonymisés (`config.example.yaml`)
- Scripts de démarrage (`start_bot.sh`)
- Dépendances (`requirements.txt`)

### ❌ Ce qui ne doit JAMAIS être dans Git

- **Tokens/clés API** (`config.yaml`, `.env`)
- **Notes personnelles** (TODOs, idées, session notes)
- **Tests one-shot** (scripts de debug temporaires)
- **Dumps/exports** (cache, logs, résultats de tests)
- **Données utilisateurs** (`data/devs.json`, listes bot)

### 🛡️ Protection multi-niveaux

1. **Séparation physique** : SerdaBot-local/ est hors du repo Git
2. **`.gitignore`** : Bloque `config.yaml`, `.env`, etc. (au cas où)
3. **Detection runtime** : `start_bot.sh` cherche config locale en priorité
4. **Fallback sécurisé** : Si aucune config, utilise `config.sample.yaml` (non fonctionnel mais safe)

---

## 📋 Checklist avant commit

Avant chaque `git commit`, vérifie :

- [ ] Aucun token/clé API dans les fichiers modifiés
- [ ] Aucune note personnelle (TODO, idées)
- [ ] Aucun dump/export temporaire
- [ ] Aucun test one-shot à la racine
- [ ] Les chemins de config sont génériques (pas de chemins absolus perso)
- [ ] Le code fonctionne avec `config.example.yaml` (après remplissage)

### Commande rapide de vérification

```bash
# Vérifier ce qui sera committé
git diff --cached

# Chercher des patterns suspects (tokens, TODO perso)
git diff --cached | grep -iE "(token|api_key|secret|TODO|FIXME|Serda)"

# Si quelque chose de suspect apparaît → annuler
git reset HEAD <fichier>
```

---

## 🤝 Pour les contributeurs externes

Si quelqu'un veut contribuer au projet :

1. **Fork le repo** sur GitHub
2. **Clone son fork** localement
3. **Créer SerdaBot-local/** et copier `config.example.yaml`
4. **Développer la feature** dans une branche
5. **Tester localement** avec sa propre config
6. **Push vers son fork** (jamais la config)
7. **Créer une Pull Request** vers le repo principal

✅ **Aucune donnée perso ne transite, tout reste local.**

---

## 🔄 Migration depuis l'ancien système

Si tu as un ancien repo avec `_local-archives/` ou `personnal/` dans Git :

```bash
# 1. Créer SerdaBot-local/
mkdir -p ../SerdaBot-local/{config,personnal,test-archives,session-notes,dumps}

# 2. Déplacer les fichiers personnels
mv personnal/* ../SerdaBot-local/personnal/
mv _local-archives/test-scripts/* ../SerdaBot-local/test-archives/
mv _local-archives/session-notes/* ../SerdaBot-local/session-notes/

# 3. Copier la config actuelle
cp src/config/config.yaml ../SerdaBot-local/config/config.yaml

# 4. Retirer du Git
git rm -r personnal/ _local-archives/
git rm src/config/config.yaml

# 5. Commit le nettoyage
git add .gitignore
git commit -m "chore: Migration vers SerdaBot-local/ (séparation code/data)"
git push origin main

# 6. Tester que tout fonctionne
./start_bot.sh  # Devrait détecter ../SerdaBot-local/config/config.yaml
```

---

## 🎓 Bonnes pratiques

### Documentation

- **Publique** (`SerdaBot/docs/`) : Architecture, API, guides d'installation
- **Privée** (`SerdaBot-local/personnal/`) : Notes de debug, idées, TODOs perso

### Tests

- **Unitaires** (`SerdaBot/tests/`) : Tests officiels (pytest), committés
- **One-shot** (`SerdaBot-local/test-archives/`) : Scripts temporaires, expérimentations

### Configuration

- **Template** (`SerdaBot/src/config/config.example.yaml`) : Anonymisé, committé
- **Sample** (`SerdaBot/src/config/config.sample.yaml`) : Minimal pour CI, committé
- **Réelle** (`SerdaBot-local/config/config.yaml`) : Tokens vrais, jamais committé

### Commits

```bash
# ✅ BON : Code générique, reproductible
git commit -m "feat: Ajout système de cache avec TTL"

# ❌ MAUVAIS : Chemin absolu, notes perso
git commit -m "fix: Bug dans test_cache.py TODO vérifier avant push"
```

---

## 🚨 En cas de leak accidentel

Si tu as committé un token par erreur :

```bash
# 1. Retirer du commit immédiatement
git rm --cached src/config/config.yaml
git commit --amend --no-edit

# 2. Si déjà pushé → force push (DANGEREUX, éviter si possible)
git push --force origin main

# 3. RÉGÉNÉRER TOUS LES TOKENS COMPROMIS
# - Twitch : twitchtokengenerator.com
# - RAWG : rawg.io/apidocs
# - OpenAI : platform.openai.com

# 4. Ajouter au .gitignore (normalement déjà fait)
echo "src/config/config.yaml" >> .gitignore
git add .gitignore
git commit -m "fix: Ajout config.yaml au .gitignore"
```

---

## 📚 Ressources

- [CONFIG_SETUP.md](CONFIG_SETUP.md) — Guide détaillé de configuration
- [README.md](../README.md) — Vue d'ensemble du projet
- [INSTALL.md](../INSTALL.md) — Installation complète
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) — Architecture du code
