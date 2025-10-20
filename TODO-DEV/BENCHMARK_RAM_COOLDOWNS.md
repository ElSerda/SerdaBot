# 📊 Benchmark RAM : Impact des Cooldowns par User

> **Objectif :** Mesurer la consommation RAM des structures de cooldowns selon le nombre d'utilisateurs actifs  
> **Contexte :** Migration vers cooldown par user (au lieu de global)  
> **Date :** 20 octobre 2025

---

## 🎯 Scénarios de Test

### Configuration de base
```python
# Structure actuelle (twitch_bot.py)
self.cooldowns: Dict[str, datetime] = {}

# Structure proposée (rate_limiter.py)
class RateLimiter:
    user_cooldowns: Dict[str, datetime]           # Dernier message
    user_hourly_counts: Dict[str, List[float]]    # Timestamps dernière heure
    endpoint_failures: Dict[str, FailureInfo]     # État endpoints
```

### Scénarios testés
1. **100 users** : Stream moyen (~50 viewers actifs)
2. **1,000 users** : Gros stream / raid
3. **10,000 users** : Stream viral
4. **50,000 users** : Événement exceptionnel

---

## 📈 Résultats Attendus (Estimations)

### Calcul théorique

**Structure simple (actuel) :**
```
Dict[str, datetime]
- Clé (username) : ~20 bytes (string)
- Valeur (datetime) : ~48 bytes (object Python)
- Overhead dict : ~8 bytes/entrée (pointeurs)
---
Total par user : ~76 bytes
```

**Estimations :**
| Users  | RAM Simple | RAM avec Hourly Tracking | RAM Total Estimé |
|--------|------------|--------------------------|------------------|
| 100    | 7.6 KB     | +24 KB (20 msgs/h)       | **~32 KB**       |
| 1,000  | 76 KB      | +240 KB                  | **~316 KB**      |
| 10,000 | 760 KB     | +2.4 MB                  | **~3.2 MB**      |
| 50,000 | 3.8 MB     | +12 MB                   | **~16 MB**       |

**Conclusion théorique :** Négligeable même pour 50k users (Python occupe ~30-100MB au boot)

---

## 🧪 Script de Benchmark

**Fichier :** `TODO-DEV/scripts/benchmark_cooldowns_ram.py`

```python
#!/usr/bin/env python3
"""
Benchmark RAM impact des cooldowns par user.
Simule différents scénarios de charge.
"""

import sys
import time
from datetime import datetime, timedelta
from memory_profiler import profile
import random
import string

def generate_username(i: int) -> str:
    """Génère un username réaliste."""
    return f"user_{i:05d}"

@profile
def benchmark_simple_cooldowns(num_users: int):
    """Structure actuelle : Dict[str, datetime]"""
    cooldowns = {}
    
    # Remplissage
    for i in range(num_users):
        username = generate_username(i)
        cooldowns[username] = datetime.now()
    
    # Simulation lookups (10k requêtes)
    for _ in range(10_000):
        user = generate_username(random.randint(0, num_users - 1))
        _ = user in cooldowns
        if user in cooldowns:
            _ = datetime.now() - cooldowns[user]
    
    # Cleanup (expire > 1h)
    now = datetime.now()
    expired = [u for u, t in cooldowns.items() if now - t > timedelta(hours=1)]
    for u in expired:
        del cooldowns[u]
    
    return len(cooldowns)

@profile
def benchmark_hourly_tracking(num_users: int, msgs_per_user: int = 20):
    """Structure proposée : tracking messages/heure"""
    user_hourly_counts = {}
    
    # Remplissage (simule msgs_per_user messages par user)
    now = time.time()
    for i in range(num_users):
        username = generate_username(i)
        timestamps = [now - random.randint(0, 3600) for _ in range(msgs_per_user)]
        user_hourly_counts[username] = timestamps
    
    # Simulation vérifications rate limit (10k requêtes)
    for _ in range(10_000):
        user = generate_username(random.randint(0, num_users - 1))
        if user in user_hourly_counts:
            # Cleanup timestamps > 1h
            cutoff = time.time() - 3600
            user_hourly_counts[user] = [
                t for t in user_hourly_counts[user] if t > cutoff
            ]
            # Vérif limite
            _ = len(user_hourly_counts[user])
    
    return len(user_hourly_counts)

@profile
def benchmark_full_rate_limiter(num_users: int):
    """Structure complète proposée."""
    class FailureInfo:
        def __init__(self):
            self.count = 0
            self.last_failure = datetime.now()
    
    # Structures
    user_cooldowns = {}
    user_hourly_counts = {}
    endpoint_failures = {
        "http://localhost:1234": FailureInfo(),
        "https://api.openai.com": FailureInfo()
    }
    
    # Remplissage users
    now = time.time()
    for i in range(num_users):
        username = generate_username(i)
        user_cooldowns[username] = datetime.now()
        user_hourly_counts[username] = [
            now - random.randint(0, 3600) for _ in range(random.randint(5, 20))
        ]
    
    # Simulation opérations (10k requêtes)
    for _ in range(10_000):
        user = generate_username(random.randint(0, num_users - 1))
        
        # Check cooldown
        if user in user_cooldowns:
            _ = datetime.now() - user_cooldowns[user]
        
        # Check hourly limit
        if user in user_hourly_counts:
            cutoff = time.time() - 3600
            user_hourly_counts[user] = [
                t for t in user_hourly_counts[user] if t > cutoff
            ]
        
        # Check endpoints
        for endpoint, info in endpoint_failures.items():
            _ = info.count
    
    # Cleanup global (expire > 1h)
    now_dt = datetime.now()
    expired = [u for u, t in user_cooldowns.items() if now_dt - t > timedelta(hours=1)]
    for u in expired:
        del user_cooldowns[u]
        if u in user_hourly_counts:
            del user_hourly_counts[u]
    
    return len(user_cooldowns)

def main():
    scenarios = [
        (100, "Stream moyen (100 users)"),
        (1_000, "Gros stream (1K users)"),
        (10_000, "Stream viral (10K users)"),
        (50_000, "Événement exceptionnel (50K users)")
    ]
    
    results = []
    
    for num_users, description in scenarios:
        print(f"\n{'='*60}")
        print(f"🧪 TEST : {description}")
        print(f"{'='*60}\n")
        
        print("📊 Test 1 : Simple cooldowns (structure actuelle)")
        start = time.time()
        count = benchmark_simple_cooldowns(num_users)
        elapsed = time.time() - start
        print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        
        print("📊 Test 2 : Hourly tracking (rate limiting)")
        start = time.time()
        count = benchmark_hourly_tracking(num_users)
        elapsed = time.time() - start
        print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        
        print("📊 Test 3 : Full RateLimiter (structure complète)")
        start = time.time()
        count = benchmark_full_rate_limiter(num_users)
        elapsed = time.time() - start
        print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        
        results.append({
            "users": num_users,
            "description": description
        })
    
    print(f"\n{'='*60}")
    print("📋 RÉSUMÉ")
    print(f"{'='*60}")
    print("\n✅ Tests terminés ! Consultez le profil RAM ci-dessus.")
    print("\n💡 Commande utilisée : python -m memory_profiler benchmark_cooldowns_ram.py")
    print("\n📝 Résultats attendus :")
    print("   - 100 users : ~32 KB")
    print("   - 1K users : ~316 KB")
    print("   - 10K users : ~3.2 MB")
    print("   - 50K users : ~16 MB")
    print("\n🎯 Conclusion : Impact RAM négligeable pour cooldowns par user")

if __name__ == "__main__":
    main()
```

---

## 🚀 Exécution du Benchmark

### Prérequis
```bash
# Installer memory_profiler
pip install memory-profiler psutil
```

### Lancer le test
```bash
cd TODO-DEV/scripts
python -m memory_profiler benchmark_cooldowns_ram.py
```

### Sortie attendue
```
Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    15     42.3 MiB     42.3 MiB           1   @profile
    16                                         def benchmark_simple_cooldowns(num_users: int):
    ...
    25     42.4 MiB      0.1 MiB           1       for i in range(num_users):
    ...
    
RÉSUMÉ :
- 100 users : 0.03 MB (32 KB)
- 1K users : 0.31 MB (316 KB)
- 10K users : 3.2 MB
- 50K users : 16 MB
```

---

## 📊 Analyse des Résultats

### Critères d'acceptation

| Scénario | RAM Max Acceptable | Temps Cleanup Max | Temps Lookup Max |
|----------|-------------------|-------------------|------------------|
| 100 users | < 1 MB | < 10 ms | < 1 µs |
| 1K users | < 5 MB | < 50 ms | < 10 µs |
| 10K users | < 20 MB | < 500 ms | < 100 µs |
| 50K users | < 50 MB | < 2s | < 1 ms |

### Comparaison vs config actuel

**Config `model_limits.json` :**
```json
{
  "max_concurrent_users_brut": 4,
  "max_concurrent_users_modere": 7,
  "user_rate_limit": 0.5
}
```

**Interprétation :**
- Modèle supporte **7 users simultanés** (latence < 3s)
- **Mais le chat Twitch peut avoir 100-1000 viewers**
- Cooldown par user permet de gérer la file d'attente intelligemment

### Recommandations selon résultats

**Si RAM < 10 MB pour 10K users :**
✅ **Implémenter cooldown par user** (impact négligeable)

**Si RAM > 50 MB pour 10K users :**
⚠️ **Optimiser structure :**
- Utiliser `collections.deque` au lieu de `List[float]`
- Limiter historique à 20 derniers messages (au lieu de 1h complète)
- Cleanup plus agressif (toutes les 10min au lieu de 1h)

---

## 🎯 Configuration Finale Suggérée

**Basé sur `model_limits.json` :**
```yaml
rate_limiting:
  # User cooldowns (basé sur tests auto-tune)
  user_cooldown: 10                    # 10s entre messages (config actuelle)
  max_requests_per_user_hour: 20       # Limite anti-spam
  max_concurrent_users: 7              # Limite simultanée (model_limits.json)
  
  # Cleanup (optimisé selon benchmark RAM)
  cleanup_interval: 600                # 10min (si RAM < 10MB pour 10K users)
  max_idle_time: 3600                  # Supprimer users inactifs > 1h
  
  # LLM endpoints (retry intelligent)
  llm_retry_delay: 5                   # 5s premier retry
  llm_backoff_multiplier: 2            # Exponentiel
  llm_backoff_max: 300                 # Max 5min
  
  # External APIs
  wikipedia_rate_limit: 1.0            # 1 req/sec (actuel)
  igdb_rate_limit: 4.0                 # 4 req/sec (limite Twitch)
```

---

## ✅ Checklist Implémentation

- [ ] Lancer benchmark RAM
- [ ] Analyser résultats (RAM < 10MB pour 10K users ?)
- [ ] Créer `src/utils/rate_limiter.py`
- [ ] Migrer cooldowns de `twitch_bot.py`
- [ ] Migrer `_failed_endpoints` de `model_utils.py`
- [ ] Migrer `_last_wiki_call` de `cache_manager.py`
- [ ] Ajouter config `rate_limiting` dans `config.yaml`
- [ ] Tester avec `scripts/test_all_commands.py`
- [ ] Valider aucun régression tests

---

**Prochaine étape :** Lancer le benchmark pour obtenir des mesures réelles !
