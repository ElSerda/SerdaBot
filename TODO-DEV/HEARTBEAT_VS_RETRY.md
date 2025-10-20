# 🎯 Heartbeat vs Retry Intelligent : Analyse Détaillée

> **Contexte :** Gestion fallback LM Studio (local) → OpenAI (cloud)  
> **Problème actuel :** Cache échec 2min hardcodé, pas de vérification proactive  
> **Date :** 20 octobre 2025

---

## 📊 État Actuel (model_utils.py)

### Stratégie actuelle : Cache échec fixe
```python
# model_utils.py - Ligne 41-75
_failed_endpoints: dict[str, datetime] = {}
_CACHE_DURATION = timedelta(minutes=2)  # Hardcodé

async def call_model(...):
    # Tente endpoint local
    if api_url and api_url not in _failed_endpoints:
        result = await try_endpoint(api_url, ...)
        if result:
            return result
        # ÉCHEC : cache 2min
        _failed_endpoints[api_url] = now + timedelta(minutes=2)
    
    # Fallback OpenAI
    return await try_openai_fallback(...)
```

**Problèmes :**
- ❌ Timing arbitraire (pourquoi 2min ?)
- ❌ Pas de distinction échec réseau vs échec modèle
- ❌ Aucune tentative de récupération proactive
- ❌ Si local revient après 30s, attente 90s inutiles

---

## 🆚 Comparaison des Options

### Option A : Heartbeat périodique

**Architecture :**
```python
# model_utils.py
class ModelHealthMonitor:
    def __init__(self):
        self.endpoints = {
            "http://localhost:1234": {
                "status": "unknown",  # healthy | degraded | down | unknown
                "last_check": None,
                "consecutive_failures": 0,
                "last_successful_call": None
            }
        }
        self.health_check_task = None
    
    async def start(self):
        """Lance le heartbeat background."""
        self.health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """Vérifie santé tous les 30s."""
        while True:
            for endpoint, info in self.endpoints.items():
                try:
                    # Ping léger (GET /health ou HEAD /)
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        response = await client.get(f"{endpoint}/health")
                        if response.status_code == 200:
                            info["status"] = "healthy"
                            info["consecutive_failures"] = 0
                        else:
                            info["status"] = "degraded"
                except:
                    info["consecutive_failures"] += 1
                    if info["consecutive_failures"] >= 3:
                        info["status"] = "down"
                
                info["last_check"] = datetime.now()
            
            await asyncio.sleep(30)  # Configurable
    
    def is_endpoint_healthy(self, endpoint: str) -> bool:
        """Vérifie si endpoint est disponible."""
        status = self.endpoints.get(endpoint, {}).get("status", "unknown")
        return status in ["healthy", "unknown"]  # Optimiste si jamais testé
```

**Avantages :**
- ✅ **Détection proactive** : Sait AVANT requête user si local down
- ✅ **Récupération rapide** : Détecte quand local revient (max 30s)
- ✅ **Métriques uptime** : Historique de santé endpoints
- ✅ **Switch intelligent** : Peut forcer OpenAI si local instable
- ✅ **Dashboard ready** : Statut temps réel pour monitoring

**Inconvénients :**
- ⚠️ **+1 task asyncio** : Background thread permanent
- ⚠️ **Appels API toutes les 30s** : Négligeable (HEAD request, <10ms)
- ⚠️ **Complexité** : +100 lignes de code
- ⚠️ **Faux positifs** : Ping OK mais modèle KO (rare)

**Configuration suggérée :**
```yaml
bot:
  health_check_enabled: true
  health_check_interval: 30     # Secondes entre pings
  health_check_timeout: 2       # Timeout du ping
  health_check_failures_threshold: 3  # Échecs avant "down"
```

**Cas d'usage idéal :**
- 🎯 Production 24/7
- 🎯 SLA strict (uptime > 99%)
- 🎯 Monitoring dashboard (Grafana)
- 🎯 Environnement instable (LM Studio crash fréquents)

---

### Option B : Retry intelligent (Backoff exponentiel)

**Architecture :**
```python
# model_utils.py
class EndpointFailureTracker:
    def __init__(self):
        self.failures = {}  # {endpoint: FailureInfo}
    
    def record_failure(self, endpoint: str):
        """Enregistre un échec et calcule backoff."""
        if endpoint not in self.failures:
            self.failures[endpoint] = FailureInfo(count=0, first_failure=datetime.now())
        
        info = self.failures[endpoint]
        info.count += 1
        info.last_failure = datetime.now()
        
        # Backoff exponentiel : 5s → 10s → 20s → 40s → 80s → 160s → 300s (max)
        info.backoff_seconds = min(300, 5 * (2 ** info.count))
    
    def record_success(self, endpoint: str):
        """Reset compteur échecs."""
        if endpoint in self.failures:
            del self.failures[endpoint]
    
    def can_retry(self, endpoint: str) -> bool:
        """Vérifie si assez de temps écoulé pour retry."""
        if endpoint not in self.failures:
            return True
        
        info = self.failures[endpoint]
        elapsed = (datetime.now() - info.last_failure).total_seconds()
        return elapsed >= info.backoff_seconds

# Dans call_model()
async def call_model(...):
    if tracker.can_retry(api_url):
        result = await try_endpoint(api_url, ...)
        if result:
            tracker.record_success(api_url)  # Reset
            return result
        tracker.record_failure(api_url)  # Incrémente backoff
    
    # Fallback OpenAI
    return await try_openai_fallback(...)
```

**Avantages :**
- ✅ **Simplicité** : Pas de thread background
- ✅ **Adaptatif** : Backoff s'ajuste selon nombre d'échecs
- ✅ **Léger** : <50 lignes de code
- ✅ **Économe ressources** : Pas d'appels périodiques

**Inconvénients :**
- ⚠️ **Réactif seulement** : Découvre panne sur erreur user
- ⚠️ **Délai récupération** : Peut attendre 5min avant retry
- ⚠️ **Pas de métriques** : Pas d'historique uptime
- ⚠️ **Accumulation échecs** : Plusieurs users peuvent échouer avant fallback

**Configuration suggérée :**
```yaml
rate_limiting:
  llm_retry_delay: 5            # Premier retry après 5s
  llm_backoff_multiplier: 2     # Exponentiel (×2 à chaque échec)
  llm_backoff_max: 300          # Max 5min entre retries
  llm_reset_on_success: true    # Reset compteur si succès
```

**Cas d'usage idéal :**
- 🎯 Dev / Test
- 🎯 Environnement stable (LM Studio fiable)
- 🎯 Priorité simplicité
- 🎯 Pas besoin monitoring temps réel

---

## 🎯 Recommandation Finale

### Pour ton cas (SerdaBot) :

**Contexte :**
- Dev actuel (tests) → Prod future (stream 24/7)
- LM Studio local (qwen2.5-3b) + OpenAI fallback
- Tests montrent : 7 users concurrent max, latence < 3s

**🔴 Phase 1 (MAINTENANT - Dev/Test) : Option B (Retry intelligent)**

**Raisons :**
1. ✅ Simple à implémenter (30min)
2. ✅ Pas de complexité additionnelle
3. ✅ Suffisant pour tests/dev
4. ✅ Compatible avec Option A future

**Implémentation :**
```python
# src/utils/endpoint_tracker.py (nouveau fichier)
class EndpointFailureTracker:
    # ... (code ci-dessus)

# Dans model_utils.py
from src.utils.endpoint_tracker import EndpointFailureTracker
_endpoint_tracker = EndpointFailureTracker()

async def call_model(...):
    if _endpoint_tracker.can_retry(api_url):
        # Try local
        ...
    # Fallback OpenAI
```

**🟢 Phase 2 (PROD 24/7) : Option A (Heartbeat)**

**Raisons :**
1. ✅ Détection proactive = meilleure UX
2. ✅ Métriques uptime pour monitoring
3. ✅ Récupération rapide si local revient
4. ✅ Justifié pour production

**Trigger migration :**
- Quand stream devient 24/7 régulier
- Si LM Studio instable (>5% downtime)
- Besoin dashboard monitoring

---

## 📋 Plan d'Implémentation

### Étape 1 : Retry Intelligent (cette semaine)

**Fichiers à créer :**
```
src/utils/endpoint_tracker.py  (nouveau)
```

**Fichiers à modifier :**
```
src/utils/model_utils.py       (ligne 41-75, remplacer cache fixe)
src/config/config.yaml          (ajouter rate_limiting.llm_*)
```

**Tests :**
```bash
# Test 1 : Échec local → fallback OpenAI
# Test 2 : Backoff exponentiel (5s → 10s → 20s)
# Test 3 : Reset sur succès
python scripts/test_endpoint_fallback.py
```

**Estimation :** 30-60 min

---

### Étape 2 : Heartbeat (prod future)

**Fichiers à créer :**
```
src/utils/health_monitor.py    (nouveau)
```

**Fichiers à modifier :**
```
src/utils/model_utils.py       (intégrer health_monitor)
src/chat/twitch_bot.py         (start health monitor au boot)
```

**Tests :**
```bash
# Test 1 : Heartbeat détecte local down en 30s
# Test 2 : Heartbeat détecte local recovery
# Test 3 : Metrics uptime
python scripts/test_health_monitor.py
```

**Estimation :** 2-3 heures

---

## 🔧 Configuration Finale Suggérée

```yaml
# config.yaml
bot:
  # Modèle local
  model_endpoint: http://127.0.0.1:1234/v1/chat/completions
  model_timeout: 10
  
  # Fallback cloud
  model_type: "openai"
  openai_model: "gpt-4o-mini"

rate_limiting:
  # ===== PHASE 1 : Retry Intelligent (ACTUEL) =====
  llm_retry_delay: 5            # Premier retry après 5s
  llm_backoff_multiplier: 2     # Exponentiel
  llm_backoff_max: 300          # Max 5min
  
  # ===== PHASE 2 : Heartbeat (PROD FUTURE) =====
  # health_check_enabled: false  # Activer en prod
  # health_check_interval: 30    # Secondes entre pings
  # health_check_timeout: 2      # Timeout ping
  # health_check_failures_threshold: 3  # Échecs avant "down"
```

---

## 🎯 TL;DR

| Critère | Retry Intelligent | Heartbeat |
|---------|-------------------|-----------|
| **Complexité** | 🟢 Simple (50 lignes) | 🟡 Moyen (150 lignes) |
| **Détection panne** | ⚠️ Réactive (sur erreur) | ✅ Proactive (avant erreur) |
| **Récupération** | ⚠️ Lente (jusqu'à 5min) | ✅ Rapide (max 30s) |
| **Ressources** | ✅ Aucune overhead | ⚠️ +1 task background |
| **Métriques** | ❌ Limitées | ✅ Uptime complet |
| **Production ready** | 🟡 OK pour dev/test | ✅ Idéal pour prod 24/7 |

**Recommandation : Implémenter Retry maintenant, migrer vers Heartbeat en prod.**
