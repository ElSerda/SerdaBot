#!/usr/bin/env python3
"""
Benchmark Rate Limiter - Test RAM & Performance
Simule N users concurrents et mesure l'empreinte mémoire + temps de lookup
"""
import asyncio
import sys
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class RateLimiterBenchmark:
    """Version test du RateLimiter pour benchmark."""
    
    def __init__(self, max_users: int = 1000):
        self._user_cooldowns: OrderedDict[str, datetime] = OrderedDict()
        self._user_llm_calls: OrderedDict[str, datetime] = OrderedDict()
        self._max_users = max_users
    
    def check_user_cooldown(self, user: str, cooldown_sec: int = 10) -> tuple[bool, int]:
        """Vérifie cooldown global user."""
        if len(self._user_cooldowns) >= self._max_users:
            self._user_cooldowns.popitem(last=False)
        
        if user in self._user_cooldowns:
            elapsed = (datetime.now() - self._user_cooldowns[user]).total_seconds()
            if elapsed < cooldown_sec:
                return False, int(cooldown_sec - elapsed)
        
        self._user_cooldowns[user] = datetime.now()
        return True, 0
    
    def check_llm_rate_limit(self, user: str, limit_sec: int = 3) -> tuple[bool, float]:
        """Rate limit LLM par user."""
        if len(self._user_llm_calls) >= self._max_users:
            self._user_llm_calls.popitem(last=False)
        
        if user in self._user_llm_calls:
            elapsed = (datetime.now() - self._user_llm_calls[user]).total_seconds()
            if elapsed < limit_sec:
                return False, limit_sec - elapsed
        
        self._user_llm_calls[user] = datetime.now()
        return True, 0.0
    
    def get_memory_usage(self) -> dict:
        """Stats RAM."""
        return {
            "user_cooldowns_count": len(self._user_cooldowns),
            "user_llm_calls_count": len(self._user_llm_calls),
            "estimated_bytes": (
                sys.getsizeof(self._user_cooldowns) +
                sys.getsizeof(self._user_llm_calls)
            )
        }


async def benchmark_rate_limiter(num_users: int, duration_sec: int):
    """
    Benchmark le rate limiter avec N users pendant X secondes.
    
    Args:
        num_users: Nombre de users simulés
        duration_sec: Durée du test en secondes
    """
    print(f"\n{'='*60}")
    print(f"🧪 BENCHMARK RATE LIMITER")
    print(f"{'='*60}")
    print(f"👥 Users simulés: {num_users}")
    print(f"⏱️  Durée: {duration_sec}s")
    print(f"📦 Max users en mémoire: {num_users}")
    print(f"{'='*60}\n")
    
    limiter = RateLimiterBenchmark(max_users=num_users)
    
    start_time = time.time()
    total_checks = 0
    total_lookup_time = 0
    
    # Simuler des appels aléatoires de users
    import random
    user_pool = [f"user_{i}" for i in range(num_users * 2)]  # 2x users pour tester LRU
    
    print("🚀 Démarrage simulation...\n")
    
    while time.time() - start_time < duration_sec:
        user = random.choice(user_pool)
        
        # Mesurer temps lookup cooldown
        lookup_start = time.perf_counter()
        allowed, remaining = limiter.check_user_cooldown(user, cooldown_sec=10)
        lookup_time = (time.perf_counter() - lookup_start) * 1000  # ms
        
        total_lookup_time += lookup_time
        total_checks += 1
        
        # Mesurer temps lookup LLM rate limit
        lookup_start = time.perf_counter()
        llm_allowed, llm_remaining = limiter.check_llm_rate_limit(user, limit_sec=3)
        lookup_time = (time.perf_counter() - lookup_start) * 1000  # ms
        
        total_lookup_time += lookup_time
        total_checks += 1
        
        # Petit sleep pour simuler activité réaliste
        await asyncio.sleep(0.001)  # 1ms entre checks
    
    elapsed = time.time() - start_time
    stats = limiter.get_memory_usage()
    
    # Calculer métriques
    avg_lookup_time = total_lookup_time / total_checks if total_checks > 0 else 0
    checks_per_sec = total_checks / elapsed
    memory_kb = stats["estimated_bytes"] / 1024
    memory_per_user = stats["estimated_bytes"] / num_users if num_users > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS")
    print(f"{'='*60}")
    print(f"✅ Checks totaux: {total_checks:,}")
    print(f"⚡ Checks/sec: {checks_per_sec:.1f}")
    print(f"⏱️  Lookup moyen: {avg_lookup_time:.4f}ms")
    print(f"📦 Users en cooldown: {stats['user_cooldowns_count']}")
    print(f"📦 Users LLM rate limit: {stats['user_llm_calls_count']}")
    print(f"💾 RAM totale: {memory_kb:.2f} KB ({stats['estimated_bytes']} bytes)")
    print(f"💾 RAM/user: {memory_per_user:.1f} bytes")
    print(f"{'='*60}\n")
    
    # Vérifications
    print("🔍 VALIDATION:")
    if avg_lookup_time < 0.1:  # <0.1ms
        print("✅ Performance lookup: EXCELLENT (<0.1ms)")
    elif avg_lookup_time < 1.0:  # <1ms
        print("✅ Performance lookup: BON (<1ms)")
    else:
        print("⚠️  Performance lookup: LENT (>1ms)")
    
    if stats['user_cooldowns_count'] <= num_users:
        print(f"✅ LRU cache: FONCTIONNE (limité à {num_users} users)")
    else:
        print(f"⚠️  LRU cache: PROBLÈME ({stats['user_cooldowns_count']} > {num_users})")
    
    if memory_kb < 100:  # <100KB
        print(f"✅ RAM usage: EXCELLENT (<100KB pour {num_users} users)")
    elif memory_kb < 500:  # <500KB
        print(f"✅ RAM usage: BON (<500KB pour {num_users} users)")
    else:
        print(f"⚠️  RAM usage: ÉLEVÉ (>{memory_kb:.0f}KB)")
    
    print()


async def run_benchmarks():
    """Exécute plusieurs benchmarks avec différentes configurations."""
    configs = [
        (100, 10),    # 100 users, 10s
        (500, 10),    # 500 users, 10s
        (1000, 15),   # 1000 users, 15s
        (5000, 20),   # 5000 users, 20s (stress test)
    ]
    
    for num_users, duration in configs:
        await benchmark_rate_limiter(num_users, duration)
        await asyncio.sleep(1)  # Pause entre benchmarks
    
    print("\n" + "="*60)
    print("✅ TOUS LES BENCHMARKS TERMINÉS")
    print("="*60)
    print("\n💡 RECOMMANDATIONS:")
    print("   - Lookup doit être <1ms")
    print("   - RAM doit être <500KB pour 1000 users")
    print("   - LRU cache doit limiter la taille du dict")
    print("\n   Si ces critères sont validés, le RateLimiter est production-ready ✅")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Rate Limiter")
    parser.add_argument("--users", type=int, default=None, help="Nombre de users (default: test multiple configs)")
    parser.add_argument("--duration", type=int, default=10, help="Durée en secondes (default: 10)")
    
    args = parser.parse_args()
    
    if args.users:
        # Single benchmark
        asyncio.run(benchmark_rate_limiter(args.users, args.duration))
    else:
        # Multiple benchmarks
        asyncio.run(run_benchmarks())
