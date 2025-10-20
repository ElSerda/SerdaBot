# Monitoring et Métriques - SerdaBot Routing

## 📊 Vue d'ensemble

Ce dossier contient les outils de monitoring pour l'architecture **Proactive Routing** de SerdaBot.

**Objectif** : Tracker les performances en production et identifier les opportunités d'amélioration.

---

## 🔧 Outils disponibles

### 1. Logs structurés (`chill_command.py`)

Les logs debug sont organisés par couche avec timing précis :

```python
# Activer debug dans config.yaml
bot:
  debug: true
```

**Format des logs** :

```
[ROUTING] 🎯 Détection: 'Quand sort Zelda ?' → game='zelda' (2.3ms)
[ROUTING] ✅ IGDB terminé: @viewer1 | game=zelda | latence=145ms
[ROUTING] ⏭️  Pas de routage détecté (1.8ms) → LLM

[LLM] 📝 Prompt: user=viewer2 | content='...' | size=523 chars
[LLM] 📨 Réponse: size=87 chars | latence=1842ms | preview='...'

[POST-FILTER] 🛡️  BLOQUÉ: user='...' | llm='...' | hint=gta | latence=1.2ms
[POST-FILTER] ✅ OK: pas de détection (0.6ms)

[SEND] ✅ Envoyé: @viewer4 | size=68 chars | latence=15ms
[METRICS] ⏱️  Total: 2152ms (routing=2 + llm=2134 + filter=1 + send=15)
```

---

### 2. Script d'analyse (`analyze_routing_metrics.py`)

**Usage** :

```bash
python scripts/analyze_routing_metrics.py logs/bot.log
```

**Métriques extraites** :

#### 📈 Statistiques générales
- Total messages traités
- % routés vers IGDB vs LLM
- Appels LLM effectués
- % post-filtre bloqué vs passé

#### 🎯 Taux de capture
- Total questions jeux détectées
- Taux routage précoce (objectif: >80%)
- Taux post-filtre (défense finale)

#### 🎮 Top jeux
- Jeux les plus demandés (routing)
- Jeux les plus bloqués (post-filtre hallucinations)

#### ⏱️ Latences moyennes
- Routage détection (objectif: <10ms)
- Appel LLM (variable)
- Post-filtre (objectif: <5ms)
- Temps total end-to-end

#### 🚨 Exemples hallucinations
- Échantillon des cas bloqués par post-filtre
- User query + LLM response + hint extrait

#### 💡 Recommandations
- Alertes automatiques si métriques anormales
- Suggestions d'optimisation

---

## 📊 Exemple de rapport

```
================================================================================
📊 RAPPORT D'ANALYSE ROUTAGE - SerdaBot
================================================================================

🔢 STATISTIQUES GÉNÉRALES
--------------------------------------------------------------------------------
Messages traités totaux:     12
  ├─ Routés vers IGDB:           6 ( 50.0%)
  └─ Traités par LLM:            6 ( 50.0%)

Appels LLM effectués:        6
  ├─ Post-filtre bloqué:         3 ( 50.0%)
  └─ Post-filtre passé:          3 ( 50.0%)

🎯 TAUX DE CAPTURE (questions jeux)
--------------------------------------------------------------------------------
Total questions jeux:        9
  ├─ Routage précoce:          66.7%  (idéal: >80%)
  └─ Post-filtre:              33.3%  (défense finale)

🎮 TOP JEUX DEMANDÉS (routage précoce)
--------------------------------------------------------------------------------
  zelda                              2 demandes
  gta                                1 demandes
  elden ring                         1 demandes

🛡️  TOP JEUX BLOQUÉS (post-filtre)
--------------------------------------------------------------------------------
  gta                                1 hallucinations bloquées
  skyrim                             1 hallucinations bloquées

⏱️  LATENCES MOYENNES
--------------------------------------------------------------------------------
Routage détection:              2.0 ms  (objectif: <10ms)
Appel LLM:                     1963 ms  (variable selon charge)
Post-filtre:                    0.8 ms  (objectif: <5ms)
Temps total (end-to-end):      1978 ms

💡 RECOMMANDATIONS
--------------------------------------------------------------------------------
✅ Taux routage dans la norme (30-80%)
⚠️  Taux post-filtre élevé (>20%) → Améliorer routage précoce
✅ Latence LLM acceptable
```

---

## 🎯 Objectifs de performance

### Taux de routage précoce
- **Optimal** : >80% des questions jeux détectées avant LLM
- **Acceptable** : 60-80%
- **À améliorer** : <60% (ajouter patterns)

### Taux post-filtre
- **Optimal** : <10% des appels LLM bloqués (routing efficace)
- **Acceptable** : 10-20%
- **Problématique** : >20% (améliorer patterns routing)

### Latences
- **Routing** : <10ms (regex simple)
- **Post-filtre** : <5ms (regex + keywords)
- **LLM** : 1-3s (dépend charge serveur)
- **Total** : <3.5s end-to-end

### Zéro hallucination
- **Objectif absolu** : 0% faux négatifs (aucune date échappée)
- **Acceptable** : <5% faux positifs (redirections prudentes)

---

## 🔍 Cas d'usage

### 1. Monitoring quotidien

```bash
# Analyser logs du jour
python scripts/analyze_routing_metrics.py logs/serda_bot_$(date +%Y%m%d).log
```

**Vérifier** :
- Taux routage stable (~70%)
- Latences normales (<3.5s total)
- Pas de pic hallucinations

---

### 2. Optimisation patterns

**Symptôme** : Taux post-filtre >20%

**Action** :
1. Identifier jeux fréquemment bloqués
2. Analyser patterns user queries
3. Ajouter patterns dans `should_route_to_gameinfo()`
4. Re-tester avec `test_routing_with_model.py`

**Exemple** :

```python
# Top bloqués: "final fantasy" (15 hallucinations)
# User queries: "FF7 sort quand ?", "Final Fantasy 16 dispo ?"

# Ajouter pattern:
r'\b(ff|final\s+fantasy)\s*\d*\s+(sort|dispo|quand)\b'
```

---

### 3. Investigation hallucinations

**Symptôme** : Exemples bloqués suspects

```
User: "GTA 6 c'est bien ?"
LLM:  "Ouais ! Sorti en 2025 je crois..."
```

**Action** :
1. Vérifier si routing aurait dû capturer
2. Si oui → améliorer pattern
3. Si non → post-filtre fonctionne correctement (défense finale)

---

### 4. Performance LLM

**Symptôme** : Latence LLM >3s

**Actions possibles** :
1. Vérifier charge LM Studio
2. Réduire `max_tokens` dans config
3. Optimiser prompt (moins de contexte)
4. Envisager modèle plus rapide (1.5B au lieu de 3B)

---

## 📝 Fichiers de logs

### Structure recommandée

```
logs/
├── serda_bot_20251019.log      # Logs journaliers
├── serda_bot_20251020.log
├── sample_routing_metrics.log  # Exemple pour tests
└── archive/
    └── serda_bot_202510*.log   # Archives mensuelles
```

### Rotation automatique

```bash
# Ajouter dans cron (rotation quotidienne)
0 0 * * * cd /path/to/SerdaBot && mv logs/current.log logs/serda_bot_$(date +\%Y\%m\%d).log
```

---

## 🚨 Alertes recommandées

### Critiques (intervention immédiate)
- ✅ **Zéro hallucination** : Si post-filtre taux <100% → BUG
- 🔥 **Latence >10s** : Serveur LLM probablement down

### Avertissements (surveillance)
- ⚠️ **Taux routage <50%** : Patterns inefficaces
- ⚠️ **Post-filtre >30%** : Routing insuffisant
- ⚠️ **Latence LLM >5s** : Charge serveur élevée

### Info (optimisation)
- 💡 **Nouveau jeu fréquent** : Ajouter aux keywords
- 💡 **Pattern rare triggeré** : Peut-être faux positif

---

## 🎓 Leçons apprises

### 1. Logs structurés > Logs verbeux
- ✅ Format parsable : `[COUCHE] emoji Action: key=value`
- ❌ Éviter : logs free-text non structurés

### 2. Timing par couche essentiel
- Permet d'identifier goulots d'étranglement
- Routing (2ms) vs LLM (2s) vs Filter (1ms)

### 3. Métriques métier > Métriques techniques
- "% hallucinations bloquées" > "lignes de code"
- "Top jeux demandés" > "nombre de regex"

### 4. Échantillons d'exemples critiques
- 5 exemples > statistiques abstraites
- Aide debugging rapide

---

## 🔮 Évolutions futures

### Court terme (v1.1)
- [ ] Dashboarding temps réel (Grafana)
- [ ] Alertes Slack/Discord
- [ ] Export CSV métriques

### Moyen terme (v1.2)
- [ ] ML pour détection anomalies
- [ ] A/B testing patterns
- [ ] Prédiction charge LLM

### Long terme (v2.0)
- [ ] Auto-optimisation patterns
- [ ] Feedback loop viewers
- [ ] Multi-LLM routing (GPT-4o fallback)

---

**Auteur** : SerdaBot Team  
**Date** : Octobre 2025  
**Status** : ✅ Production Ready

**Voir aussi** :
- `docs/PROACTIVE_ROUTING.md` - Architecture complète
- `scripts/test_routing_*.py` - Tests unitaires
