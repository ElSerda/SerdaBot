#!/usr/bin/env python3
"""
Test CACHE ONLY - Pas d'appels API 🚀

Utilise uniquement le cache pour tester rapidement.
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Activer le mode dev pour avoir le cache JSON
os.environ["BOT_ENV"] = "dev"

from config.config import load_config
from core.cache import GAME_CACHE
from core.commands.api import fetch_game_data


async def test_cache_only():
    """Test avec cache uniquement (0 appel API)."""
    print("\n" + "="*60)
    print("⚡ TEST CACHE ONLY - Pas d'appels API")
    print("="*60)
    
    config = load_config()
    
    # Stats avant
    stats_before = GAME_CACHE.stats()
    print(f"\n📊 Cache avant: {stats_before['valid_entries']} entrées")
    
    # Test plusieurs jeux
    jeux = ["Hades", "Elden Ring", "Stardew Valley", "GTA 6", "Among Us"]
    
    results = {
        'hits': 0,
        'misses': 0,
        'total_time': 0,
    }
    
    print("\n🔍 Tests:")
    print("-" * 60)
    
    for jeu in jeux:
        start = time.time()
        data = await fetch_game_data(jeu, config, cache_only=True)
        duration = time.time() - start
        
        if data:
            results['hits'] += 1
            print(f"✅ {jeu:20s} → CACHE HIT ({duration*1000:.2f}ms)")
        else:
            results['misses'] += 1
            print(f"❌ {jeu:20s} → CACHE MISS")
        
        results['total_time'] += duration
    
    # Stats finales
    print("\n" + "="*60)
    print("📊 RÉSULTATS")
    print("="*60)
    print(f"✅ Cache hits:  {results['hits']}/{len(jeux)}")
    print(f"❌ Cache misses: {results['misses']}/{len(jeux)}")
    print(f"⚡ Temps total:  {results['total_time']*1000:.2f}ms")
    print(f"⚡ Temps moyen:  {results['total_time']*1000/len(jeux):.2f}ms")
    print(f"\n💡 Appels API effectués: 0")
    print(f"💡 Économie: 100% (mode cache only)")
    
    stats_after = GAME_CACHE.stats()
    print(f"\n📦 Cache final: {stats_after['valid_entries']} entrées")
    
    if stats_after['cache_file']:
        if os.path.exists(stats_after['cache_file']):
            size = os.path.getsize(stats_after['cache_file'])
            print(f"📁 Fichier: {stats_after['cache_file']} ({size} bytes)")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_cache_only())
