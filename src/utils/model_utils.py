"""Utilities for communicating with the configured LLM endpoints.

This module implements a small priority/fallback strategy:
- Primary: local LM Studio endpoint (configured in config['bot']['model_endpoint'])
- Fallback: OpenAI Async client if an API key is present

The implementation intentionally keeps behavior simple and robust:
- No DeadBot or other secondary local endpoints are contacted.
- Endpoints that fail are cached for a short duration to avoid retry storms.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx

# Ajouter le répertoire parent au path pour les imports
if os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from prompts.prompt_loader import load_system_prompt

# Token and temperature defaults (fallback si config absent)
MAX_TOKENS_ASK_DEFAULT = 120
MAX_TOKENS_CHILL_DEFAULT = 150    # Augmenté pour réponses complètes sans troncature
TEMP_ASK_DEFAULT = 0.4
TEMP_CHILL_DEFAULT = 0.8          # Créatif pour mode CHILL


def estimate_tokens(text: str) -> int:
    """Estimate token count using simple heuristic (4 chars ≈ 1 token)."""
    if not text:
        return 0
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
) -> Optional[str]:
    """Call the preferred model endpoint, falling back to OpenAI if needed.

    Returns:
        str: LLM response content (success)
        None: All LLMs unavailable → caller should use fallback responses
    
    Cascade behavior:
        1. Try LM Studio (local) → if success, return response
        2. Try OpenAI (cloud) → if success, return response  
        3. All failed → return None (fallback to fun responses)
    
    Note: None means "no LLM available", empty string "" means "LLM responded but empty".
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

        # Lire depuis config.yaml (avec fallback sur defaults)
        bot_config = config.get("bot", {}) if config else {}
        if mode == "ask":
            max_tokens = bot_config.get("max_tokens_ask", MAX_TOKENS_ASK_DEFAULT)
            temperature = bot_config.get("temperature_ask", TEMP_ASK_DEFAULT)
        else:
            max_tokens = bot_config.get("max_tokens_chill", MAX_TOKENS_CHILL_DEFAULT)
            temperature = bot_config.get("temperature_chill", TEMP_CHILL_DEFAULT)
        
        repeat_penalty = 1.05  # Légère pénalité pour éviter répétitions bizarres
        model_name = bot_config.get("model_name", "local-model")

        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "repeat_penalty": repeat_penalty,
            "top_p": 0.9,  # Nucleus sampling pour cohérence
        }
        
        # DEBUG: Logger le payload complet
        print(f"[PAYLOAD] 📦 Envoi à LM Studio: max_tokens={max_tokens}, temp={temperature}, model={model_name}")

        start_time = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=timeout)
            if response.status_code != 200:
                print(f"[MODEL] ❌ {endpoint_type.upper()} error: {response.status_code}")
                return ""

            duration = time.time() - start_time
            data = response.json()

            # Extraire les vraies métriques usage si disponibles
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            finish_reason = None

            # Compatible avec format OpenAI-like ou LM Studio
            result = ""
            if isinstance(data, dict):
                if "choices" in data and data["choices"]:
                    # OpenAI-like
                    choice = data["choices"][0]
                    if isinstance(choice, dict) and choice.get("message"):
                        result = choice["message"].get("content", "")
                    # Extraire finish_reason
                    finish_reason = choice.get("finish_reason")
                else:
                    # LM Studio sometimes returns {'response': '...'}
                    result = data.get("response", "") or data.get("text", "")

            result = (result or "").strip()
            if not result:
                print("[MODEL] ⚠️ Réponse vide reçue de l'endpoint")
                return ""

            output_chars = len(result)
            output_tokens = completion_tokens if completion_tokens > 0 else estimate_tokens(result)
            tokens_per_sec = output_tokens / duration if duration > 0 else 0

            print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, {output_tokens} tokens (real)")
            print(f"[METRICS] 📊 USAGE: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")
            print(f"[METRICS] 🏁 FINISH: {finish_reason or 'unknown'}")
            print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
            print(f"[MODEL] ✅ {endpoint_type.upper()} réponse complète")
            print(f"[DEBUG] 💬 OUTPUT: {result}")
            return result

    except Exception as e:  # network/parsing errors
        print(f"[MODEL] ❌ {endpoint_type.upper()} failed: {e}")
        return ""


async def try_openai_fallback(prompt: str, config: dict, user: Optional[str], mode: str = "chill") -> Optional[str]:
    """Fallback to OpenAI Async client.
    
    Returns:
        str: OpenAI response (success)
        None: No API key or OpenAI failed
    """

    try:
        # Dynamic import to avoid hard dependency at import time
        from openai import AsyncOpenAI  # type: ignore

        api_key = config.get("openai", {}).get("api_key")
        if not api_key or not api_key.startswith("sk-"):
            print("[MODEL] ⚠️ Pas de clé OpenAI configurée")
            return None

        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")

        client = AsyncOpenAI(api_key=api_key)
        bot_config = config.get("bot", {}) if config else {}
        model = bot_config.get("openai_model", "gpt-4o-mini")

        system_prompt = load_system_prompt(mode=mode)
        start_time = time.time()

        # Lire depuis config.yaml (avec fallback)
        if mode == "ask":
            max_tokens = bot_config.get("max_tokens_ask", MAX_TOKENS_ASK_DEFAULT)
            temperature = bot_config.get("temperature_ask", TEMP_ASK_DEFAULT)
        else:
            max_tokens = bot_config.get("max_tokens_chill", MAX_TOKENS_CHILL_DEFAULT)
            temperature = bot_config.get("temperature_chill", TEMP_CHILL_DEFAULT)

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
            print("[MODEL] ⚠️ Réponse vide d'OpenAI")
            return None

        output_chars = len(result)
        output_tokens = estimate_tokens(result)
        tokens_per_sec = output_tokens / duration if duration > 0 else 0

        print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, ~{output_tokens} tokens")
        print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
        print("[MODEL] ✅ OPENAI fallback utilisé")
        return result

    except Exception as e:
        print(f"[MODEL] ❌ OpenAI fallback failed: {e}")
        return None
