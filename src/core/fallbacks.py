"""Système de fallback pour les commandes nécessitant un LLM.

Ce module fournit des réponses pré-définies quand le LLM n'est pas disponible,
garantissant que le bot reste fonctionnel et amusant même sans modèle local.
"""

import random
from typing import Literal

# Répliques pré-définies par intention
FALLBACKS = {
    "ask": [
        "Je réfléchis… mais mon cerveau est en pause 🧠💤",
        "Pas de LLM dispo — je suis en mode robot vintage !",
        "Demande-moi plus tard, j'ai une migraine de modèle.",
        "Mon IA fait une sieste. Réessaie dans 5 minutes ? ☕",
        "Question intéressante, mais je suis en mode économie d'énergie 🔋",
        "Désolé, mon cerveau électronique est parti chercher des cigarettes… il revient jamais.",
        "J'ai besoin de mon LLM pour ça, et il est en vacances 🏖️",
        "Sans mon IA, je suis juste un bot qui dit des trucs random. Comme ça. 🤷",
    ],
    
    "chill": [
        "Salut ! 👋",
        "Yo !",
        "Coucou, ça gaze ?",
        "Hey ! 😊",
        "Wesh !",
        "Présent ! 🫡",
        "Yop !",
        "Ici ! 🙋",
        "Hello !",
        "Bien ou bien ?",
        "Ça roule ?",
        "Ouais ? 👀",
        "Chaud ! 🔥",
        "GG !",
        "Stylé !",
        "Tranquille 😎",
        "Écoute, je suis là, mais pas trop bavard aujourd'hui.",
        "Mon IA est en pause café, mais je te salue quand même ! ☕",
        "Pas de LLM = pas de blabla. Juste un 'yo' et on est bons. 👍",
    ],
    
    "ask_timeout": [
        "Trop dur pour moi… sans mon LLM, je suis perdu 😅",
        "Mon IA a timeout. Elle reviendra… peut-être.",
        "Le modèle a crashé. Comme Windows 98. Nostalgie. 💾",
        "Erreur 404 : Intelligence non trouvée.",
    ],
    
    "ask_error": [
        "Oups, j'ai planté. C'est pas ma faute, c'est le LLM ! 🤖💥",
        "Erreur critique : mon cerveau a bugué.",
        "Je crois que j'ai besoin d'un reboot… 🔄",
    ],
}


FallbackIntent = Literal["ask", "chill", "ask_timeout", "ask_error"]


def get_fallback_response(intent: FallbackIntent, mode: str = "fun") -> str:
    """
    Retourne une réponse fallback aléatoire selon l'intention.
    
    Args:
        intent: Type de réponse ("ask", "chill", "ask_timeout", "ask_error")
        mode: Style de réponse ("fun", "silent", "minimal")
    
    Returns:
        Une réponse textuelle adaptée
    
    Exemples:
        >>> get_fallback_response("ask")
        "Je réfléchis… mais mon cerveau est en pause 🧠💤"
        
        >>> get_fallback_response("chill")
        "Salut ! 👋"
        
        >>> get_fallback_response("ask", mode="silent")
        "Commande temporairement indisponible."
    """
    # Mode silent : réponse neutre
    if mode == "silent":
        return "Commande temporairement indisponible."
    
    # Mode minimal : juste un emoji
    if mode == "minimal":
        return "🤖"
    
    # Mode fun (par défaut) : répliques humoristiques
    responses = FALLBACKS.get(intent, FALLBACKS["chill"])
    return random.choice(responses)


def get_all_fallback_intents() -> list[str]:
    """Retourne la liste de toutes les intentions disponibles."""
    return list(FALLBACKS.keys())


def add_custom_fallback(intent: str, responses: list[str]) -> None:
    """
    Ajoute des réponses personnalisées pour une intention.
    
    Args:
        intent: Nom de l'intention
        responses: Liste de réponses possibles
    
    Exemples:
        >>> add_custom_fallback("custom", ["Réponse 1", "Réponse 2"])
        >>> get_fallback_response("custom")
        "Réponse 1"  # ou "Réponse 2"
    """
    if intent not in FALLBACKS:
        FALLBACKS[intent] = []
    FALLBACKS[intent].extend(responses)
