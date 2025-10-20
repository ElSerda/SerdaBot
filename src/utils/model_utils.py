"""Utilities for communicating with the configured LLM endpoints.

This module implements a small priority/fallback strategy:
- Primary: local LM Studio endpoint (configured in config['bot']['model_endpoint'])
- Fallback: OpenAI Async client if an API key is present

The implementation intentionally keeps behavior simple and robust:
- No DeadBot or other secondary local endpoints are contacted.
- Endpoints that fail are cached for a short duration to avoid retry storms.
"""

from __future__ import annotations

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx

# Ajouter le répertoire parent au path pour les imports
if os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from prompts.prompt_loader import load_system_prompt

# Token and temperature defaults (empirical)
MAX_TOKENS_ASK = 120
MAX_TOKENS_CHILL = 80    # Augmenté de 60→80 pour phrases complètes avec nouveau prompt
TEMP_ASK = 0.4
TEMP_CHILL = 0.6         # Réduit de 0.7→0.6 pour moins d'aléatoire


def estimate_tokens(text: str) -> int:
    """Approximate token count (~4 chars per token)."""
    return max(1, len(text) // 4)


# Simple in-memory cache of failed endpoints to avoid immediate retries
_failed_endpoints: dict[str, datetime] = {}
_CACHE_DURATION = timedelta(minutes=2)


async def call_model(
    prompt: str,
    config: dict,
    user: Optional[str] = None,
    timeout: Optional[int] = None,
    mode: str = "chill",
) -> str:
    """Call the preferred model endpoint, falling back to OpenAI if needed.

    Returns the model response as a string or an empty string on failure.
    """

    effective_timeout = timeout if timeout is not None else config.get("bot", {}).get("model_timeout", 10)
    print(f"[MODEL] ⏱️ Timeout configuré: {effective_timeout}s")

    # Expire old failed endpoints
    now = datetime.now()
    expired = [k for k, v in _failed_endpoints.items() if now - v > _CACHE_DURATION]
    for k in expired:
        del _failed_endpoints[k]
        print(f"[MODEL] 🔄 Réactivation de {k}")

    api_url = config.get("bot", {}).get("model_endpoint") or config.get("bot", {}).get("api_url")

    # Try LM Studio-like endpoint if configured and not recently marked failed
    if api_url and api_url not in _failed_endpoints:
        print("[MODEL] 🔗 Tentative LM Studio...")
        result = await try_endpoint(api_url, prompt, user, effective_timeout, endpoint_type="lm_studio", mode=mode, config=config)
        if result:
            return result
        _failed_endpoints[api_url] = now
        print("[MODEL] ⚠️ Endpoint local indisponible, passer au fallback")

    print("[MODEL] 🌐 Utilisation du fallback OpenAI (si configuré)")
    return await try_openai_fallback(prompt, config, user, mode)


async def try_endpoint(
    api_url: str,
    prompt: str,
    user: Optional[str],
    timeout: int,
    endpoint_type: str = "lm_studio",
    mode: str = "chill",
    config: Optional[dict] = None,
) -> str:
    """Attempt to call a single HTTP endpoint and return the text result.

    The function is tolerant: any networking or parsing error returns an empty string.
    """

    try:
        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")
        print(f"[DEBUG] 📄 USER Prompt: {prompt}")

        system_prompt = load_system_prompt(mode=mode)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

        max_tokens = MAX_TOKENS_ASK if mode == "ask" else MAX_TOKENS_CHILL
        temperature = TEMP_ASK if mode == "ask" else TEMP_CHILL
        repeat_penalty = 1.05  # Légère pénalité pour éviter répétitions bizarres

        model_name = config.get("bot", {}).get("model_name", "local-model") if config else "local-model"

        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "repeat_penalty": repeat_penalty,
            "top_p": 0.9,  # Nucleus sampling pour cohérence
        }

        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=timeout)
            if response.status_code != 200:
                print(f"[MODEL] ❌ {endpoint_type.upper()} error: {response.status_code}")
                return ""

            duration = time.time() - start_time
            data = response.json()

            # Compatible avec format OpenAI-like ou LM Studio
            result = ""
            if isinstance(data, dict):
                if "choices" in data and data["choices"]:
                    # OpenAI-like
                    choice = data["choices"][0]
                    if isinstance(choice, dict) and choice.get("message"):
                        result = choice["message"].get("content", "")
                else:
                    # LM Studio sometimes returns {'response': '...'}
                    result = data.get("response", "") or data.get("text", "")

            result = (result or "").strip()
            if not result:
                print("[MODEL] ⚠️ Réponse vide reçue de l'endpoint")
                return ""

            output_chars = len(result)
            output_tokens = estimate_tokens(result)
            tokens_per_sec = output_tokens / duration if duration > 0 else 0

            print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, ~{output_tokens} tokens")
            print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
            print(f"[MODEL] ✅ {endpoint_type.upper()} réponse complète")
            print(f"[DEBUG] 💬 OUTPUT: {result}")
            return result

    except Exception as e:  # network/parsing errors
        print(f"[MODEL] ❌ {endpoint_type.upper()} failed: {e}")
        return ""


async def try_openai_fallback(prompt: str, config: dict, user: Optional[str], mode: str = "chill") -> str:
    """Fallback to OpenAI Async client. Returns string or an explanatory message on failure."""

    try:
        # Dynamic import to avoid hard dependency at import time
        from openai import AsyncOpenAI  # type: ignore

        api_key = config.get("openai", {}).get("api_key")
        if not api_key or not api_key.startswith("sk-"):
            return "❌ Tous les modèles locaux indisponibles et pas de clé OpenAI"

        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")

        client = AsyncOpenAI(api_key=api_key)
        model = config.get("bot", {}).get("openai_model", "gpt-4o-mini")

        system_prompt = load_system_prompt(mode=mode)
        start_time = time.time()

        max_tokens = MAX_TOKENS_ASK if mode == "ask" else MAX_TOKENS_CHILL
        temperature = TEMP_ASK if mode == "ask" else TEMP_CHILL

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        duration = time.time() - start_time
        result = ""
        try:
            result = getattr(response.choices[0].message, "content", "") or str(response)
        except Exception:
            result = str(response)

        result = (result or "").strip()
        if not result:
            return "❌ Réponse vide d'OpenAI"

        output_chars = len(result)
        output_tokens = estimate_tokens(result)
        tokens_per_sec = output_tokens / duration if duration > 0 else 0

        print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, ~{output_tokens} tokens")
        print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
        print("[MODEL] ✅ OPENAI fallback utilisé")
        return result

    except Exception as e:
        print(f"[MODEL] ❌ OpenAI fallback failed: {e}")
        return "💀 SerdaBot en mode survie ! Tous mes cerveaux sont KO. Revenez dans 2 min ! 🔄"
