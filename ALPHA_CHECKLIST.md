# ALPHA_CHECKLIST.md — Vérifications Avant Release Alpha

Checklist des erreurs et améliorations à faire avant la release publique.

---

## ✅ Complété (Prêt pour Alpha)

### Infrastructure
- [x] Support multi-plateforme (Windows, Linux, macOS)
- [x] Script de démarrage Windows (`start_bot.ps1`)
- [x] Script de démarrage Linux (`start_bot.sh`)
- [x] Build system avec PyInstaller
- [x] CI/CD avec GitHub Actions
- [x] Tests unitaires (62 tests, 100% passing)
- [x] Coverage à 27%+

### Fonctionnalités Core
- [x] Bot Twitch opérationnel
- [x] 24 commandes (4 publiques, 20 mod)
- [x] Système de fallback IA (LM Studio → DeadBot → OpenAI)
- [x] Timeout configurable pour machines lentes
- [x] Métriques détaillées (tokens, tok/s, durée)
- [x] Whitelist/Blacklist de bots
- [x] Système de traduction (FR ↔ EN)
- [x] Système de roast dynamique (roast.json modulaire)
- [x] Mode Easter Egg pour devs

### Documentation
- [x] README.md complet
- [x] INSTALL.md (Linux/macOS)
- [x] INSTALL_WINDOWS.md
- [x] COMMANDS.md (documentation des 24 commandes)
- [x] BUILD.md (guide de build .exe)
- [x] LICENSE (AGPL-v3)

---

## 🔧 À Corriger Avant Beta

### Bugs Connus

#### 🐛 Priorité Haute
- [ ] **Steam API** : Module `utils/steam.py` est vide (ligne 60 de game_utils.py l'importe)
  - Impact : Commande `!gameinfo` peut échouer si Steam est utilisé
  - Solution : Implémenter `search_steam_summary()` ou retirer l'import

- [ ] **Error Handling** : Certaines exceptions ne sont pas catchées proprement
  - `twitch_bot.py` : Log générique sans gestion spécifique
  - Solution : Ajouter try/except spécifiques avec fallbacks

- [ ] **Config Validation** : Pas de validation des valeurs du config.yaml
  - Si timeout négatif, ça crash
  - Si URL mal formée, erreur cryptique
  - Solution : Ajouter validation au chargement

#### 🐛 Priorité Moyenne
- [ ] **LLM.py** : Module legacy à 0% de coverage, non utilisé
  - 138 lignes de code mort
  - Solution : Supprimer ou documenter comme "deprecated"

- [ ] **Logging** : Pas de rotation des logs
  - Les fichiers logs/ peuvent grossir indéfiniment
  - Solution : Ajouter rotation (ex: 10 MB max, 5 fichiers)

- [ ] **API Server** : Module `api_server.py` à 0% de coverage
  - Non testé, peut avoir des bugs
  - Solution : Ajouter tests ou documenter comme "expérimental"

#### 🐛 Priorité Basse
- [x] **Prompts** : Système optimisé avec budget control
  - Budget USER = 180 chars max (smart clipping)
  - Prompts totaux: 398-439 chars (réduction 54-58%)
  - Tests validés: 62/62 passing ✅

- [ ] **Data Files** : Pas de création auto des fichiers JSON manquants
  - Si `bot_whitelist.json` manque, crash
  - Solution : Créer fichiers vides si absents

- [ ] **Code Quality (Pylint)** : Exceptions trop générales dans plusieurs fichiers
  - `src/core/igdb_api.py` : 1x `except Exception`
  - `src/utils/log.py` : 1x `except Exception`
  - `src/utils/game_utils.py` : 3x `except Exception`
  - `src/utils/translator.py` : 1x `except Exception`
  - `src/utils/llm.py` : 4x `except Exception` + 1x `import traceback`
  - Solution : Remplacer par exceptions spécifiques (non bloquant pour Alpha)

---

## 🚀 Améliorations Possibles (Post-Alpha)

### Fonctionnalités
- [ ] Système de cooldown par utilisateur (pas global)
- [ ] Historique des commandes (logs structurés)
- [ ] Dashboard web pour stats (connexions, commandes, tokens)
- [ ] Support multi-channels (plusieurs chaînes Twitch)
- [ ] Commandes personnalisées par channel

### Performance
- [ ] Cache Redis pour réponses IA fréquentes
- [ ] Compression des prompts longs
- [ ] Batch processing des traductions
- [ ] Pool de connexions HTTP

### Sécurité
- [ ] Rate limiting par IP
- [ ] Chiffrement des tokens dans config.yaml
- [ ] Audit logging pour commandes mod
- [ ] Signature des releases GitHub

### UX
- [ ] Interface graphique (Tkinter ou web)
- [ ] Wizard de configuration initial
- [ ] Auto-update checker
- [ ] Notifications desktop (succès/erreurs)

---

## 📋 Checklist Release Alpha

### Avant de créer le .exe
1. [ ] Exécuter `python tools/pre_build_check.py`
2. [ ] Vérifier que tous les tests passent : `pytest tests/`
3. [ ] Vérifier coverage : `pytest --cov=src --cov-report=term`
4. [ ] Tester sur machine propre (nouveau venv)
5. [ ] Corriger bug Steam API (priorité haute)

### Build
1. [ ] Sur Windows : `.\build.ps1 -Clean -Test`
2. [ ] Tester l'exe sur machine sans Python
3. [ ] Vérifier taille exe (<100 MB idéalement)
4. [ ] Créer archive : `SerdaBot-v0.1.0-alpha-win64.zip`

### Documentation Release
1. [ ] Créer CHANGELOG.md avec liste des features
2. [ ] Mettre à jour README.md avec lien download
3. [ ] Créer page wiki GitHub (optionnel)

### GitHub Release
1. [ ] Tag : `git tag -a v0.1.0-alpha -m "Alpha Release"`
2. [ ] Push tag : `git push origin v0.1.0-alpha`
3. [ ] Créer release sur GitHub
4. [ ] Uploader .zip Windows
5. [ ] Ajouter notes de release (features + bugs connus)

---

## ⚠️ Disclaimers pour Alpha

À mentionner dans les notes de release :

```markdown
⚠️ **Version Alpha - Bugs Attendus**

Cette version est une **preview technique** pour early adopters.

**Limitations connues :**
- Module Steam non implémenté (commande !gameinfo peut échouer)
- Pas de rotation des logs (peut consommer de l'espace disque)
- Config non validé (erreurs cryptiques si mal formaté)
- Testé principalement sur Windows 10/11 et Ubuntu 22.04

**Pré-requis :**
- LM Studio installé + modèle chargé (ou clé API OpenAI)
- Config Twitch valide (client_id, client_secret, token)
- Python 3.10+ (si build depuis source)

**Support :**
- GitHub Issues pour bugs
- Discord (lien) pour questions
```

---

## 🎯 Critères pour Passer en Beta

- [ ] 90% des bugs priorité haute corrigés
- [ ] Coverage > 40%
- [ ] Testé sur 3+ machines différentes
- [ ] Documentation complète (FAQ, troubleshooting)
- [ ] 50+ utilisateurs en alpha sans crash majeur
- [ ] Build automatique pour 3 plateformes (Win/Linux/Mac)

---

## 📊 État Actuel

| Métrique | Valeur | Objectif Beta |
|----------|--------|---------------|
| Tests | 62/62 ✅ | 100+ |
| Coverage | 27% | 40%+ |
| Bugs P1 | 2 🟥 | 0 |
| Bugs P2 | 3 🟡 | 1 max |
| Bugs P3 | 2 🔵 | 5 max |
| Platforms | 3 ✅ | 3 |
| Pylint Warnings | ~12 🟡 | 0 |
| Users | 0 | 50+ |
| Prompt Length | 398-439 chars ✅ | <500 |

**Bugs corrigés récemment :**
- ✅ Steam API (désactivé proprement)
- ✅ Pylint warnings dans `chill_command.py` (5 corrigés)
- ✅ Prompts trop longs (957 → 398-439 chars, -54-58%)
- ✅ Hardcoded usernames (remplacé par roast.json modulaire)
- ✅ 11 fichiers obsolètes supprimés (cleanup -316 lignes)

---

## 🎯 Nouveautés depuis dernier check

### ✨ Optimisation Prompts (2025-10-18)
- **Budget control** : USER_BUDGET = 180 chars max
- **Smart clipping** : Préserve Mode/Jeu/Titre en priorité
- **Roast quotes** : Limitées à 3 × 28 chars max
- **Résultats** : 54-58% de réduction (957 → 398-439 chars)
- **Cleanup** : -316 lignes de code, 11 fichiers obsolètes supprimés

### 🤖 Système Roast Dynamique (2025-10-18)
- **6 nouvelles commandes** : !addroast, !delroast, !listroast, !addquote, !delquote, !listquotes
- **Config JSON** : `config/roast.json` (max 200 users, 200 quotes)
- **Plus de hardcoding** : Fini les `prompt_*_elserda.txt`
- **Modulaire** : Géré via TwitchIO Cog (`roast_manager.py`)

---

**Dernière mise à jour :** 2025-10-18
