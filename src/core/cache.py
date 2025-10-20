"""
Système de cache global pour les données de jeux.

Utilise RAM en production, et JSON en dev pour persistance.
Économise les requêtes API (RAWG limité à 1000/jour).
"""
import json
import os
from pathlib import Path
from time import time
from typing import Any, Dict, Optional


class GlobalGameCache:
    """Cache global pour les données de jeux avec TTL."""
    
    def __init__(self, default_ttl: int = 3600, cache_file: Optional[str] = None):
        """
        Initialise le cache.
        
        Args:
            default_ttl: Durée de vie par défaut (secondes). 3600 = 1h
            cache_file: Fichier JSON pour persistance (dev mode). None = RAM uniquement (prod)
        """
        self._cache: Dict[str, dict] = {}
        self._ttl = default_ttl
        self._cache_file = cache_file
        
        # Charger le cache depuis JSON si disponible (dev mode)
        if self._cache_file and os.path.exists(self._cache_file):
            self._load_from_file()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.
        
        Args:
            key: Clé de cache (ex: "game:hades")
        
        Returns:
            Données cachées ou None si expiré/inexistant
        """
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Vérifier expiration
        if time() - entry["timestamp"] > entry["ttl"]:
            del self._cache[key]
            self._save_to_file()  # Mettre à jour le fichier
            return None
        
        return entry["data"]
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            data: Données à cacher
            ttl: Durée de vie personnalisée (secondes). None = default_ttl
        """
        self._cache[key] = {
            "data": data,
            "timestamp": time(),
            "ttl": ttl or self._ttl
        }
        
        # Sauvegarder dans le fichier si mode dev
        self._save_to_file()
    
    def clear(self):
        """Vide tout le cache."""
        self._cache.clear()
        self._save_to_file()
    
    def cleanup_expired(self):
        """Nettoie les entrées expirées (à appeler périodiquement)."""
        now = time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry["timestamp"] > entry["ttl"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            print(f"[CACHE] 🧹 Nettoyage: {len(expired_keys)} entrées expirées supprimées")
            self._save_to_file()
    
    def stats(self) -> dict:
        """Retourne des statistiques sur le cache."""
        now = time()
        total = len(self._cache)
        expired = sum(
            1 for entry in self._cache.values()
            if now - entry["timestamp"] > entry["ttl"]
        )
        
        return {
            "total_entries": total,
            "valid_entries": total - expired,
            "expired_entries": expired,
            "cache_file": self._cache_file,
        }
    
    def _load_from_file(self):
        """Charge le cache depuis le fichier JSON (dev mode)."""
        if not self._cache_file:
            return
        
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
            print(f"[CACHE] 📂 Cache chargé depuis {self._cache_file} ({len(self._cache)} entrées)")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"[CACHE] ⚠️ Impossible de charger le cache: {e}")
            self._cache = {}
    
    def _save_to_file(self):
        """Sauvegarde le cache dans le fichier JSON (dev mode)."""
        if not self._cache_file:
            return
        
        try:
            # Créer le dossier si nécessaire
            Path(self._cache_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CACHE] ⚠️ Impossible de sauvegarder le cache: {e}")


# Instance globale (singleton)
# Production: RAM uniquement (cache_file=None)
# Dev: Persistance JSON dans cache/games.json
_cache_file = "cache/games.json" if os.getenv("BOT_ENV") == "dev" else None

GAME_CACHE = GlobalGameCache(
    default_ttl=3600,  # 1h par défaut
    cache_file=_cache_file
)


def get_cache_key(prefix: str, game_name: str) -> str:
    """
    Génère une clé de cache normalisée.
    
    Args:
        prefix: Préfixe (ex: "game", "summary", "price")
        game_name: Nom du jeu
    
    Returns:
        Clé normalisée (ex: "game:hades")
    """
    normalized = game_name.lower().strip()
    return f"{prefix}:{normalized}"


def get_ttl_for_game(release_year: str) -> int:
    """
    Calcule le TTL adapté selon l'année de sortie.
    
    Logique:
    - Jeux anciens (< 2024): 7200s = 2h (données stables)
    - Jeux récents (>= 2024): 1800s = 30min (peuvent changer)
    
    Args:
        release_year: Année de sortie (str)
    
    Returns:
        TTL en secondes
    """
    try:
        year = int(release_year)
        return 7200 if year < 2024 else 1800
    except (ValueError, TypeError):
        return 3600  # Par défaut 1h si année inconnue
