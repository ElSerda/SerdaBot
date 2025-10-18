# Changelog - SerdaBot

Toutes les modifications notables de ce projet seront documentées ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [0.1.1-alpha] - 2025-10-18

### ✨ Ajouté
- **Documentation modèle**: `docs/MODEL_CONFIG.md` avec config détaillée Qwen 2.5-1.5B
- **Archive tests**: `personnal/tests/` avec 17 fichiers tests optimisation + README
- **Fallback OpenAI**: GPT-4o-mini (100% succès, 4x moins cher que GPT-3.5-turbo)
- **Test comparatif**: `scripts/test_gpt4o_mini.py` (GPT-4o-mini vs GPT-3.5-turbo)
- Métriques performances finales (93% ASK, 80% CHILL, 87% global)

### 🔧 Modifié
- **Prompts production**: Passage prompts chinois → **français natifs** (100% français)
- **Limite ASK**: "250 caractères" → **"200 caractères"** (marge sécurité → réel ≤250 chars)
  - Résultat: 85.7% → **93.3% succès** (+7.6%)
- **Personnalité CHILL**: Ton paresseux/sarcastique → **fun/cool décontracté** (1-5 mots)
- **Few-shot enrichi**: 1 exemple → **2 exemples** (réactions + questions)
  - Résultat: 53% → **80% succès** questions (+27%)
- **Températures optimisées**: 
  - ASK: 0.6 → **0.4** (déterministe, zéro hallucinations)
  - CHILL: 0.7 → **0.5** (stable, naturel)
- **Max tokens adaptatifs**: 
  - ASK: 60 → **80 tokens** (~200 chars prompt)
  - CHILL: 60 → **20 tokens** (ultra strict 1-5 mots)
- **Stop sequences dynamiques**: 
  - ASK: `["\n\n"]` (paragraphes seulement, explications complètes)
  - CHILL: `None` (naturel)
- **README.md**: Mistral-7B → **Qwen 2.5-1.5B** + stats performances
- **Fallback OpenAI**: GPT-3.5-turbo → **GPT-4o-mini** (4x moins cher, 100% succès validé)

### 🗑️ Supprimé
- Système roast/quotes (ton sarcastique global intégré dans CHILL)
- Références anciennes prompts chinois (SYSTEM_ASK_ZH/CHILL_ZH deviennent aliases)
- Mentions Mistral/Phi-2 dans commentaires code

### 🐛 Corrigé
- Code-switching chinois (100% réponses françaises validé)
- Verbosité ASK (30-204 mots → 136 chars moyenne)
- Verbosité CHILL questions (15 mots → 2.6 mots moyenne)
- Dépassements limite 250 chars (5 cas problématiques résolus: internet 330→128, blockchain 363→220)

### 📊 Performances
- **ASK**: 93.3% ≤250 chars (moyenne 136 chars, 0.41s latence)
- **CHILL**: 80% ≤5 mots (moyenne 2.6 mots, 0.09s latence)
- **Global**: ~87% succès (objectif 80% dépassé)
- **IRC**: 100% réponses <500 chars (limite Twitch respectée)
- **Hallucinations**: 0 (tests massifs 85 cas validés)
- **Fallback GPT-4o-mini**: 100% ASK + 100% CHILL (10 cas testés), 4x moins cher que GPT-3.5-turbo

---

## [0.1.0-alpha] - 2025-10-01

### ✨ Ajouté
- Bot Twitch initial avec commandes `!ask`, `!game`, `!trad`, `!chill`
- Intégration Mistral-7B local (GGUF via ctransformers)
- Support IGDB/RAWG pour recherche jeux vidéo
- LibreTranslate pour traduction multilingue
- Système roast/quotes personnalisé
- Configuration YAML flexible
- Tests unitaires (pytest)
- CI/CD GitHub Actions

### 🎯 Features Initiales
- Mode ask: Questions factuelles avec tags
- Mode game: Recherche jeux localisée
- Mode trad: Traduction français
- Mode chill: Réponses sarcastiques avec roast/quotes

---

## Légende

- `✨ Ajouté` : Nouvelles fonctionnalités
- `🔧 Modifié` : Modifications fonctionnalités existantes
- `🗑️ Supprimé` : Fonctionnalités retirées
- `🐛 Corrigé` : Corrections bugs
- `📊 Performances` : Améliorations performances
- `🔒 Sécurité` : Corrections vulnérabilités
- `📝 Documentation` : Mises à jour documentation

---

## Roadmap

### v0.2.0 (Prévu)
- [ ] Support JSON metadata (tone, confidence) pour réactions Twitch
- [ ] Commande `!reactor` (hype events)
- [ ] Dashboard web stats bot
- [ ] Support multi-langues complet (EN, ZH)

### v1.0.0 (Futur)
- [ ] Passage production stable
- [ ] Tests load (1000+ messages/min)
- [ ] Docker containerization
- [ ] Documentation API complète
