"""Prompt loading and building utilities for SerdaBot."""

import os
from typing import Optional, Sequence

from cogs.roast_manager import DEFAULT_PATH, load_roast_config


# === SYSTEM PROMPT (chargé une seule fois) ===
_SYSTEM_PROMPT: Optional[str] = None

# === ROAST CONFIG (cache rechargeable) ===
_roast_cache = load_roast_config(DEFAULT_PATH)

# === MODE STYLES (ultra légers) ===
MODE_STYLES = {
    "chill": "Ton complice et décontracté.",
    "ask": "Ton clair et direct.",
    "trad": "Traduis en français naturel.",
    "reactor": "Réagis à la hype liée au jeu.",
}

# Budget pour garder le prompt USER compact
USER_BUDGET = 180  # chars max pour le user prompt


def _clip(s: str, n: int) -> str:
    """Coupe proprement une string à n chars."""
    return s if len(s) <= n else s[: max(0, n - 1)].rstrip() + "…"


def _join_short_quotes(quotes: Sequence[str], max_quotes: int = 3, per_quote_max: int = 28) -> str:
    """Joint max 3 quotes courtes (28 chars max chacune)."""
    if not quotes:
        return ""
    short = []
    for q in quotes:
        q = q.strip().strip('«»"\' ').replace("\n", " ")
        if not q:
            continue
        short.append(_clip(q, per_quote_max))
        if len(short) >= max_quotes:
            break
    return " | ".join(short)


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
    Build compact USER prompt with budget control (no overload).
    
    Args:
        mode: Command type ('ask', 'chill', 'trad', 'reactor')
        content: User message content
        user: Username who sent the message
        game: Current game being played (optional)
        title: Stream title (optional)
    
    Returns:
        Formatted user prompt string (≤180 chars target)
    """
    mode = (mode or "chill").lower()
    game = game or "inconnu"
    title = title or "-"
    
    # Base: Mode + Jeu + Titre + Style + Message
    parts = [
        f"Mode: {mode}.",
        f"Jeu: {game}.",
        f"Titre: {title}.",
        MODE_STYLES.get(mode, ""),
        f"Viewer «{content}».",
    ]
    
    # Roast compact si user éligible
    roast_users = {u.lower() for u in _roast_cache.get("users", [])}
    quotes = _roast_cache.get("quotes", [])
    is_roast = user.lower() in roast_users
    
    if is_roast:
        parts.append(f"Roast {user}: taquin, drôle, jamais méchant.")
        rq = _join_short_quotes(quotes, max_quotes=3, per_quote_max=28)
        if rq:
            parts.append(f"Réf. possibles: {rq}.")
    
    parts.append("Réponds dans ton style habituel, une phrase unique.")
    user_prompt = " ".join(p for p in parts if p)
    
    # Budget control: clip proprement si > 180 chars
    if len(user_prompt) > USER_BUDGET:
        # Garde Mode + Jeu + Titre (prioritaires)
        head = " ".join(parts[:3])
        tail = " ".join(parts[3:])
        allowed = max(0, USER_BUDGET - len(head) - 1)
        user_prompt = head + " " + _clip(tail, allowed)
    
    return user_prompt

