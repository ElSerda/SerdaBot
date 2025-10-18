"""Utility functions for AI model communication."""

import time
from datetime import datetime, timedelta

import httpx

from prompts.prompt_loader import load_system_prompt


# Configuration optimale des tokens par mode (validé empiriquement sur 98 tests)
# Qwen2.5-3B: 98.9% fiable, ~150 chars moyens, phrases complètes
# Test: 98/98 pytest PASS (validé Windows + Linux)
# Augmenté CHILL de 45→60 pour éviter phrases coupées (fix v1.1.1)
MAX_TOKENS_ASK = 120    # Headroom pour réponses 230-250 chars (évite cuts)
MAX_TOKENS_CHILL = 60   # Phrases complètes avec ponctuation (était 45)
TEMP_ASK = 0.4          # Déterministe pour faits
TEMP_CHILL = 0.7        # Créatif et naturel (synchro avec config.yaml)


def estimate_tokens(text: str) -> int:
    """Estime le nombre de tokens (approximatif: ~4 chars = 1 token pour FR/EN)"""
    return len(text) // 4

# Cache des endpoints down (évite de retenter inutilement)
_failed_endpoints = {}
_CACHE_DURATION = timedelta(minutes=2)  # Retest après 2 min


async def call_model(
    prompt: str, config: dict, user: str | None = None, timeout: int | None = None, mode: str = "chill"
) -> str:
    """Queries the model using the configured endpoint with fallback.
    
    Args:
        prompt: User prompt text
        config: Bot configuration
        user: Username (optional)
        timeout: Request timeout in seconds
        mode: Command mode ('ask' or 'chill') - determines system prompt and params
    """

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
        result = await try_endpoint(api_url, prompt, user, effective_timeout, "lm_studio", mode, config)
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
        result = await try_endpoint(deadbot_api, prompt, user, effective_timeout, "deadbot", mode, config)
        if result:
            return result
        _failed_endpoints[deadbot_api] = now
        print("[MODEL] ⚠️ DeadBot indisponible")
    else:
        print("[MODEL] ⏭️ DeadBot skip (down)")

    # === PRIORITÉ 3: OpenAI API ===
    print("[MODEL] 🌐 Fallback OpenAI...")
    return await try_openai_fallback(prompt, config, user, mode)


async def try_endpoint(
    api_url: str, prompt: str, user: str | None, timeout: int, endpoint_type: str, mode: str = "chill", config: dict | None = None
) -> str:
    """Essaie un endpoint spécifique
    
    Args:
        api_url: Endpoint URL
        prompt: User prompt
        user: Username
        timeout: Request timeout
        endpoint_type: Type ('lm_studio' or 'deadbot')
        mode: Command mode ('ask' or 'chill')
        config: Bot config (pour récupérer model_name)
    """
    try:
        # Métriques INPUT
        input_chars = len(prompt)
        input_tokens = estimate_tokens(prompt)
        print(f"[METRICS] 📥 INPUT: {input_chars} chars, ~{input_tokens} tokens")
        print(f"[DEBUG] 📄 USER Prompt: {prompt}")

        # Adapter le payload selon le type d'endpoint
        if endpoint_type == "lm_studio":
            # Charger le bon system prompt selon le mode passé en paramètre
            system_prompt = load_system_prompt(mode=mode)
            print(f"[DEBUG] 🧠 SYSTEM Prompt ({len(system_prompt)} chars, mode={mode}): {system_prompt[:100]}...")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Config depuis constantes
            max_tokens = MAX_TOKENS_ASK if mode == "ask" else MAX_TOKENS_CHILL
            temperature = TEMP_ASK if mode == "ask" else TEMP_CHILL
            repeat_penalty = 1.1 if mode == "ask" else 1.0
            
            # Récupère le nom du modèle depuis la config
            model_name = config.get("bot", {}).get("model_name", "local-model") if config else "local-model"
            
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "repeat_penalty": repeat_penalty,
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
                
                # Alerte si dépassement (mode ask uniquement)
                if mode == "ask" and output_chars > 250:
                    print(f"[⚠️] Réponse trop longue ({output_chars} chars) !")
                
                # Afficher output complet sur plusieurs lignes si nécessaire
                print(f"[DEBUG] 💬 OUTPUT:")
                print(f"   {result}")
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
    prompt: str, config: dict, user: str | None, mode: str = "chill"  # pylint: disable=unused-argument
) -> str:
    """Fallback vers OpenAI (GPT-4o-mini) si tous les endpoints locaux échouent.
    
    Args:
        prompt: User prompt
        config: Bot configuration
        user: Username (unused)
        mode: Command mode ('ask' or 'chill')
    
    GPT-4o-mini choisi pour:
    - 100% succès ASK + CHILL validé
    - 4x moins cher que GPT-3.5-turbo ($0.15/$0.60 vs $0.50/$1.50 par 1M tokens)
    - Latence acceptable pour fallback (0.57-1.52s)
    """
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
        model = config['bot'].get('openai_model', 'gpt-4o-mini')  # Fallback optimal (100% succès, 4x moins cher)
        
        # Charger le bon system prompt selon le mode passé en paramètre
        system_prompt = load_system_prompt(mode=mode)

        # Démarrer le timer
        start_time = time.time()

        # Config depuis constantes
        max_tokens = MAX_TOKENS_ASK if mode == "ask" else MAX_TOKENS_CHILL
        temperature = TEMP_ASK if mode == "ask" else TEMP_CHILL
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
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
