"""Prompt loading and building utilities for SerdaBot."""

import os
from typing import Optional

from cogs.roast_manager import DEFAULT_PATH, load_roast_config


# === SYSTEM PROMPT (chargé une seule fois) ===
_SYSTEM_PROMPT: Optional[str] = None

# === ROAST CONFIG (cache rechargeable) ===
_roast_cache = load_roast_config(DEFAULT_PATH)


def reload_roast_config(path: str = DEFAULT_PATH):
    """Reload roast configuration from disk (call after !addroast/!delroast)."""
    global _roast_cache
    _roast_cache = load_roast_config(path)


def load_system_prompt() -> str:
    """Load the universal system prompt for serda_bot."""
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, 'prompt_system.txt')
        with open(path, 'r', encoding='utf-8') as f:
            _SYSTEM_PROMPT = f.read().strip()
    return _SYSTEM_PROMPT


def make_prompt(
    mode: str,
    content: str,
    user: str,
    game: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """
    Build the 'user' prompt to send to LM Studio.
    Includes dynamic roast logic based on roast.json config.
    
    Args:
        mode: Command type ('ask', 'chill', 'trad', 'reactor', etc.)
        content: User message content
        user: Username who sent the message
        game: Current game being played (optional)
        title: Stream title (optional)
    
    Returns:
        Formatted user prompt string
    """
    base = f"Contexte: Jeu={game or 'inconnu'}, Titre={title or '-'}.\n"
    
    # Dynamic roast detection (not hardcoded!)
    roast_users = {u.lower() for u in _roast_cache.get("users", [])}
    quotes = _roast_cache.get("quotes", [])
    
    if user.lower() in roast_users:
        base += (
            f"Le message vient de ton créateur/roast-target ({user}). "
            "Active un roast taquin (jamais méchant). "
        )
        if quotes:
            # Inject up to 8 quotes for context
            joined = " | ".join(quotes[:8])
            base += f"Tu peux t'inspirer de ses excuses/citations: {joined}.\n"
    
    # Command-specific prompts
    if mode == "ask":
        base += f"Question du viewer: «{content}». Réponds clairement, en 1 phrase, sans détour."
    elif mode == "chill":
        base += f"Viewer dit: «{content}». Réponds sur un ton complice et fun."
    elif mode == "trad":
        base += f"Texte à traduire: «{content}». Traduis naturellement en français courant du chat Twitch."
    elif mode == "reactor":
        base += (
            f"Le chat spam «{content}». Réagis avec une phrase drôle et en lien avec {game or 'le jeu'}, "
            "comme si tu participais à la hype collective."
        )
    else:
        base += f"Message: «{content}». Réponds naturellement, comme dans une conversation de stream."
    
    return base.strip()


def load_prompt_template(name, lang='en'):
    """
    DEPRECATED: Legacy function for backward compatibility.
    Use make_prompt() instead for new code.
    """
    # Fallback pour les anciens fichiers de prompt s'ils existent encore
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f'prompt_{name}_{lang}.txt'
    path = os.path.join(current_dir, filename)

    if not os.path.isfile(path):
        fallback_path = os.path.join(current_dir, f'prompt_{name}_en.txt')
        if os.path.isfile(fallback_path):
            path = fallback_path
        else:
            raise FileNotFoundError(
                f'Prompt file not found: {path} or fallback {fallback_path}'
            )

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
