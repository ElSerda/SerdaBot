"""Utility functions for AI model communication."""

import time
from datetime import datetime, timedelta

import httpx

from prompts.prompt_loader import load_system_prompt


def estimate_tokens(text: str) -> int:
    """Estime le nombre de tokens (approximatif: ~4 chars = 1 token pour FR/EN)"""
    return len(text) // 4


def _detect_mode_from_messages(messages: list) -> str:
    """Détecte le mode depuis le contenu USER pour température adaptative."""
    if not messages:
        return "chill"
    user_content = messages[-1].get("content", "")
    return "ask" if "Explique brièvement:" in user_content else "chill"


def _temp_for_mode(messages: list) -> float:
    """Determine temperature based on detected mode from messages."""
    mode = _detect_mode_from_messages(messages)
    # ask = 0.55 (plus précis), autres = 0.7
    return 0.55 if mode == "ask" else 0.7

# Cache des endpoints down (évite de retenter inutilement)
_failed_endpoints = {}
_CACHE_DURATION = timedelta(minutes=2)  # Retest après 2 min


async def call_model(
    prompt: str, config: dict, user: str | None = None, timeout: int | None = None
) -> str:
    """Queries the model using the configured endpoint with fallback."""

    # Récupérer le timeout depuis la config ou utiliser 10s par défaut
    effective_timeout: int = timeout if timeout is not None else config.get("bot", {}).get("model_timeout", 10)

    print(f"[MODEL] ⏱️ Timeout configuré: {effective_timeout}s")

    # Nettoyer le cache des endpoints expirés
    now = datetime.now()
    expired = [k for k, v in _failed_endpoints.items() if now - v > _CACHE_DURATION]
    for k in expired:
        del _failed_endpoints[k]
        print(f"[MODEL] 🔄 Réactivation de {k}")

    # === PRIORITÉ 1: LM Studio ===
    api_url = config["bot"].get("model_endpoint") or config["bot"].get("api_url")
    if api_url and "1234" in api_url and api_url not in _failed_endpoints:
        print("[MODEL] 🔗 Tentative LM Studio...")
        result = await try_endpoint(api_url, prompt, user, effective_timeout, "lm_studio")
        if result:
            return result
        _failed_endpoints[api_url] = now
        print("[MODEL] ⚠️ LM Studio indisponible")
    elif api_url in _failed_endpoints:
        print("[MODEL] ⏭️ LM Studio skip (down)")

        # === PRIORITÉ 2: DeadBot ===
    deadbot_api = "http://127.0.0.1:5001/chat"
    if deadbot_api not in _failed_endpoints:
        print("[MODEL] 🔗 Tentative DeadBot...")
        result = await try_endpoint(deadbot_api, prompt, user, effective_timeout, "deadbot")
        if result:
            return result
        _failed_endpoints[deadbot_api] = now
        print("[MODEL] ⚠️ DeadBot indisponible")
    else:
        print("[MODEL] ⏭️ DeadBot skip (down)")

    # === PRIORITÉ 3: OpenAI API ===
    print("[MODEL] 🌐 Fallback OpenAI...")
    return await try_openai_fallback(prompt, config, user)


async def try_endpoint(
    api_url: str, prompt: str, user: str | None, timeout: int, endpoint_type: str
) -> str:
    """Essaie un endpoint spécifique"""
    try:
        # Métriques INPUT
        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")
        print(f"[DEBUG] 📄 USER Prompt: {prompt}")

        # Adapter le payload selon le type d'endpoint
        if endpoint_type == "lm_studio":
            system_prompt = load_system_prompt()
            print(f"[DEBUG] 🧠 SYSTEM Prompt ({len(system_prompt)} chars): {system_prompt}")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            temp = _temp_for_mode(messages)
            
            payload = {
                "model": "local-model",
                "messages": messages,
                "max_tokens": 250,  # Limite Twitch (500 chars) / 2
                "temperature": temp,
                "stream": False
            }
        else:
            # DeadBot FastAPI format
            payload = {"prompt": prompt}
            if user:
                payload["user"] = user

        # Démarrer le timer
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=timeout)

            if response.status_code == 200:
                # Calculer la durée
                duration = time.time() - start_time

                data = response.json()
                if "choices" in data and endpoint_type == "lm_studio":
                    result = data["choices"][0]["message"]["content"]
                elif "response" in data and endpoint_type == "deadbot":
                    result = data["response"]
                else:
                    result = data.get("response", "")

                # Métriques OUTPUT
                output_chars = len(result)
                output_tokens = estimate_tokens(result)
                tokens_per_sec = output_tokens / duration if duration > 0 else 0

                print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, ~{output_tokens} tokens")
                print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
                print(f"[DEBUG] 💬 OUTPUT: {result}")
                print(f"[MODEL] ✅ {endpoint_type.upper()} réponse complète")
                return result
            print(f"[MODEL] ❌ {endpoint_type.upper()} error: {response.status_code}")

    except (
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.ConnectError,
        httpx.TimeoutException,
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
    ) as e:
        print(f"[MODEL] ❌ {endpoint_type.upper()} failed: {type(e).__name__}")

    return ""


async def try_openai_fallback(
    prompt: str, config: dict, user: str | None  # pylint: disable=unused-argument
) -> str:
    """Fallback vers OpenAI si tous les endpoints locaux échouent"""
    try:
        # Import dynamique pour éviter les erreurs si OpenAI pas installé
        from openai import AsyncOpenAI  # pylint: disable=import-outside-toplevel

        api_key = config.get('openai', {}).get('api_key')
        if not api_key or not api_key.startswith('sk-'):
            return "❌ Tous les modèles locaux indisponibles et pas de clé OpenAI"

        # Métriques INPUT
        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")

        client = AsyncOpenAI(api_key=api_key)
        model = config['bot'].get('openai_model', 'gpt-3.5-turbo')
        system_prompt = load_system_prompt()

        # Démarrer le timer
        start_time = time.time()

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,  # Limite Twitch (500 chars) / 2
            temperature=0.7
        )

        # Calculer la durée
        duration = time.time() - start_time

        result = response.choices[0].message.content
        if result:
            result = result.strip()

            # Métriques OUTPUT
            output_chars = len(result)
            output_tokens = estimate_tokens(result)
            tokens_per_sec = output_tokens / duration if duration > 0 else 0

            print(f"[METRICS] 📤 OUTPUT: {output_chars} chars, ~{output_tokens} tokens")
            print(f"[METRICS] ⚡ Durée: {duration:.2f}s, {tokens_per_sec:.1f} tok/s")
            print(f"[MODEL] ✅ OPENAI fallback: {output_chars} caractères")
            return result
        return "❌ Réponse vide d'OpenAI"

    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        print(f"[MODEL] ❌ OpenAI fallback failed: {e}")
        return "💀 SerdaBot en mode survie ! Tous mes cerveaux sont KO. Revenez dans 2 min ! 🔄"
