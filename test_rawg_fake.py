#!/usr/bin/env python3
"""
Test RAWG avec des jeux inexistants/obscurs 🎮

Vérifie que l'API gère bien les cas limites.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import load_config
from core.commands.api.rawg_api import fetch_game_from_rawg


async def test_rawg(game_name: str):
    """Test RAWG pour un jeu."""
    print(f"\n🔍 Recherche: {game_name}")
    print("-" * 60)
    
    config = load_config()
    data = await fetch_game_from_rawg(game_name, config)
    
    if not data:
        print(f"❌ Pas trouvé: {game_name}\n")
        return
    
    print(f"✅ {data['name']} ({data['release_year']})")
    print(f"📅 Sortie: {data['release_date']}")
    
    if data.get('platforms'):
        print(f"🎮 Plateformes: {', '.join(data['platforms'][:5])}")
    
    if data.get('developers'):
        print(f"👨‍💻 Dev: {', '.join(data['developers'][:3])}")
    if data.get('publishers'):
        print(f"🏢 Publisher: {', '.join(data['publishers'][:3])}")
    
    if data.get('metacritic'):
        print(f"⭐ Metacritic: {data['metacritic']}/100")
    if data.get('rating'):
        print(f"⭐ Note: {data['rating']}/5 ({data['ratings_count']:,} avis)")
    
    if data.get('genres'):
        print(f"🎭 Genres: {', '.join(data['genres'][:3])}")
    
    print()


async def main():
    """Test avec des jeux fake/obscurs/typos."""
    tests = [
        "azerty12345qwerty",           # Totalement fake
        "Half Life 3",                 # N'existe pas (encore 😢)
        "Stardew Valey",               # Typo volontaire
        "Among Us",                    # Jeu simple/petit
        "Vampire Survivors",           # Jeu indie récent
        "xXx_GameDoesNotExist_xXx",   # Encore fake
    ]
    
    print("\n" + "="*60)
    print("🧪 TEST RAWG - CAS LIMITES (Fake/Typos/Obscurs)")
    print("="*60)
    
    for jeu in tests:
        await test_rawg(jeu)
        await asyncio.sleep(0.3)  # Pas spam
    
    print("="*60)
    print("✅ Tests terminés !\n")


if __name__ == "__main__":
    asyncio.run(main())
