#!/usr/bin/env python3
"""
Comparaison RAWG vs IGDB - Résilience aux typos 🔍

Test pour voir quelle API gère mieux les fautes d'orthographe.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import load_config
from core.commands.api.rawg_api import fetch_game_from_rawg
from core.commands.api.igdb_api import get_igdb_token, query_game


async def compare_apis(game_name_with_typo: str, correct_name: str):
    """Compare RAWG vs IGDB pour un jeu avec typo."""
    print(f"\n{'='*60}")
    print(f"🔍 Test: '{game_name_with_typo}' (typo)")
    print(f"✅ Correct: '{correct_name}'")
    print(f"{'='*60}")
    
    config = load_config()
    
    # Test RAWG
    print("\n📘 RAWG:")
    print("-" * 40)
    rawg_result = await fetch_game_from_rawg(game_name_with_typo, config)
    if rawg_result:
        print(f"✅ Trouvé: {rawg_result['name']}")
        print(f"   Année: {rawg_result['release_year']}")
    else:
        print("❌ Aucun résultat")
    
    # Test IGDB (synchrone)
    print("\n📕 IGDB:")
    print("-" * 40)
    try:
        token = get_igdb_token()
        igdb_result = query_game(game_name_with_typo, token)
        if igdb_result:
            print(f"✅ Trouvé: {igdb_result['name']}")
            year = igdb_result.get('first_release_date', '')
            if year:
                from datetime import datetime
                year = datetime.fromtimestamp(year).year
            print(f"   Année: {year if year else '?'}")
        else:
            print("❌ Aucun résultat")
    except Exception as e:
        print(f"❌ Erreur IGDB: {e}")
        igdb_result = None
    
    # Verdict
    print("\n🏆 RÉSULTAT:")
    print("-" * 40)
    if rawg_result and igdb_result:
        print("Les deux APIs ont trouvé le jeu !")
    elif rawg_result and not igdb_result:
        print("RAWG gagne ! Plus résilient aux typos 🎯")
    elif igdb_result and not rawg_result:
        print("IGDB gagne ! Plus résilient aux typos 🎯")
    else:
        print("Aucune API n'a trouvé (typo trop forte)")


async def main():
    """Test plusieurs typos courantes."""
    tests = [
        ("Stardew Valey", "Stardew Valley"),        # Valey → Valley
        ("Elden Rign", "Elden Ring"),                # Rign → Ring
        ("Baldurs Gate 3", "Baldur's Gate 3"),       # Baldurs → Baldur's
        ("Mincecraft", "Minecraft"),                 # Mincecraft → Minecraft
        ("The Witcher 3 Wild Hunt", "The Witcher 3"), # Nom long
        ("God of war", "God of War"),                # Casse différente
    ]
    
    print("\n" + "="*60)
    print("🧪 COMPARAISON RAWG vs IGDB - RÉSILIENCE AUX TYPOS")
    print("="*60)
    
    for typo, correct in tests:
        await compare_apis(typo, correct)
        await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print("✅ Comparaison terminée !\n")


if __name__ == "__main__":
    asyncio.run(main())
