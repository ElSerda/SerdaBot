"""
🎮 Cache système pour API jeux - KissBot V1

Cache simple mais efficace pour éviter de poncer RAWG API !
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GameCache:
    """Cache système pour les données de jeux."""
    
    def __init__(self, cache_file: str = "cache/games.json", cache_duration_hours: int = 24):
        self.cache_file = cache_file
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache: Dict[str, Any] = {}
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self):
        """Créer le dossier cache si nécessaire."""
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _load_cache(self):
        """Charger le cache depuis le fichier."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Nettoyer les entrées expirées
                now = datetime.now()
                valid_cache = {}
                
                for key, entry in data.items():
                    cached_time = datetime.fromisoformat(entry['cached_at'])
                    if now - cached_time < self.cache_duration:
                        valid_cache[key] = entry
                
                self.cache = valid_cache
                logger.info(f"🗂️ Cache chargé: {len(self.cache)} entrées valides")
            else:
                logger.info("🗂️ Nouveau cache créé")
                
        except Exception as e:
            logger.error(f"Erreur chargement cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Sauvegarder le cache."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache: {e}")
    
    def get(self, game_query: str) -> Optional[Dict[Any, Any]]:
        """Récupérer un jeu du cache."""
        cache_key = game_query.lower().strip()
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            cached_time = datetime.fromisoformat(entry['cached_at'])
            
            # Vérifier si pas expiré
            if datetime.now() - cached_time < self.cache_duration:
                logger.info(f"🎯 Cache HIT: {game_query}")
                return entry['data']
            else:
                # Supprimer entrée expirée
                del self.cache[cache_key]
                logger.info(f"⏰ Cache EXPIRED: {game_query}")
        
        logger.info(f"❌ Cache MISS: {game_query}")
        return None
    
    def set(self, game_query: str, game_data: Dict[Any, Any]):
        """Mettre en cache un jeu."""
        cache_key = game_query.lower().strip()
        
        entry = {
            'data': game_data,
            'cached_at': datetime.now().isoformat(),
            'query': game_query
        }
        
        self.cache[cache_key] = entry
        self._save_cache()
        logger.info(f"💾 Cache SAVE: {game_query}")
    
    def clear_expired(self):
        """Nettoyer les entrées expirées."""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry['cached_at'])
            if now - cached_time >= self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"🧹 Cache nettoyé: {len(expired_keys)} entrées expirées")
    
    def get_stats(self) -> Dict[str, Any]:
        """Stats du cache."""
        return {
            'total_entries': len(self.cache),
            'cache_file': self.cache_file,
            'cache_duration_hours': self.cache_duration.total_seconds() / 3600,
            'games_cached': [entry['query'] for entry in self.cache.values()]
        }

# Instance globale
game_cache = GameCache()