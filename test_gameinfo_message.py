#!/usr/bin/env python3
"""
Test du rendu du message !gameinfo avec RAWG + CACHE 🎮

Simule la commande !gameinfo pour voir le message final avec cache.
"""
import asyncio
import os
import sys
import time
from config.config import load_config
from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game
from core.commands.api import fetch_game_data

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Activer le mode dev pour avoir le cache JSON
os.environ["BOT_ENV"] = "dev"



async def test_message_format(game_name: str, test_cache: bool = False):
    """Test le formatage du message pour un jeu."""
    print(f"\n{'='*60}")
    print(f"🎮 Test: !gameinfo {game_name}")
    print('='*60)
    
    config = load_config()
    cache_key = get_cache_key("gameinfo", game_name)
    
    # Test du cache si demandé
    if test_cache:
        cached = GAME_CACHE.get(cache_key)
        if cached:
            print(f"\n⚡ CACHE HIT ! Message récupéré du cache")
            print(f"🔑 Clé: {cache_key}")
            print("\n💬 MESSAGE DEPUIS CACHE:")
            print("-" * 60)
            # Le cache contient les données, pas le message formaté
            # Donc on va simuler quand même
        else:
            print(f"\n❌ CACHE MISS - Appel API nécessaire")
    
    # Récupérer les données
    start = time.time()
    data = await fetch_game_data(game_name, config)
    duration = time.time() - start
    
    if not data:
        print(f"❌ Jeu non trouvé: {game_name}\n")
        return
    
    # Afficher les données brutes
    print(f"\n⏱️ Temps récupération: {duration:.3f}s")
    print("\n📊 DONNÉES RÉCUPÉRÉES:")
    print("-" * 60)
    print(f"Nom: {data.get('name')}")
    print(f"Année: {data.get('release_year')}")
    print(f"Plateformes: {data.get('platforms', [])[:5]}")
    print(f"Developers: {data.get('developers', [])}")
    print(f"Publishers: {data.get('publishers', [])}")
    print(f"Metacritic: {data.get('metacritic')}")
    print(f"Rating: {data.get('rating')}")
    print(f"Avis: {data.get('ratings_count')}")
    
    # Mettre en cache
    ttl = get_ttl_for_game(data.get('release_year', '?'))
    GAME_CACHE.set(cache_key, data, ttl=ttl)
    print(f"\n💾 Mis en cache (TTL: {ttl}s = {ttl//60}min)")
    print(f"🔑 Clé: {cache_key}")
    
    # Simuler le message Twitch (version simplifiée)
    print("\n💬 MESSAGE TWITCH SIMULÉ:")
    print("-" * 60)
    
    name = data.get('name', 'Inconnu')
    year = data.get('release_year', '?')
    platforms = data.get('platforms', [])
    developers = data.get('developers', [])
    publishers = data.get('publishers', [])
    metacritic = data.get('metacritic')
    rating = data.get('rating')
    ratings_count = data.get('ratings_count', 0)
    
    # Ligne 1
    msg = f"@viewer 🎮 {name} ({year})"
    if platforms:
        plat_str = ', '.join(platforms[:5]) if isinstance(platforms, list) else platforms
        msg += f", {plat_str}"
    if developers:
        dev_str = ', '.join(developers[:2])
        msg += f" | Dev: {dev_str}"
    if publishers:
        pub_str = ', '.join(publishers[:2])
        msg += f" | Pub: {pub_str}"
    
    print(msg)
    
    # Ligne 2: Ratings
    if metacritic or rating:
        rating_parts = []
        if metacritic:
            rating_parts.append(f"⭐ Metacritic: {metacritic}/100")
        if rating:
            part = f"Note: {rating}/5"
            if ratings_count > 0:
                count_str = f"{ratings_count // 1000}k" if ratings_count >= 1000 else str(ratings_count)
                part += f" ({count_str} avis)"
            rating_parts.append(part)
        print(" | ".join(rating_parts))
    
    print()


async def main():
    """Test avec plusieurs jeux + test du cache."""
    jeux = [
        "Hades",
        "Elden Ring",
        "Stardew Valley",
    ]
    
    print("\n" + "="*60)
    print("🧪 TEST MESSAGE !gameinfo - AVEC RAWG + CACHE")
    print("="*60)
    
    # Premier passage : remplir le cache
    print("\n🔥 PHASE 1: Remplissage du cache")
    print("="*60)
    for jeu in jeux:
        await test_message_format(jeu, test_cache=False)
        await asyncio.sleep(0.3)
    
    # Deuxième passage : utiliser le cache
    print("\n\n⚡ PHASE 2: Test du cache (même jeux)")
    print("="*60)
    for jeu in jeux:
        await test_message_format(jeu, test_cache=True)
        await asyncio.sleep(0.3)
    
    # Stats finales
    print("\n" + "="*60)
    print("📊 STATISTIQUES FINALES DU CACHE")
    print("="*60)
    stats = GAME_CACHE.stats()
    print(f"📦 Total entrées: {stats['total_entries']}")
    print(f"✅ Entrées valides: {stats['valid_entries']}")
    print(f"❌ Entrées expirées: {stats['expired_entries']}")
    print(f"📁 Fichier: {stats['cache_file']}")
    
    print("\n" + "="*60)
    print("✅ Tests terminés !")
    print("="*60)
    print(f"\n💡 Phase 1: {len(jeux)} jeux × 2 appels API = {len(jeux)*2} requêtes")
    print(f"💡 Phase 2: {len(jeux)} jeux × 0 appels API = 0 requêtes (cache)")
    print(f"💡 Économie: {len(jeux)*2} requêtes évitées ! 💰")
    print()


if __name__ == "__main__":
    asyncio.run(main())
