#!/usr/bin/env python3
"""
🔥 KissBot Cache Warmup - Architecture Moderne

Script de remplissage intelligent pour les caches KissBot:
- GameCache classique (TTL fixe)
- QuantumGameCache (apprentissage adaptatif)

Usage:
    python scripts/warmup_cache.py [--quantum] [--games file.txt]
    
NOUVEAU: Support du système quantique avec pré-apprentissage !
"""

import asyncio
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Setup path pour imports KissBot
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports KissBot modernes
from config_loader import load_config
from backends.game_cache import GameCache
from backends.game_lookup import GameLookup

try:
    from backends.quantum_game_cache import QuantumGameCache
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# 🎮 Jeux populaires pour warmup (optimisé pour audiences Twitch)
POPULAR_GAMES = [
    # 🔥 AAA Trending 2024-2025
    "Elden Ring",
    "Baldur's Gate 3", 
    "Cyberpunk 2077",
    "Starfield",
    "Hogwarts Legacy",
    "Diablo 4",
    
    # 🎯 AAA Classiques (toujours demandés)
    "The Witcher 3",
    "Red Dead Redemption 2",
    "GTA V",
    "Skyrim",
    "Dark Souls 3",
    "God of War",
    
    # 🏆 Indies Populaires
    "Hades",
    "Stardew Valley", 
    "Hollow Knight",
    "Celeste",
    "Dead Cells",
    "Vampire Survivors",
    "Pizza Tower",
    "Lethal Company",
    
    # 🎮 Multiplayer Twitch
    "League of Legends",
    "Valorant", 
    "Counter-Strike 2",
    "Apex Legends",
    "Fortnite",
    "Minecraft",
    "World of Warcraft",
    
    # 🎪 Variés (requests fréquentes)
    "Terraria",
    "Factorio",
    "Subnautica",
    "Portal 2",
    "Half-Life 2",
    "Ori and the Will of the Wisps"
]

class ModernCacheWarmer:
    """Warmup intelligent pour architecture KissBot moderne."""
    
    def __init__(self, config: Dict[str, Any], use_quantum: bool = False):
        self.config = config
        self.use_quantum = use_quantum and QUANTUM_AVAILABLE
        
        # Initialiser backends
        self.game_lookup = GameLookup(config)
        self.classic_cache = GameCache(config)
        
        if self.use_quantum:
            self.quantum_cache = QuantumGameCache(config)
            logger.info("🔬 Mode quantique activé")
        else:
            self.quantum_cache = None
            logger.info("🔧 Mode classique uniquement")
    
    async def warmup_games(self, games: List[str], delay: float = 0.5) -> Dict[str, Any]:
        """
        Warmup intelligent avec support quantique.
        
        Args:
            games: Liste des jeux à charger
            delay: Délai entre requêtes (rate limiting)
        """
        print("\n" + "="*60)
        print("🔥 KISSBOT CACHE WARMUP")
        print("="*60)
        print(f"🎮 {len(games)} jeux à charger")
        print(f"⏱️  Délai: {delay}s entre requêtes")
        print(f"🔬 Quantum: {'✅ Activé' if self.use_quantum else '❌ Désactivé'}")
        
        # Stats initiales
        classic_before = len(self.classic_cache.cache)
        quantum_before = 0
        if self.use_quantum and self.quantum_cache:
            quantum_stats = self.quantum_cache.get_quantum_game_stats()
            quantum_before = quantum_stats.get('game_keys', 0)
        
        print(f"📦 Cache classique avant: {classic_before} entrées")
        if self.use_quantum and self.quantum_cache:
            print(f"🔬 Cache quantique avant: {quantum_before} entrées")
        print()
        
        results = {
            'success': 0,
            'failed': 0,
            'cached_classic': 0,
            'cached_quantum': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        for i, game in enumerate(games, 1):
            print(f"[{i:2d}/{len(games)}] 🔍 Recherche: {game}...", end=" ")
            
            try:
                # Recherche via GameLookup (API)
                game_result = await self.game_lookup.search_game(game)
                
                if game_result:
                    # Cache classique
                    if not self.classic_cache.get(game):
                        # Convertir GameResult en dict pour cache
                        game_dict = {
                            'name': game_result.name,
                            'year': game_result.year,
                            'rating_rawg': game_result.rating_rawg,
                            'metacritic': game_result.metacritic,
                            'platforms': game_result.platforms,
                            'genres': game_result.genres,
                            'summary': game_result.summary,
                            'confidence': game_result.confidence,
                            'primary_source': game_result.primary_source
                        }
                        self.classic_cache.set(game, game_dict)
                        results['cached_classic'] += 1
                        cache_status = "💾 Classique"
                    else:
                        cache_status = "⚡ Déjà en cache"
                    
                    # Cache quantique (avec pré-apprentissage)
                    if self.use_quantum and self.quantum_cache:
                        quantum_result = await self.quantum_cache.search_quantum_game(
                            query=game,
                            observer="warmup_script"
                        )
                        if quantum_result and quantum_result.get('verified') != 1:
                            # Auto-confirm pour pré-apprentissage
                            self.quantum_cache.confirm_game(game, "warmup_script")
                            results['cached_quantum'] += 1
                            cache_status += " + 🔬 Quantique"
                    
                    print(f"✅ {cache_status}")
                    results['success'] += 1
                    
                else:
                    print("❌ Non trouvé")
                    results['failed'] += 1
                    results['errors'].append(f"{game}: Non trouvé")
                
            except Exception as e:
                print(f"💥 Erreur: {e}")
                results['failed'] += 1
                results['errors'].append(f"{game}: {str(e)}")
            
            # Rate limiting
            if i < len(games):
                await asyncio.sleep(delay)
        
        # Stats finales
        duration = time.time() - start_time
        classic_after = len(self.classic_cache.cache)
        
        print("\n" + "="*60)
        print("📊 RÉSULTATS WARMUP")
        print("="*60)
        print(f"✅ Succès:        {results['success']}/{len(games)} ({results['success']/len(games)*100:.1f}%)")
        print(f"❌ Échecs:        {results['failed']}/{len(games)}")
        print(f"📦 Cache classique: {classic_before} → {classic_after} (+{classic_after - classic_before})")
        
        if self.use_quantum and self.quantum_cache:
            quantum_stats = self.quantum_cache.get_quantum_game_stats()
            quantum_after = quantum_stats.get('game_keys', 0)
            confirmed = quantum_stats.get('confirmed_games', 0)
            print(f"🔬 Cache quantique:  {quantum_before} → {quantum_after} (+{quantum_after - quantum_before})")
            print(f"🎯 États confirmés: {confirmed}")
            print(f"📈 Apprentissage:   {quantum_stats.get('learning_rate', 0):.1%}")
        
        print(f"⏱️  Durée totale:   {duration:.1f}s")
        print(f"⚡ Vitesse moy:    {len(games)/duration:.1f} jeux/s")
        
        if results['errors']:
            print(f"\n⚠️ Erreurs détaillées:")
            for error in results['errors'][:5]:  # Limiter affichage
                print(f"   {error}")
            if len(results['errors']) > 5:
                print(f"   ... et {len(results['errors'])-5} autres")
        
        print(f"\n🔥 Cache warmup terminé !")
        if self.use_quantum:
            print("🔬 Le système quantique a pré-appris vos jeux favoris !")
        
        return results

def load_games_from_file(filepath: str) -> List[str]:
    """Charge liste de jeux depuis un fichier."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            games = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"📂 {len(games)} jeux chargés depuis {filepath}")
        return games
    except FileNotFoundError:
        logger.error(f"❌ Fichier non trouvé: {filepath}")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur lecture fichier: {e}")
        return []

async def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="🔥 KissBot Cache Warmup")
    parser.add_argument('--quantum', action='store_true', 
                       help='Activer warmup quantique (pré-apprentissage)')
    parser.add_argument('--games', type=str,
                       help='Fichier texte avec liste de jeux (un par ligne)')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Délai entre requêtes en secondes (défaut: 0.5)')
    
    args = parser.parse_args()
    
    # Vérifier disponibilité quantique
    if args.quantum and not QUANTUM_AVAILABLE:
        print("❌ Système quantique non disponible")
        print("💡 Installez les dépendances quantiques ou utilisez le mode classique")
        return 1
    
    # Charger config
    try:
        config = load_config()
        logger.info("✅ Configuration chargée")
    except Exception as e:
        logger.error(f"❌ Erreur config: {e}")
        return 1
    
    # Charger liste de jeux
    if args.games:
        games = load_games_from_file(args.games)
        if not games:
            return 1
    else:
        games = POPULAR_GAMES
        logger.info(f"🎮 Utilisation liste par défaut: {len(games)} jeux")
    
    # Warmup
    warmer = ModernCacheWarmer(config, use_quantum=args.quantum)
    
    try:
        results = await warmer.warmup_games(games, delay=args.delay)
        
        # Code de retour selon succès
        if results['success'] == len(games):
            return 0  # Tout s'est bien passé
        elif results['success'] > len(games) * 0.8:
            return 0  # 80%+ de succès = OK
        else:
            return 1  # Trop d'échecs
            
    except KeyboardInterrupt:
        print("\n🛑 Warmup interrompu par l'utilisateur")
        return 1
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))