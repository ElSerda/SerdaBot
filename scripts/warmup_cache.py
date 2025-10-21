#!/usr/bin/env python3
"""
Script de remplissage du cache - Warmup 🔥

Remplit le cache avec les jeux populaires pour éviter les appels API.
À lancer avant les tests ou en maintenance.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Activer le mode dev pour avoir le cache JSON
os.environ["BOT_ENV"] = "dev"

from config.config import load_config
from core.cache import GAME_CACHE
from core.commands.api import fetch_game_data

# Liste de jeux populaires à mettre en cache
POPULAR_GAMES = [
    # AAA récents
    "Elden Ring",
    "Baldur's Gate 3",
    "Cyberpunk 2077",
    "Starfield",
    "The Last of Us Part II",
    "God of War Ragnarök",
    
    # AAA classiques
    "The Witcher 3",
    "Red Dead Redemption 2",
    "GTA V",
    "Skyrim",
    "Dark Souls 3",
    
    # Indies populaires
    "Hades",
    "Stardew Valley",
    "Hollow Knight",
    "Celeste",
    "Dead Cells",
    "Vampire Survivors",
    "Among Us",
    
    # Multiplayer
    "League of Legends",
    "Valorant",
    "Counter-Strike 2",
    "Apex Legends",
    "Overwatch 2",
]


async def warmup_cache(games: list[str], delay: float = 0.5):
    """
    Remplit le cache avec une liste de jeux.
    
    Args:
        games: Liste des noms de jeux
        delay: Délai entre chaque requête (éviter rate limit)
    """
    config = load_config()
    
    print("\n" + "="*60)
    print("🔥 WARMUP DU CACHE")
    print("="*60)
    print(f"📋 {len(games)} jeux à charger")
    print(f"⏱️ Délai: {delay}s entre chaque requête")
    
    # Stats avant
    stats_before = GAME_CACHE.stats()
    print(f"📦 Cache avant: {stats_before['valid_entries']} entrées\n")
    
    results = {
        'success': 0,
        'failed': 0,
        'cached': 0,
    }
    
    for i, game in enumerate(games, 1):
        print(f"[{i}/{len(games)}] {game:30s} ", end='', flush=True)
        
        try:
            data = await fetch_game_data(game, config)
            
            if data:
                results['success'] += 1
                print(f"✅ {data['name']} ({data.get('release_year', '?')})")
            else:
                results['failed'] += 1
                print("❌ Non trouvé")
            
            # Petit délai pour ne pas spam l'API
            if i < len(games):
                await asyncio.sleep(delay)
                
        except Exception as e:
            results['failed'] += 1
            print(f"❌ Erreur: {e}")
    
    # Stats finales
    print("\n" + "="*60)
    print("📊 RÉSULTATS DU WARMUP")
    print("="*60)
    
    stats_after = GAME_CACHE.stats()
    
    print(f"✅ Succès:        {results['success']}/{len(games)}")
    print(f"❌ Échecs:        {results['failed']}/{len(games)}")
    print(f"📦 Entrées cache: {stats_after['valid_entries']}")
    print(f"📈 Nouvelles:     {stats_after['valid_entries'] - stats_before['valid_entries']}")
    
    if stats_after['cache_file']:
        if os.path.exists(stats_after['cache_file']):
            size = os.path.getsize(stats_after['cache_file'])
            print(f"📁 Fichier:       {stats_after['cache_file']}")
            print(f"💾 Taille:        {size:,} bytes ({size/1024:.1f} KB)")
    
    print(f"\n💡 Le cache est maintenant chaud ! 🔥")
    print(f"💡 Les prochains appels seront instantanés ⚡")
    print()


async def main():
    """Point d'entrée principal."""
    # Mode auto si argument --auto
    auto_mode = len(sys.argv) > 1 and sys.argv[1] == "--auto"
    
    if not auto_mode:
        print("\n🎮 Script de Warmup du Cache")
        print("="*60)
        
        choice = input("\n1. Charger les jeux populaires (recommandé)\n2. Charger une liste personnalisée\n\nChoix (1/2): ").strip()
        
        if choice == "2":
            custom_games = input("\nEntrez les jeux séparés par des virgules:\n> ").strip()
            games = [g.strip() for g in custom_games.split(',') if g.strip()]
        else:
            games = POPULAR_GAMES
        
        if not games:
            print("\n❌ Aucun jeu à charger !")
            return
        
        print(f"\n🚀 Lancement du warmup pour {len(games)} jeux...")
        input("Appuyez sur Entrée pour continuer (Ctrl+C pour annuler)...\n")
    else:
        # Mode auto : charge directement les jeux populaires
        games = POPULAR_GAMES
    
    await warmup_cache(games)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Warmup annulé par l'utilisateur")
