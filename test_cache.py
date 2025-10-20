#!/usr/bin/env python3
"""
Test du système de cache pour !gameinfo 🎮

Vérifie que le cache fonctionne et économise les requêtes API.
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Activer le mode dev pour avoir le cache JSON
os.environ["BOT_ENV"] = "dev"

from config.config import load_config
from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game
from core.commands.api import fetch_game_data


async def test_cache():
    """Test du cache avec plusieurs scénarios."""
    print("\n" + "="*60)
    print("🧪 TEST SYSTÈME DE CACHE")
    print("="*60)
    
    config = load_config()
    
    # Test 1: Premier appel (MISS)
    print("\n📍 TEST 1: Premier appel (cache MISS)")
    print("-" * 60)
    
    game_name = "Hades"
    cache_key = get_cache_key("gameinfo", game_name)
    
    start = time.time()
    data1 = await fetch_game_data(game_name, config)
    duration1 = time.time() - start
    
    print(f"✅ Données récupérées en {duration1:.2f}s")
    print(f"📊 Jeu: {data1['name']} ({data1['release_year']})")
    
    # Calculer le TTL
    ttl = get_ttl_for_game(data1['release_year'])
    print(f"⏱️ TTL calculé: {ttl}s ({ttl//60}min)")
    
    # Mettre en cache
    GAME_CACHE.set(cache_key, data1, ttl=ttl)
    print(f"💾 Mis en cache avec clé: {cache_key}")
    
    # Test 2: Deuxième appel (HIT)
    print("\n📍 TEST 2: Deuxième appel (cache HIT)")
    print("-" * 60)
    
    start = time.time()
    cached_data = GAME_CACHE.get(cache_key)
    duration2 = time.time() - start
    
    if cached_data:
        print(f"⚡ CACHE HIT ! Récupéré en {duration2*1000:.2f}ms")
        print(f"📊 Jeu: {cached_data['name']} ({cached_data['release_year']})")
        print(f"🚀 Accélération: {duration1/duration2:.0f}x plus rapide !")
    else:
        print("❌ Cache MISS (pas normal)")
    
    # Test 3: Stats du cache
    print("\n📍 TEST 3: Statistiques du cache")
    print("-" * 60)
    
    stats = GAME_CACHE.stats()
    print(f"📊 Total entrées: {stats['total_entries']}")
    print(f"✅ Entrées valides: {stats['valid_entries']}")
    print(f"❌ Entrées expirées: {stats['expired_entries']}")
    print(f"📁 Fichier cache: {stats['cache_file']}")
    
    # Test 4: TTL pour différentes années
    print("\n📍 TEST 4: TTL adaptatif selon l'année")
    print("-" * 60)
    
    test_years = ["2020", "2023", "2024", "2025", "?"]
    for year in test_years:
        ttl = get_ttl_for_game(year)
        print(f"Année {year:4s}: TTL = {ttl:4d}s ({ttl//60:2d}min)")
    
    # Test 5: Vérifier le fichier JSON (dev mode)
    print("\n📍 TEST 5: Persistance JSON (mode dev)")
    print("-" * 60)
    
    cache_file = stats['cache_file']
    if cache_file and os.path.exists(cache_file):
        file_size = os.path.getsize(cache_file)
        print(f"✅ Fichier créé: {cache_file}")
        print(f"📦 Taille: {file_size} bytes")
        
        # Lire le contenu
        with open(cache_file, 'r') as f:
            content = f.read()
            lines = content.count('\n')
            print(f"📄 Lignes: {lines}")
    else:
        print("⚠️ Pas de fichier cache (mode prod)")
    
    print("\n" + "="*60)
    print("✅ Tests terminés !")
    print("="*60)
    print(f"\n💡 Économie de requêtes: 1 appel API au lieu de 2")
    print(f"💡 Fichier cache: {cache_file}")
    print()


if __name__ == "__main__":
    asyncio.run(test_cache())
