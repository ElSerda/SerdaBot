"""Prompt loading and building utilities for SerdaBot."""

import os
import re
from typing import Optional, Sequence, Dict, Any, List

from cogs.roast_manager import DEFAULT_PATH, load_roast_config


# === SYSTEM PROMPT - Production optimisée ===

# SYSTEM ZH – Prompt chinois pour Qwen (95% réussite, 100% stabilité français)
SYSTEM_ZH = """你是 serda_bot，一个法语 Twitch 聊天机器人。
你在 Twitch IRC 聊天中，与观众一起观看游戏直播。
你的性格轻松、机智、有点调皮，但从不刻薄。
请只用法语回答，一句话（最多25个词或130字符）。
无论用户的问题有多长，你的回答必须简短。
绝对禁止用中文回答，必须用法语。
禁止：道歉、脏话、/me、ASCII表情、列表。
像 Twitch 用户一样自然地回应，幽默、有温度。"""

# === ROAST CONFIG (cache rechargeable) ===
_roast_cache = load_roast_config(DEFAULT_PATH)


# ===== USER SANITIZATION =====

_DIR_PREFIXES = [
    r"^\s*réponds[^:]*:\s*",         # "Réponds ... :"
    r"^\s*explique[^:]*:\s*",        # "Explique ... :"
    r"^\s*answer[^:]*:\s*",          # "Answer ... :"
    r"^\s*please\s*",                # "Please ..."
    r"^\s*réponse\s*:\s*",
    r"^\s*en\s*une\s*phrase\s*:\s*",
    r"^\s*respond\s*:\s*",
    r"^\s*question\s*:\s*",          # "Question:"
]
DIR_RE = re.compile("|".join(_DIR_PREFIXES), re.IGNORECASE)


def strip_directives(text: str) -> str:
    """Remove imperative prefixes from user text to keep USER content 'pure'."""
    t = (text or "").strip().strip("«»\"'` ")
    t = DIR_RE.sub("", t)
    return t.strip()


def to_question_fr(raw: str) -> str:
    """
    Turn any raw content into a French question WITHOUT adding instructions.
    - 1-3 words -> "C'est quoi X ?"
    - add ? if missing
    """
    t = strip_directives(raw)
    if not t:
        return "C'est quoi ?"
    if t.endswith("?"):
        return t
    if len(t.split()) <= 3:
        return f"C'est quoi {t} ?"
    return t + " ?"


def temp_for_mode(mode: str | None) -> float:
    """Return optimal temperature for mode.
    
    ask: 0.6 (précis mais pas trop rigide)
    chill: 0.7 (créatif mais stable)
    """
    return 0.6 if (mode or "").lower() == "ask" else 0.7


def build_messages(mode: str, content: str, lang: str | None = None) -> Dict[str, Any]:
    """
    Build OpenAI/LM-Studio compatible messages structure.
    
    Returns dict with:
        - system: str
        - messages: List[Dict[str, str]]
        - temperature: float
    """
    system = load_system_prompt(lang)
    mode_norm = (mode or "chill").lower()
    
    # Mode ask : reformule en question pour clarifier l'intention
    # Mode chill : texte brut (juste nettoyage directives)
    if mode_norm == "ask":
        user_text = to_question_fr(content)
    else:
        user_text = strip_directives(content)

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_text},
    ]
    
    return {
        "system": system,
        "messages": messages,
        "temperature": temp_for_mode(mode_norm)
    }


def make_openai_payload(model: str, built: Dict[str, Any], max_tokens: int = 60, stop: List[str] | None = None) -> Dict[str, Any]:
    """
    Build a payload for OpenAI-compatible /v1/chat/completions endpoints (e.g., LM Studio).
    
    Temperature from built dict overrides LM Studio settings!
    """
    return {
        "model": model,
        "messages": built["messages"],
        "temperature": built["temperature"],  # Override LM Studio!
        "top_p": 0.9,
        "top_k": 40,
        "min_p": 0.05,
        "repeat_penalty": 1.10,
        "max_tokens": max_tokens,
        "stop": stop or ["\nUser:", "\nAssistant:"],
    }

# === MODE STYLES (ultra légers) ===
MODE_STYLES = {
    "chill": "Réponds sur ton complice.",
    "ask": "Explique brièvement:",
    "trad": "Traduis en FR:",
    "reactor": "Réagis à la hype.",
}

# Budget pour garder le prompt USER compact
USER_BUDGET = 180  # chars max pour le user prompt


def _clip(s: str, n: int) -> str:
    """Coupe proprement une string à n chars."""
    return s if len(s) <= n else s[: max(0, n - 1)].rstrip() + "…"


def _short_quotes(quotes: Sequence[str], n: int = 2, per_quote_max: int = 35) -> list:
    """Clip quotes pour éviter dépassement budget. Max 2 quotes, 35 chars chacune."""
    out = []
    for q in (quotes or []):
        q = (q or "").strip().replace("\n", " ")
        if not q:
            continue
        if len(q) > per_quote_max:
            q = q[:per_quote_max].rstrip() + "…"
        out.append(q)
        if len(out) >= n:
            break
    return out


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


def load_system_prompt(lang: str | None = None) -> str:
    """
    Load system prompt optimized for Qwen.
    
    Args:
        lang: Ignored (kept for API compatibility). Always returns ZH prompt.
    
    Returns:
        SYSTEM_ZH - Chinese instructions for best performance with Qwen
                    (95% success rate, 100% French stability)
    """
    return SYSTEM_ZH


def make_prompt(
    mode: str,
    content: str,
    user: str,
    game: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """
    Build USER prompt with sanitization and smart reformulation.
    
    Args:
        mode: Command type ('ask', 'chill', 'trad', 'reactor')
        content: User message content
        user: Username who sent the message
        game: IGNORED (kept for API compatibility)
        title: IGNORED (kept for API compatibility)
    
    Returns:
        Clean user message (reformulated for ask if needed)
    """
    mode = (mode or "chill").lower()
    
    # Pour ask: sanitize + reformule en question
    if mode == "ask":
        return to_question_fr(content)
    
    # Pour chill/autres: juste sanitize
    return strip_directives(content)

