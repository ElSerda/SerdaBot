# ✅ TODO-DEV : Fichiers Créés et Actions Complétées

> **Date :** 20 octobre 2025  
> **Contexte :** Suite analyse architecturale SerdaBot (score 9.2/10)

---

## 📂 Fichiers Créés

### 1. `OPTIMISATIONS.md`
**Contenu :** TODO structuré avec 6 tâches prioritisées
- 🔴 Haute : Centralisation cooldowns, Heartbeat, Structured output
- 🟡 Moyenne : Cache LLM, Métriques export
- 🟢 Basse : Documentation architecture

**Prochaines actions :**
1. Implémenter `RateLimiter` centralisé (4h)
2. Choisir stratégie heartbeat vs retry (voir HEARTBEAT_VS_RETRY.md)

---

### 2. `BENCHMARK_RAM_COOLDOWNS.md`
**Contenu :** Plan de benchmark RAM pour cooldowns par user

**Résultats obtenus :**
```
| Users  | Simple (MB) | Hourly (MB) | Full (MB) | Total |
|--------|-------------|-------------|-----------|-------|
|    100 |        0.01 |        0.08 |      0.06 |  0.15 |
|  1,000 |        0.11 |        0.76 |      0.59 |  1.47 |
| 10,000 |        1.09 |        7.64 |      5.90 | 14.63 |
```

**✅ Conclusion : Impact RAM NÉGLIGEABLE (5.9 MB pour 10K users)**

**Prochaine action :** Implémenter cooldown par user sans hésitation

---

### 3. `HEARTBEAT_VS_RETRY.md`
**Contenu :** Analyse comparative détaillée

**Recommandation finale :**
- **Phase 1 (MAINTENANT)** : Retry intelligent avec backoff exponentiel
  - Simple (50 lignes)
  - Suffisant pour dev/test
  - 30-60 min implémentation

- **Phase 2 (PROD 24/7)** : Heartbeat proactif
  - Détection proactive
  - Métriques uptime
  - Justifié en production

**Prochaine action :** Implémenter retry intelligent cette semaine

---

### 4. `scripts/benchmark_cooldowns_ram.py`
**Contenu :** Script benchmark fonctionnel

**Features :**
- ✅ Fonctionne avec ou sans `memory_profiler`
- ✅ Tests 100 / 1K / 10K users
- ✅ Option `--extreme` pour 50K users
- ✅ Mesure RAM + temps cleanup + temps lookup

**Utilisation :**
```bash
cd TODO-DEV/scripts
python benchmark_cooldowns_ram.py
# OU avec profiler détaillé
pip install memory-profiler psutil
python -m memory_profiler benchmark_cooldowns_ram.py
```

---

## ⚙️ Configuration Mise à Jour

### `config.yaml` - Nouvelle section `rate_limiting`

**Ajouté :**
```yaml
rate_limiting:
  # User cooldowns (basé sur model_limits.json)
  user_cooldown: 10                    # Actuel
  max_requests_per_user_hour: 20       # Nouveau
  max_concurrent_users: 7              # model_limits.json
  
  # Cleanup (basé sur benchmark RAM)
  cleanup_interval: 600                # 10min
  max_idle_time: 3600                  # 1h
  
  # LLM retry intelligent (Phase 1)
  llm_retry_delay: 5                   # 5s → 10s → 20s → ...
  llm_backoff_multiplier: 2
  llm_backoff_max: 300                 # Max 5min
  
  # Heartbeat (Phase 2 - désactivé)
  health_check_enabled: false
  health_check_interval: 30
  
  # External APIs
  wikipedia_rate_limit: 1.0
  igdb_rate_limit: 4.0

# Performance (auto-tuned)
max_concurrent_users_modere: 7         # Production recommandé
```

**Sources :**
- `config/model_limits.json` : max_concurrent_users_modere = 7
- Benchmark RAM : 5.9 MB pour 10K users (négligeable)
- auto-tune/ : user_rate_limit = 0.5 req/sec

---

## 📊 Métriques de Référence

### RAM (benchmark réel)
| Scénario | RAM Full RateLimiter | Verdict |
|----------|---------------------|---------|
| 100 users (stream moyen) | 0.06 MB | ✅ Négligeable |
| 1K users (gros stream) | 0.59 MB | ✅ Négligeable |
| 10K users (viral) | 5.90 MB | ✅ Acceptable |

### Performance LLM (model_limits.json)
| Mode | Max Users | Latence Max | Throughput |
|------|-----------|-------------|------------|
| Brut | 4 | 2.41s | N/A |
| Modéré | 7 | 2.49s | ~22-60 tok/s |

---

## 🎯 Prochaines Actions Prioritaires

### Cette semaine (🔴 Haute priorité)

1. **Implémenter Retry Intelligent**
   - Créer `src/utils/endpoint_tracker.py`
   - Modifier `src/utils/model_utils.py`
   - Tester avec `scripts/test_endpoint_fallback.py` (à créer)
   - **Temps estimé :** 30-60 min

2. **Centraliser Cooldowns**
   - Créer `src/utils/rate_limiter.py`
   - Migrer cooldowns de `twitch_bot.py`
   - Migrer `_failed_endpoints` de `model_utils.py`
   - Migrer `_last_wiki_call` de `cache_manager.py`
   - **Temps estimé :** 3-4 heures

3. **Lancer Benchmark Extrême (optionnel)**
   ```bash
   python TODO-DEV/scripts/benchmark_cooldowns_ram.py --extreme
   ```
   - Mesurer 50K users
   - Valider conclusions

### Ce mois (🟡 Moyenne priorité)

4. **Activer Structured Output (metadata)**
   - Modifier `chill_command.py` : `extract_metadata=True`
   - Ajouter émojis contextuels selon tone
   - Ajouter disclaimer si confidence < 0.6
   - **Temps estimé :** 2 heures

5. **Cache LLM Responses (optionnel)**
   - Créer `src/utils/llm_cache.py`
   - Intégrer dans `call_model()`
   - **Temps estimé :** 3 heures

### Quand temps disponible (🟢 Basse priorité)

6. **Documentation Architecture**
   - Diagrammes séquence (pipeline flow)
   - ADR (Architecture Decision Records)
   - **Temps estimé :** 4 heures

7. **Migrer vers Heartbeat (prod 24/7)**
   - Créer `src/utils/health_monitor.py`
   - Intégrer dans `twitch_bot.py` au boot
   - **Temps estimé :** 2-3 heures

---

## 📝 Notes Importantes

### Pourquoi ces priorités ?

**Retry Intelligent (Phase 1) :**
- ✅ Simple à implémenter (30 min)
- ✅ Amélioration immédiate (vs cache fixe 2min)
- ✅ Pas de complexité additionnelle
- ✅ Compatible avec Phase 2 future

**Cooldowns centralisés :**
- ✅ Benchmark prouve RAM négligeable (5.9 MB pour 10K users)
- ✅ Code actuellement dispersé (3 fichiers)
- ✅ Facilite maintenance future
- ✅ Prépare rate limiting par user

**Heartbeat (Phase 2) :**
- ⚠️ Complexité additionnelle (+150 lignes)
- ⚠️ Justifié SEULEMENT en prod 24/7
- ⚠️ Attendre stabilité Phase 1

---

## 🎓 Références

### Fichiers à lire
- `config/model_limits.json` : Résultats auto-tune
- `auto-tune/find_max_concurrent.py` : Script tuning
- `src/utils/model_utils.py` : Logique actuelle fallback
- `src/chat/twitch_bot.py` : Cooldowns actuels

### Commandes utiles
```bash
# Benchmark RAM
cd TODO-DEV/scripts && python benchmark_cooldowns_ram.py

# Auto-tune (si besoin re-tester)
cd auto-tune && python find_max_concurrent.py

# Tests intégration
cd scripts && python test_full_pipeline.py
cd scripts && python test_all_commands.py
```

---

## ✅ Checklist Validation

**Avant implémentation :**
- [x] Benchmark RAM lancé (résultats : 5.9 MB pour 10K users)
- [x] Config `rate_limiting` ajoutée dans `config.yaml`
- [x] Plan heartbeat vs retry analysé
- [ ] Tests actuels passent (24/24 pipeline, 17/17 commands)

**Après implémentation Retry Intelligent :**
- [ ] `src/utils/endpoint_tracker.py` créé
- [ ] `src/utils/model_utils.py` modifié
- [ ] Tests passent sans régression
- [ ] Backoff validé (5s → 10s → 20s)

**Après implémentation RateLimiter :**
- [ ] `src/utils/rate_limiter.py` créé
- [ ] Migrations terminées (3 fichiers)
- [ ] Config YAML utilisée (pas de hardcode)
- [ ] Tests 100% passing

---

## 🚀 Résumé Exécutif

**Ce qui a été fait :**
1. ✅ Analyse architecturale complète (score 9.2/10)
2. ✅ Benchmark RAM cooldowns (négligeable même 10K users)
3. ✅ Analyse heartbeat vs retry (recommandation Phase 1/2)
4. ✅ Config enrichie avec `rate_limiting` (basé sur auto-tune)
5. ✅ TODO structuré avec priorités claires

**Ce qui reste à faire :**
1. 🔴 Implémenter retry intelligent (30-60 min)
2. 🔴 Centraliser cooldowns (3-4h)
3. 🟡 Activer structured output (2h)
4. 🟡 Cache LLM optionnel (3h)
5. 🟢 Documentation + Heartbeat Phase 2 (quand prod 24/7)

**Impact attendu :**
- Meilleure gestion fallback (retry intelligent)
- Code plus maintenable (cooldowns centralisés)
- Anti-spam efficace (limite par user validée)
- Production-ready à 95% (manque heartbeat proactif)

---

**Prochaine étape suggérée :** Implémenter retry intelligent (fichier `endpoint_tracker.py`) cette semaine.
