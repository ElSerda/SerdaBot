"""Prompt loading and building utilities for SerdaBot."""

import re
from typing import Optional, Sequence, Dict, Any, List


# === SYSTEM PROMPT - Production optimisée ===

# SYSTEM ASK – Prompt factuel pour questions (SANS exemples - test naturel)
SYSTEM_ASK_FINAL = """Réponds de façon concise et précise en 1-2 phrases. Maximum 230 caractères.
Si tu ne sais pas ou si la question concerne des événements après 2023, dis clairement que tu ne sais pas.
Tes données s'arrêtent en 2023, sois honnête si on te demande des infos récentes.
"""

# SYSTEM CHILL – Prompt fun/cool pour interactions sociales
SYSTEM_CHILL_FINAL = """Tu es serda_bot, bot Twitch cool et décontracté.
Adapte ta réponse : 2-6 mots pour réactions simples (minimum 10 caractères), jusqu'à 2 phrases courtes si question intéressante.
Pour questions complexes nécessitant explications détaillées, suggère '!ask' plutôt.
Tes connaissances s'arrêtent en 2023. Si question sur événements après 2023, dis que tu ne sais pas.
Style naturel Twitch, pas de formules de robot. TERMINE TOUJOURS tes phrases.

Exemples:
"Salut !" → "Yo !"
"lol" → "Marrant."
"gg" → "Stylé !"
"comment ça va ?" → "Nickel, et toi ?"
"t'es qui toi ?" → "Serda_Bot, le bot du stream."
"tu fais quoi ?" → "Je traine sur le chat."
"apprends moi un truc" → "Les pandas dorment 14h par jour. Stylé non ?"
"tu as quelque chose à dire ?" → "Ouais, le stream est cool aujourd'hui."
"c'est quoi ton role ?" → "Je commente et réponds aux questions."
"""


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
    - Remove duplicate "c'est quoi" if already present
    """
    t = strip_directives(raw)
    
    # Enlever "c'est quoi" au début si déjà présent
    t_lower = t.lower()
    if t_lower.startswith("c'est quoi "):
        t = t[11:].strip()  # Remove "c'est quoi "
    elif t_lower.startswith("c quoi "):
        t = t[7:].strip()  # Remove "c quoi "
    
    if not t:
        return "C'est quoi ? Réponds en une phrase."
    if len(t.split()) <= 3:
        return f"C'est quoi {t} ? Réponds en une phrase."
    return f"{t} ? Réponds en une phrase."


def build_messages(mode: str, content: str, lang: str | None = None, extract_metadata: bool = False) -> Dict[str, Any]:
    """
    Build OpenAI/LM-Studio compatible messages structure.
    
    Args:
        mode: Command mode ('ask' or 'chill')
        content: User input message
        lang: Language for system prompt (default: 'zh')
        extract_metadata: If True, enforce JSON output with metadata
    
    Returns dict with:
        - system: str
        - messages: List[Dict[str, str]]
        - temperature: float
    """
    mode_norm = (mode or "chill").lower()
    
    # Choisir le bon prompt selon le mode
    if mode_norm == "ask":
        system = SYSTEM_ASK_FINAL
    else:
        system = SYSTEM_CHILL_FINAL
    
    # Renforcement JSON si metadata activée
    if extract_metadata:
        system += '\n\n⚠️ IMPORTANT: Réponds UNIQUEMENT en JSON valide. Format strict: {"m":"ton message en français","t":"tone","c":0.9}. Aucun texte avant ou après le JSON.'
    
    # Mode ask : reformule en question pour clarifier l'intention
    # Mode chill : texte brut (juste nettoyage directives)
    if mode_norm == "ask":
        user_text = to_question_fr(content)
    else:
        user_text = strip_directives(content)

    # Few-shot enrichi pour mode chill (inclut réactions + questions + anti-anecdotes)
    if mode_norm == "chill" and not extract_metadata:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": "lol"},
            {"role": "assistant", "content": "Marrant."},
            {"role": "user", "content": "t'es qui toi ?"},
            {"role": "assistant", "content": "Le bot du stream."},
            {"role": "user", "content": "raconte une anecdote"},
            {"role": "assistant", "content": "Pas d'anecdotes perso 😉"},
            {"role": "user", "content": "ton avis sur l'IA ?"},
            {"role": "assistant", "content": "Prometteur, à encadrer."},
            {"role": "user", "content": user_text},
        ]
    else:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ]
    
    # Température réduite pour JSON (plus stable)
    if extract_metadata:
        temperature = 0.4  # Strict pour garantir JSON valide
    else:
        temperature = 0.4 if mode_norm == "ask" else 0.5
    
    return {
        "system": system,
        "messages": messages,
        "temperature": temperature
    }


def get_response_format(extract_metadata: bool = False) -> Dict[str, Any] | None:
    """
    Generate optimized JSON Schema for structured output.
    
    Args:
        extract_metadata: If True, force JSON output with message + tone metadata
    
    Returns:
        JSON Schema dict or None (for normal text output)
    
    Note:
        Uses short keys (m/t/c) to reduce token overhead by ~30%
    """
    if not extract_metadata:
        return None
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "r",  # Short name
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "m": {
                        "type": "string",
                        "description": "Message (français, max 130 chars)"
                    },
                    "t": {
                        "type": "string",
                        "enum": ["complice", "taquin", "hype", "neutre", "sarcastique"],
                        "description": "Tone"
                    },
                    "c": {
                        "type": "number",
                        "description": "Confidence (0.0-1.0)"
                    }
                },
                "required": ["m", "t"],
                "additionalProperties": False
            }
        }
    }


def make_openai_payload(
    model: str, 
    built: Dict[str, Any], 
    max_tokens: int = 60, 
    stop: List[str] | None = None,
    extract_metadata: bool = False
) -> Dict[str, Any]:
    """
    Build a payload for OpenAI-compatible /v1/chat/completions endpoints (e.g., LM Studio).
    
    Args:
        model: Model name
        built: Output from build_messages()
        max_tokens: Maximum tokens to generate (80 ASK, 20 CHILL optimaux)
        stop: Stop sequences
        extract_metadata: If True, use JSON Schema to extract tone/confidence metadata
    
    Returns:
        API payload dict
    
    Note:
        Temperature from built dict overrides LM Studio settings!
        Config optimale: ASK 80 tokens + temp 0.4 (200 chars prompt → réel ≤250), CHILL 20 tokens + temp 0.5 (95% succès validé)
    """
    # Déterminer mode depuis les messages pour config optimale
    mode = "ask" if "C'est quoi" in str(built["messages"]) or "?" in str(built["messages"][-1].get("content", "")) else "chill"
    
    # Config optimale par mode (93% ASK + 80% CHILL validé)
    if mode == "ask":
        optimal_max_tokens = 120  # ~250-300 chars réels, explications développées
        optimal_stop = ["\n\n"]  # Stop paragraphes seulement
        optimal_repeat = 1.1
    else:
        optimal_max_tokens = 40  # Permet 1-2 phrases courtes (≈80-100 chars)
        optimal_stop = None  # Pas de stop, naturel
        optimal_repeat = 1.0
    
    payload = {
        "model": model,
        "messages": built["messages"],
        "temperature": built["temperature"],  # Override LM Studio!
        "top_p": 0.9,
        "top_k": 40,
        "min_p": 0.05,
        "repeat_penalty": optimal_repeat,
        "max_tokens": max_tokens if max_tokens != 60 else optimal_max_tokens,  # Use optimal si default
        "stop": stop if stop is not None else optimal_stop,
    }
    
    # Add structured output if requested
    response_format = get_response_format(extract_metadata)
    if response_format:
        payload["response_format"] = response_format
    
    return payload

def parse_structured_response(response_text: str) -> Dict[str, Any]:
    """
    Parse structured JSON response from LLM with robust fallback.
    
    Args:
        response_text: Raw response text (should be JSON if extract_metadata=True)
    
    Returns:
        Dict with keys:
        - message: str (the actual response text)
        - tone: str | None (detected tone)
        - confidence: float | None (confidence score)
    
    Note:
        Accepts both short keys (m/t/c) and long keys (message/tone/confidence)
        for backward compatibility and robustness.
    """
    import json
    
    try:
        # Try to extract JSON if surrounded by text
        # Match: {...} or just parse directly
        json_match = re.search(r'\{[^{}]*"[mtc]"[^{}]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)
        
        parsed = json.loads(response_text)
        
        # Robust parser: accepts both short (m/t/c) and long keys
        return {
            "message": parsed.get("m") or parsed.get("message") or response_text,
            "tone": parsed.get("t") or parsed.get("tone"),
            "confidence": parsed.get("c") or parsed.get("confidence")
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        # Fallback: treat as plain text
        return {
            "message": response_text.strip(),
            "tone": None,
            "confidence": None
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


def load_system_prompt(lang: str | None = None, mode: str = "chill") -> str:
    """
    Load system prompt optimized for Qwen 2.5-1.5B-Instruct.
    
    Args:
        lang: Ignored (kept for API compatibility)
        mode: Command mode ('ask' or 'chill')
    
    Returns:
        SYSTEM_ASK_FINAL for ask mode (factual, 200 chars limit)
        SYSTEM_CHILL_FINAL for chill mode (fun/cool, 1-5 words)
    """
    if mode == "ask":
        return SYSTEM_ASK_FINAL
    return SYSTEM_CHILL_FINAL


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

