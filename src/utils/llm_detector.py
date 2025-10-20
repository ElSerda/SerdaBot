"""Détection de la disponibilité du LLM local.

Ce module permet de vérifier si un LLM local (LM Studio) est accessible
et de déterminer automatiquement si le bot doit utiliser le mode fallback.
"""

import os
import httpx
from typing import Optional


def is_llm_available(endpoint: str = "http://localhost:1234/v1/models", timeout: float = 2.0) -> bool:
    """
    Vérifie si le LLM local est disponible.
    
    Args:
        endpoint: URL de l'endpoint du LLM (ex: LM Studio)
        timeout: Timeout de la requête en secondes
    
    Returns:
        True si le LLM est accessible, False sinon
    
    Exemples:
        >>> is_llm_available()
        True  # Si LM Studio est lancé
        
        >>> is_llm_available()
        False  # Si LM Studio est arrêté ou en CI
    """
    # En CI, pas de LLM disponible
    if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
        return False
    
    # Tente de contacter le LLM
    try:
        response = httpx.get(endpoint, timeout=timeout)
        return response.status_code == 200
    except (httpx.RequestError, httpx.TimeoutException, Exception):
        return False


def check_llm_status(config: dict) -> tuple[bool, Optional[str]]:
    """
    Vérifie le statut du LLM et retourne un message informatif.
    
    Args:
        config: Configuration du bot (contient l'endpoint du modèle)
    
    Returns:
        Tuple (disponible: bool, message: str)
    
    Exemples:
        >>> check_llm_status(config)
        (True, "✅ LLM détecté : http://localhost:1234/v1")
        
        >>> check_llm_status(config)
        (False, "⚠️  LLM non disponible → mode fallback activé")
    """
    endpoint = config.get("bot", {}).get("model_endpoint", "http://localhost:1234/v1/models")
    
    # Convertir l'endpoint chat en endpoint models pour le check
    if "/chat/completions" in endpoint:
        check_endpoint = endpoint.replace("/chat/completions", "/models")
    else:
        check_endpoint = endpoint
    
    available = is_llm_available(check_endpoint)
    
    if available:
        return True, f"✅ LLM détecté : {endpoint}"
    else:
        return False, "⚠️  LLM non disponible → mode fallback activé"


def get_llm_mode(config: dict) -> str:
    """
    Détermine le mode LLM à utiliser selon la config.
    
    Args:
        config: Configuration du bot
    
    Returns:
        "enabled" | "disabled" | "auto"
    
    Priorité :
        1. Variable d'environnement LLM_MODE
        2. Config llm.enabled (si présente)
        3. Défaut : "auto" (détection automatique)
    """
    # Override via variable d'environnement
    env_mode = os.getenv("LLM_MODE")
    if env_mode in ["enabled", "disabled", "auto"]:
        return env_mode
    
    # Config explicite (future feature)
    llm_config = config.get("bot", {}).get("llm", {})
    if isinstance(llm_config, dict):
        enabled = llm_config.get("enabled", "auto")
        if enabled is True:
            return "enabled"
        elif enabled is False:
            return "disabled"
        elif enabled == "auto":
            return "auto"
    
    # Défaut : auto-détection
    return "auto"
