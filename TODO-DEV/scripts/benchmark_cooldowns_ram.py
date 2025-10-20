#!/usr/bin/env python3
"""
Benchmark RAM impact des cooldowns par user.
Simule différents scénarios de charge pour mesurer la consommation mémoire.

Usage:
    python -m memory_profiler benchmark_cooldowns_ram.py
    
    OU (sans memory_profiler, utilise tracemalloc):
    python benchmark_cooldowns_ram.py
"""

import sys
import time
import tracemalloc
from datetime import datetime, timedelta
import random

# Try to import memory_profiler, but don't fail if not available
try:
    from memory_profiler import profile  # type: ignore
    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    # Fallback: no-op decorator
    def profile(func):
        return func
    print("⚠️  memory_profiler non installé. Utilisation de tracemalloc à la place.")
    print("    Pour des profils détaillés, installez : pip install memory-profiler psutil\n")


def generate_username(i: int) -> str:
    """Génère un username réaliste style Twitch."""
    return f"viewer_{i:05d}"


@profile
def benchmark_simple_cooldowns(num_users: int):
    """Structure actuelle : Dict[str, datetime]"""
    print(f"   🔹 Remplissage {num_users} users...")
    cooldowns = {}
    
    # Remplissage
    for i in range(num_users):
        username = generate_username(i)
        cooldowns[username] = datetime.now()
    
    print(f"   🔹 Simulation 10K lookups...")
    # Simulation lookups (10k requêtes)
    for _ in range(10_000):
        user = generate_username(random.randint(0, num_users - 1))
        _ = user in cooldowns
        if user in cooldowns:
            _ = datetime.now() - cooldowns[user]
    
    print(f"   🔹 Cleanup expired (> 1h)...")
    # Cleanup (expire > 1h)
    now = datetime.now()
    expired = [u for u, t in cooldowns.items() if now - t > timedelta(hours=1)]
    for u in expired:
        del cooldowns[u]
    
    return len(cooldowns)


@profile
def benchmark_hourly_tracking(num_users: int, msgs_per_user: int = 20):
    """Structure proposée : tracking messages/heure pour rate limiting."""
    print(f"   🔹 Remplissage {num_users} users avec {msgs_per_user} msgs/user...")
    user_hourly_counts = {}
    
    # Remplissage (simule msgs_per_user messages par user)
    now = time.time()
    for i in range(num_users):
        username = generate_username(i)
        timestamps = [now - random.randint(0, 3600) for _ in range(msgs_per_user)]
        user_hourly_counts[username] = timestamps
    
    print(f"   🔹 Simulation 10K vérifications rate limit...")
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
    """Structure complète proposée avec endpoints tracking."""
    class FailureInfo:
        def __init__(self):
            self.count = 0
            self.last_failure = datetime.now()
            self.backoff_time = 5
    
    print(f"   🔹 Initialisation structures complètes...")
    # Structures
    user_cooldowns = {}
    user_hourly_counts = {}
    endpoint_failures = {
        "http://localhost:1234": FailureInfo(),
        "https://api.openai.com": FailureInfo()
    }
    
    print(f"   🔹 Remplissage {num_users} users...")
    # Remplissage users
    now = time.time()
    for i in range(num_users):
        username = generate_username(i)
        user_cooldowns[username] = datetime.now()
        user_hourly_counts[username] = [
            now - random.randint(0, 3600) for _ in range(random.randint(5, 20))
        ]
    
    print(f"   🔹 Simulation 10K opérations complètes...")
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
        for _endpoint, info in endpoint_failures.items():
            _ = info.count
            _ = info.backoff_time
    
    print(f"   🔹 Cleanup global...")
    # Cleanup global (expire > 1h)
    now_dt = datetime.now()
    expired = [u for u, t in user_cooldowns.items() if now_dt - t > timedelta(hours=1)]
    for u in expired:
        del user_cooldowns[u]
        if u in user_hourly_counts:
            del user_hourly_counts[u]
    
    return len(user_cooldowns)


def measure_with_tracemalloc(func, *args):
    """Mesure RAM avec tracemalloc si memory_profiler non disponible."""
    tracemalloc.start()
    start_mem = tracemalloc.get_traced_memory()[0] / 1024 / 1024  # MB
    
    start_time = time.time()
    result = func(*args)
    elapsed = time.time() - start_time
    
    _current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    mem_used = (peak_mem - start_mem * 1024 * 1024) / 1024 / 1024  # MB
    
    return result, elapsed, mem_used


def main():
    scenarios = [
        (100, "Stream moyen (100 users)"),
        (1_000, "Gros stream (1K users)"),
        (10_000, "Stream viral (10K users)"),
    ]
    
    # Optionnel : test extrême si spécifié
    if len(sys.argv) > 1 and sys.argv[1] == "--extreme":
        scenarios.append((50_000, "Événement exceptionnel (50K users)"))
    
    results = []
    
    print("\n" + "="*70)
    print("🧪 BENCHMARK RAM : Impact des Cooldowns par User")
    print("="*70)
    
    if not HAS_MEMORY_PROFILER:
        print("\n💡 Mode tracemalloc activé (mesures manuelles)")
    
    for num_users, description in scenarios:
        print(f"\n{'='*70}")
        print(f"🎯 TEST : {description}")
        print(f"{'='*70}\n")
        
        scenario_results = {"users": num_users, "description": description}
        
        # Test 1 : Simple cooldowns
        print("📊 Test 1 : Simple cooldowns (structure actuelle)")
        if HAS_MEMORY_PROFILER:
            start = time.time()
            count = benchmark_simple_cooldowns(num_users)
            elapsed = time.time() - start
            print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        else:
            count, elapsed, mem_used = measure_with_tracemalloc(benchmark_simple_cooldowns, num_users)
            print(f"   ✅ {count} users traités en {elapsed:.2f}s")
            print(f"   📊 RAM utilisée : {mem_used:.2f} MB\n")
            scenario_results["simple_ram_mb"] = mem_used
        
        # Test 2 : Hourly tracking
        print("📊 Test 2 : Hourly tracking (rate limiting)")
        if HAS_MEMORY_PROFILER:
            start = time.time()
            count = benchmark_hourly_tracking(num_users)
            elapsed = time.time() - start
            print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        else:
            count, elapsed, mem_used = measure_with_tracemalloc(benchmark_hourly_tracking, num_users)
            print(f"   ✅ {count} users traités en {elapsed:.2f}s")
            print(f"   📊 RAM utilisée : {mem_used:.2f} MB\n")
            scenario_results["hourly_ram_mb"] = mem_used
        
        # Test 3 : Full RateLimiter
        print("📊 Test 3 : Full RateLimiter (structure complète)")
        if HAS_MEMORY_PROFILER:
            start = time.time()
            count = benchmark_full_rate_limiter(num_users)
            elapsed = time.time() - start
            print(f"   ✅ {count} users traités en {elapsed:.2f}s\n")
        else:
            count, elapsed, mem_used = measure_with_tracemalloc(benchmark_full_rate_limiter, num_users)
            print(f"   ✅ {count} users traités en {elapsed:.2f}s")
            print(f"   📊 RAM utilisée : {mem_used:.2f} MB\n")
            scenario_results["full_ram_mb"] = mem_used
        
        results.append(scenario_results)
    
    # Résumé final
    print(f"\n{'='*70}")
    print("📋 RÉSUMÉ DES RÉSULTATS")
    print(f"{'='*70}\n")
    
    if not HAS_MEMORY_PROFILER:
        print("| Users  | Simple (MB) | Hourly (MB) | Full (MB) | Total Estimé |")
        print("|--------|-------------|-------------|-----------|--------------|")
        for r in results:
            simple = r.get("simple_ram_mb", 0)
            hourly = r.get("hourly_ram_mb", 0)
            full = r.get("full_ram_mb", 0)
            total = simple + hourly + full
            print(f"| {r['users']:6,} | {simple:11.2f} | {hourly:11.2f} | {full:9.2f} | {total:12.2f} |")
        
        print("\n🎯 CONCLUSION :")
        max_ram = max(r.get("full_ram_mb", 0) for r in results)
        if max_ram < 10:
            print(f"   ✅ Impact RAM NÉGLIGEABLE ({max_ram:.2f} MB max)")
            print("   ✅ Recommandation : IMPLÉMENTER cooldown par user")
        elif max_ram < 50:
            print(f"   ⚠️  Impact RAM ACCEPTABLE ({max_ram:.2f} MB max)")
            print("   ✅ Recommandation : IMPLÉMENTER avec cleanup toutes les 10min")
        else:
            print(f"   ❌ Impact RAM ÉLEVÉ ({max_ram:.2f} MB max)")
            print("   ⚠️  Recommandation : OPTIMISER structure (deque, limite msgs)")
    else:
        print("✅ Tests terminés ! Consultez le profil RAM ci-dessus.")
        print("\n💡 Pour des mesures quantitatives, relancez sans memory_profiler.")
    
    print("\n📝 Valeurs de référence attendues :")
    print("   - 100 users : ~0.03 MB (32 KB)")
    print("   - 1K users : ~0.31 MB (316 KB)")
    print("   - 10K users : ~3.2 MB")
    print("   - 50K users : ~16 MB")
    
    print("\n🚀 Pour tester le scénario extrême (50K users) :")
    print("   python benchmark_cooldowns_ram.py --extreme")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
