"""
Rate Limiter - Gestionnaire centralisé des cooldowns et rate limits.

Ce module centralise TOUS les rate limits du bot :
- Cooldowns globaux par user (commands)
- Rate limit LLM par user (anti-spam)
- Health check endpoints (backoff exponentiel)
- Rate limit Wikipedia (1 req/sec)

RAM optimisée : LRU cache avec limite configurable (default 1000 users = ~50KB)
"""
import time
from collections import OrderedDict
from datetime import datetime
from typing import Optional


class RateLimiter:
    """
    Gestionnaire centralisé de tous les rate limits du bot.
    
    Features:
    - LRU cache pour limiter RAM (FIFO quand max_users atteint)
    - Backoff exponentiel pour endpoints échoués
    - Rate limit Wikipedia 1 req/sec
    - Cooldown global par user (commands)
    - Rate limit LLM par user (anti-spam)
    
    Memory usage: ~50 bytes/user → 1000 users ≈ 50KB
    Lookup time: <0.1ms (dict lookup O(1))
    """
    
    def __init__(self, max_users: int = 1000):
        """
        Initialise le rate limiter.
        
        Args:
            max_users: Nombre max d'users en mémoire (LRU cache).
                      Au-delà, vire les plus vieux (FIFO).
                      1000 users ≈ 50KB RAM.
        """
        # LRU cache pour limiter RAM (OrderedDict = FIFO automatique)
        self._user_cooldowns: OrderedDict[str, datetime] = OrderedDict()
        self._user_llm_calls: OrderedDict[str, datetime] = OrderedDict()
        
        # Endpoint failures (pas de limite, généralement <10 endpoints)
        # Format: {endpoint: (fail_time, fail_count)}
        self._endpoint_failures: dict[str, tuple[datetime, int]] = {}
        
        # Wikipedia rate limit (global, pas par user)
        self._last_wiki_call: float = 0
        
        # Config
        self._max_users = max_users
    
    def check_user_cooldown(self, user: str, cooldown_sec: int = 10) -> tuple[bool, int]:
        """
        Vérifie le cooldown global d'un user (commandes).
        
        Args:
            user: Username
            cooldown_sec: Cooldown en secondes (default: 10s)
        
        Returns:
            (allowed, remaining_sec)
            - allowed: True si user peut utiliser une commande
            - remaining_sec: Secondes restantes si en cooldown
        
        Usage:
            allowed, remaining = rate_limiter.check_user_cooldown("serda", cooldown_sec=10)
            if not allowed:
                print(f"Cooldown: {remaining}s restant")
        """
        # LRU: virer le plus vieux si max atteint
        if len(self._user_cooldowns) >= self._max_users:
            self._user_cooldowns.popitem(last=False)  # FIFO
        
        # Vérifier cooldown
        if user in self._user_cooldowns:
            elapsed = (datetime.now() - self._user_cooldowns[user]).total_seconds()
            if elapsed < cooldown_sec:
                return False, int(cooldown_sec - elapsed)
        
        # OK, enregistrer timestamp
        self._user_cooldowns[user] = datetime.now()
        return True, 0
    
    def check_llm_rate_limit(self, user: str, limit_sec: int = 3) -> tuple[bool, float]:
        """
        Rate limit spécifique pour appels LLM par user (anti-spam).
        Plus strict que le cooldown global.
        
        Args:
            user: Username
            limit_sec: Rate limit en secondes (default: 3s)
        
        Returns:
            (allowed, remaining_sec)
            - allowed: True si user peut appeler le LLM
            - remaining_sec: Secondes restantes si rate limited
        
        Usage:
            allowed, remaining = rate_limiter.check_llm_rate_limit("serda", limit_sec=3)
            if not allowed:
                print(f"Rate limit LLM: {remaining:.1f}s restant")
        """
        # LRU: virer le plus vieux si max atteint
        if len(self._user_llm_calls) >= self._max_users:
            self._user_llm_calls.popitem(last=False)  # FIFO
        
        # Vérifier rate limit
        if user in self._user_llm_calls:
            elapsed = (datetime.now() - self._user_llm_calls[user]).total_seconds()
            if elapsed < limit_sec:
                return False, limit_sec - elapsed
        
        # OK, enregistrer timestamp
        self._user_llm_calls[user] = datetime.now()
        return True, 0.0
    
    def check_endpoint_health(self, endpoint: str) -> tuple[bool, Optional[str]]:
        """
        Vérifie la santé d'un endpoint avec backoff exponentiel.
        
        Backoff:
        - 1er échec: 30s cooldown
        - 2e échec: 1min cooldown
        - 3e échec: 2min cooldown
        - 4e échec: 4min cooldown
        - Max: 5min cooldown
        
        Args:
            endpoint: URL de l'endpoint (ex: "http://localhost:1234/v1/chat/completions")
        
        Returns:
            (is_healthy, reason)
            - is_healthy: True si endpoint est dispo (ou jamais échoué)
            - reason: Message d'erreur si en cooldown (ex: "Endpoint en cooldown (45s, échec #2)")
        
        Usage:
            healthy, reason = rate_limiter.check_endpoint_health(api_url)
            if not healthy:
                print(f"[MODEL] ⚠️ {reason}, fallback direct")
                return await try_openai_fallback(...)
        """
        if endpoint not in self._endpoint_failures:
            return True, None
        
        fail_time, fail_count = self._endpoint_failures[endpoint]
        
        # Backoff exponentiel: 30s * 2^fail_count, max 5min
        backoff = min(300, 30 * (2 ** fail_count))
        elapsed = (datetime.now() - fail_time).total_seconds()
        
        if elapsed < backoff:
            remaining = int(backoff - elapsed)
            return False, f"Endpoint en cooldown ({remaining}s, échec #{fail_count})"
        
        # Backoff expiré, réinitialiser (prochain appel va retry)
        del self._endpoint_failures[endpoint]
        return True, None
    
    def mark_endpoint_failure(self, endpoint: str):
        """
        Enregistre un échec d'endpoint (incrémente compteur pour backoff).
        
        Args:
            endpoint: URL de l'endpoint qui a échoué
        
        Usage:
            try:
                result = await try_endpoint(api_url, ...)
                rate_limiter.mark_endpoint_success(api_url)
            except Exception:
                rate_limiter.mark_endpoint_failure(api_url)
        """
        if endpoint in self._endpoint_failures:
            _, count = self._endpoint_failures[endpoint]
            self._endpoint_failures[endpoint] = (datetime.now(), count + 1)
            print(f"[RATE_LIMIT] 📉 Endpoint échec #{count + 1}: {endpoint}")
        else:
            self._endpoint_failures[endpoint] = (datetime.now(), 1)
            print(f"[RATE_LIMIT] 📉 Endpoint échec #1: {endpoint}")
    
    def mark_endpoint_success(self, endpoint: str):
        """
        Réinitialise le compteur d'échecs d'un endpoint (sur succès).
        
        Args:
            endpoint: URL de l'endpoint qui a réussi
        
        Usage:
            result = await try_endpoint(api_url, ...)
            if result:
                rate_limiter.mark_endpoint_success(api_url)
        """
        if endpoint in self._endpoint_failures:
            _, count = self._endpoint_failures[endpoint]
            del self._endpoint_failures[endpoint]
            print(f"[RATE_LIMIT] 📈 Endpoint récupéré après {count} échec(s): {endpoint}")
    
    def check_wiki_rate_limit(self) -> tuple[bool, float]:
        """
        Rate limit global pour Wikipedia API (1 requête/seconde).
        
        Returns:
            (allowed, remaining_sec)
            - allowed: True si appel Wikipedia autorisé
            - remaining_sec: Secondes à attendre si rate limited
        
        Usage:
            allowed, remaining = rate_limiter.check_wiki_rate_limit()
            if not allowed:
                await asyncio.sleep(remaining)
        """
        now = time.time()
        elapsed = now - self._last_wiki_call
        
        if elapsed < 1.0:
            return False, 1.0 - elapsed
        
        self._last_wiki_call = now
        return True, 0.0
    
    def get_memory_usage(self) -> dict:
        """
        Retourne des stats RAM pour monitoring/debug.
        
        Returns:
            Dict avec:
            - user_cooldowns_count: Nombre d'users en cooldown
            - user_llm_calls_count: Nombre d'users en rate limit LLM
            - endpoint_failures_count: Nombre d'endpoints échoués
            - estimated_bytes: RAM estimée en bytes
        
        Usage:
            stats = rate_limiter.get_memory_usage()
            print(f"RAM: {stats['estimated_bytes'] / 1024:.2f} KB")
        """
        import sys
        return {
            "user_cooldowns_count": len(self._user_cooldowns),
            "user_llm_calls_count": len(self._user_llm_calls),
            "endpoint_failures_count": len(self._endpoint_failures),
            "estimated_bytes": (
                sys.getsizeof(self._user_cooldowns) +
                sys.getsizeof(self._user_llm_calls) +
                sys.getsizeof(self._endpoint_failures)
            )
        }
    
    def reset_user_cooldowns(self):
        """Réinitialise tous les cooldowns users (debug/tests)."""
        self._user_cooldowns.clear()
        self._user_llm_calls.clear()
        print("[RATE_LIMIT] 🔄 Reset tous les cooldowns users")
    
    def reset_endpoint_failures(self):
        """Réinitialise tous les échecs endpoints (debug/tests)."""
        self._endpoint_failures.clear()
        print("[RATE_LIMIT] 🔄 Reset tous les échecs endpoints")


# Instance globale (singleton)
rate_limiter = RateLimiter(max_users=1000)
