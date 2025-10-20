# 🎯 TODO - Optimisations Prioritaires SerdaBot

**Date de création** : 2025-10-20  
**Auteur** : GitHub Copilot (analyse du codebase)  
**Contexte** : Suite à l'analyse architecture complète, voici les améliorations recommandées par ordre de priorité.

---

## 🔴 PRIORITÉ HAUTE (Production Impact)

### 1. ⏱️ **Refactoriser les Cooldowns - Centralisation**

**Problème actuel** :
- Cooldowns dispersés dans 3 endroits :
  - `twitch_bot.py:76` → `self.cooldowns = {}` (cooldown global par user)
  - `model_utils.py:41` → `_failed_endpoints = {}` (cache endpoint échecs 2min)
  - `cache_manager.py:22` → `_last_wiki_call` (rate limit Wikipedia 1req/s)
- Pas de cooldown spécifique pour l'accès LLM par user
- Mémoire RAM non optimisée (dict infini si beaucoup d'users)

**Solution recommandée** :
```python
# Créer src/utils/rate_limiter.py
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    """Gestionnaire centralisé de tous les rate limits."""
    
    def __init__(self, max_users: int = 1000):
        # LRU cache pour limiter RAM (FIFO quand max_users atteint)
        self._user_cooldowns: OrderedDict[str, datetime] = OrderedDict()
        self._user_llm_calls: OrderedDict[str, datetime] = OrderedDict()
        self._endpoint_failures: dict[str, tuple[datetime, int]] = {}
        self._last_wiki_call: float = 0
        self._max_users = max_users
    
    def check_user_cooldown(self, user: str, cooldown_sec: int = 10) -> tuple[bool, int]:
        """Vérifie cooldown global user (commands)."""
        # Si dépassé max_users, virer le plus vieux (FIFO)
        if len(self._user_cooldowns) >= self._max_users:
            self._user_cooldowns.popitem(last=False)
        
        if user in self._user_cooldowns:
            elapsed = (datetime.now() - self._user_cooldowns[user]).total_seconds()
            if elapsed < cooldown_sec:
                return False, int(cooldown_sec - elapsed)
        
        self._user_cooldowns[user] = datetime.now()
        return True, 0
    
    def check_llm_rate_limit(self, user: str, limit_sec: int = 3) -> tuple[bool, float]:
        """Rate limit spécifique LLM par user (3s entre appels)."""
        if len(self._user_llm_calls) >= self._max_users:
            self._user_llm_calls.popitem(last=False)
        
        if user in self._user_llm_calls:
            elapsed = (datetime.now() - self._user_llm_calls[user]).total_seconds()
            if elapsed < limit_sec:
                return False, limit_sec - elapsed
        
        self._user_llm_calls[user] = datetime.now()
        return True, 0.0
    
    def check_endpoint_health(self, endpoint: str) -> tuple[bool, Optional[str]]:
        """
        Backoff exponentiel pour endpoints échoués.
        1er échec: 30s, 2e: 1min, 3e: 2min, max: 5min
        """
        if endpoint not in self._endpoint_failures:
            return True, None
        
        fail_time, fail_count = self._endpoint_failures[endpoint]
        backoff = min(300, 30 * (2 ** fail_count))  # Max 5min
        elapsed = (datetime.now() - fail_time).total_seconds()
        
        if elapsed < backoff:
            return False, f"Endpoint en cooldown ({int(backoff - elapsed)}s, échec #{fail_count})"
        
        # Réinitialiser après backoff
        del self._endpoint_failures[endpoint]
        return True, None
    
    def mark_endpoint_failure(self, endpoint: str):
        """Enregistre un échec endpoint (incrémente compteur)."""
        if endpoint in self._endpoint_failures:
            _, count = self._endpoint_failures[endpoint]
            self._endpoint_failures[endpoint] = (datetime.now(), count + 1)
        else:
            self._endpoint_failures[endpoint] = (datetime.now(), 1)
    
    def mark_endpoint_success(self, endpoint: str):
        """Réinitialise compteur échecs sur succès."""
        if endpoint in self._endpoint_failures:
            del self._endpoint_failures[endpoint]
    
    def check_wiki_rate_limit(self) -> tuple[bool, float]:
        """Wikipedia: 1 requête/seconde."""
        import time
        now = time.time()
        elapsed = now - self._last_wiki_call
        
        if elapsed < 1.0:
            return False, 1.0 - elapsed
        
        self._last_wiki_call = now
        return True, 0.0
    
    def get_memory_usage(self) -> dict:
        """Stats RAM pour benchmark."""
        import sys
        return {
            "user_cooldowns_count": len(self._user_cooldowns),
            "user_llm_calls_count": len(self._user_llm_calls),
            "endpoint_failures_count": len(self._endpoint_failures),
            "estimated_bytes": (
                sys.getsizeof(self._user_cooldowns) +
                sys.getsizeof(self._user_llm_calls) +
                sys.getsizeof(self._endpoint_failures)
            )
        }

# Instance globale
rate_limiter = RateLimiter(max_users=1000)
```

**Migration** :
- [ ] Créer `src/utils/rate_limiter.py`
- [ ] Remplacer `self.cooldowns` dans `twitch_bot.py`
- [ ] Remplacer `_failed_endpoints` dans `model_utils.py`
- [ ] Remplacer `_last_wiki_call` dans `cache_manager.py`
- [ ] Ajouter `rate_limiter.check_llm_rate_limit(user)` dans `chill_command.py` AVANT appel LLM
- [ ] Benchmark RAM : tester avec 100/500/1000 users simulés

**Bénéfices** :
- ✅ RAM maîtrisée (max 1000 users, ~50KB en mémoire)
- ✅ Rate limit LLM par user (3s) → évite spam
- ✅ Backoff exponentiel endpoint → meilleure résilience
- ✅ Code centralisé → 1 seul endroit à maintenir

**Effort estimé** : 2-3h

---

### 2. 🏥 **Heartbeat Model Local - Stratégie Recommandée**

**Problème actuel** :
- Cache endpoint échec pendant 2min = délai avant retry
- Pas de health check proactif
- Utilisateur attend timeout (10s) pour découvrir que LM Studio est down

**Options analysées** :

#### ❌ **Option A : Heartbeat périodique (déconseillé)**
```python
# Ping toutes les 30s → surcharge réseau inutile
async def heartbeat_loop():
    while True:
        await asyncio.sleep(30)
        await check_health(endpoint)
```
**Problèmes** :
- Consomme des tokens inutilement
- Surcharge réseau
- LM Studio peut être up mais surchargé

#### ✅ **Option B : Lazy Health Check (RECOMMANDÉ)**
```python
# Dans rate_limiter.py
class RateLimiter:
    async def try_endpoint_with_health(self, endpoint: str, payload: dict) -> tuple[bool, str]:
        """
        Essaye l'endpoint avec health check rapide si récemment échoué.
        Si échec récent: ping léger avant vraie requête.
        """
        health_ok, msg = self.check_endpoint_health(endpoint)
        
        if not health_ok:
            # Endpoint en cooldown, tenter un health check léger
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    # Ping rapide sans payload lourd
                    response = await client.get(f"{endpoint}/health")
                    if response.status_code == 200:
                        # Endpoint est revenu, réinitialiser
                        self.mark_endpoint_success(endpoint)
                        health_ok = True
            except Exception:
                # Toujours down, garder cooldown
                return False, msg or "Endpoint indisponible"
        
        return health_ok, ""
```

**Stratégie finale recommandée** :
```python
# Dans model_utils.py - call_model()

# 1. Vérifier santé endpoint (backoff exponentiel)
health_ok, reason = rate_limiter.check_endpoint_health(api_url)
if not health_ok:
    print(f"[MODEL] ⚠️ {reason}, fallback direct")
    return await try_openai_fallback(...)

# 2. Essayer LM Studio
try:
    result = await try_endpoint(api_url, ...)
    if result:
        rate_limiter.mark_endpoint_success(api_url)  # Réinit compteur
        return result
    rate_limiter.mark_endpoint_failure(api_url)
except Exception:
    rate_limiter.mark_endpoint_failure(api_url)

# 3. Fallback OpenAI
return await try_openai_fallback(...)
```

**Bénéfices** :
- ✅ Pas de heartbeat périodique = 0 surcharge
- ✅ Health check UNIQUEMENT quand échec récent
- ✅ Backoff exponentiel évite spam d'un endpoint down
- ✅ Fallback immédiat si endpoint en cooldown

**Migration** :
- [ ] Intégrer `check_endpoint_health()` dans `call_model()`
- [ ] Remplacer logique `_failed_endpoints` actuelle
- [ ] Ajouter logging backoff : "Échec #3, retry dans 2min"

**Effort estimé** : 1h

---

## 🟡 PRIORITÉ MOYENNE (Amélioration Progressive)

### 3. 📊 **Structured Output - Activer Metadata en Production**

**Actuellement** : Code existe dans `prompt_loader.py` mais `extract_metadata=False` partout

**Suggestion** :
```python
# Activer UNIQUEMENT pour mode CHILL (détection incertitude)
if mode == "chill":
    response = await call_model(..., extract_metadata=True)
    parsed = parse_structured_response(response)
    
    if parsed["confidence"] and parsed["confidence"] < 0.7:
        # Ajouter disclaimer
        message = f"🤔 {parsed['message']} (pas sûr à 100%)"
    else:
        message = parsed["message"]
```

**Bénéfices** :
- Transparence sur l'incertitude du modèle
- Détection automatique des réponses vagues
- Pas d'impact sur mode ASK (factuel déjà validé)

**Migration** :
- [ ] Activer dans `chill_command.py` ligne 180
- [ ] Tester avec qwen2.5-3b (vérifier format JSON valide)
- [ ] Benchmark latence : +50ms acceptable ?

**Effort estimé** : 1h

---

### 4. 💾 **Cache LLM Responses (Optionnel)**

**Idée** : Cache les questions fréquentes identiques
```python
# src/utils/llm_cache.py
from functools import lru_cache
import hashlib

class LLMResponseCache:
    def __init__(self, max_size: int = 500, ttl_hours: int = 24):
        self._cache: dict[str, tuple[str, datetime]] = {}
        self._max_size = max_size
        self._ttl = timedelta(hours=ttl_hours)
    
    def get(self, prompt: str, mode: str) -> Optional[str]:
        key = hashlib.sha256(f"{mode}:{prompt}".encode()).hexdigest()
        if key in self._cache:
            response, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return response
            del self._cache[key]
        return None
    
    def set(self, prompt: str, mode: str, response: str):
        if len(self._cache) >= self._max_size:
            # Virer le plus vieux
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        
        key = hashlib.sha256(f"{mode}:{prompt}".encode()).hexdigest()
        self._cache[key] = (response, datetime.now())
```

**Questions à valider** :
- [ ] Benchmark hit rate sur 1 semaine production
- [ ] RAM occupée (500 entrées ≈ 500KB estimé)
- [ ] Pertinence : questions répétées fréquentes ?

**Effort estimé** : 2h + 1 semaine observation

---

## 🟢 PRIORITÉ BASSE (Nice to Have)

### 5. 📈 **Metrics Export JSON (Alternative Dashboard)**

**Contexte** : Tu as déjà les logs live dans le terminal ✅

**Suggestion light** : Export JSON horaire pour analyse post-mortem
```python
# src/utils/metrics_exporter.py
class MetricsExporter:
    def __init__(self, output_dir: Path = Path("logs/metrics")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._hourly_stats = {
            "llm_calls": 0,
            "cache_hits": 0,
            "routing_hits": 0,
            "errors": 0,
            "avg_latency_ms": []
        }
    
    def log_llm_call(self, latency_ms: float, tokens_in: int, tokens_out: int):
        self._hourly_stats["llm_calls"] += 1
        self._hourly_stats["avg_latency_ms"].append(latency_ms)
    
    async def export_hourly(self):
        """Export toutes les heures."""
        while True:
            await asyncio.sleep(3600)
            timestamp = datetime.now().strftime("%Y%m%d_%H00")
            filepath = self.output_dir / f"metrics_{timestamp}.json"
            
            # Calculer moyennes
            stats = self._hourly_stats.copy()
            if stats["avg_latency_ms"]:
                stats["avg_latency_ms"] = sum(stats["avg_latency_ms"]) / len(stats["avg_latency_ms"])
            
            with open(filepath, "w") as f:
                json.dump(stats, f, indent=2)
            
            # Reset
            self._hourly_stats = {k: 0 if k != "avg_latency_ms" else [] for k in stats}
```

**Usage** : Analyser tendances, détecter regressions après update modèle

**Effort estimé** : 1h

---

## 🧪 BENCHMARKS À FAIRE

### Benchmark RAM Cooldowns
```bash
# Simuler 100/500/1000 users concurrents
python scripts/benchmark_rate_limiter.py --users 1000 --duration 60

# Mesurer :
# - RAM utilisée (via psutil)
# - Temps lookup (doit être <1ms)
# - Taille dict après cleanup LRU
```

### Benchmark Cache LLM Hit Rate
```bash
# Observer 1 semaine en production
# Compter combien de fois même question posée
# Décider si pertinent (seuil: 20% hit rate minimum)
```

---

## 📝 NOTES DE MIGRATION

### Ordre d'implémentation recommandé :
1. **RateLimiter** (Priority High) → Impact immédiat RAM + anti-spam LLM
2. **Heartbeat strategy** (Priority High) → Meilleure UX fallback
3. **Structured output** (Priority Medium) → Test 1 semaine, désactiver si pas concluant
4. **Cache LLM** (Priority Low) → Observer d'abord hit rate naturel
5. **Metrics export** (Priority Low) → Quand besoin analyse historique

### Tests de régression :
- [ ] `test_full_pipeline.py` : 24/24 tests doivent passer
- [ ] `test_all_commands.py` : 17/17 tests doivent passer
- [ ] Benchmark latence : vérifier que rate_limiter ajoute <1ms overhead

---

## 💬 FEEDBACK & AJUSTEMENTS

**Questions ouvertes** :
1. **RAM max acceptable** : 1000 users = ~50KB, 10k users = ~500KB. Limite à définir ?
2. **LLM rate limit** : 3s entre appels par user. Trop strict ? Trop lax ?
3. **Backoff max** : 5min actuellement. Augmenter à 10min ?

**Si tu veux prioriser différemment** : Dis-moi et j'ajuste le TODO !

---

**Dernière mise à jour** : 2025-10-20  
**Statut global** : 🟢 Prêt pour implémentation
