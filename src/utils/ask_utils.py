import httpx
from typing import Optional
from prompts.prompt_loader import load_prompt_template


def build_ask_prompt(user: str, question: str, max_length: int = 500) -> str:
    """Builds a clean prompt for an !ask command using the ask template."""
    try:
        template = load_prompt_template('ask', 'fr')
        prompt = template.replace('{question}', question.strip())
        prompt = prompt.replace('{max_length}', str(max_length))
        return prompt
    except Exception as e:
        print(f"[ASK_UTILS] ⚠️ Erreur chargement template: {e}")
        # Fallback basique
        return f"<|im_start|>system\nRéponds à la question de manière concise.<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"


def get_max_length(prefix: str, suffix: str, limit: int = 500) -> int:
    """Calculates available character space for content between prefix and suffix."""
    return max(0, limit - len(prefix) - len(suffix))


async def call_model(
    prompt: str, config: dict, user: str = None, timeout: int = 30
) -> str:
    """Queries the model using the configured endpoint with fallback."""
    
    # === PRIORITÉ 1: LM Studio ===
    api_url = config["bot"].get("model_endpoint") or config["bot"].get("api_url")
    if api_url and "1234" in api_url:
        print(f"[ASK_UTILS] 🔗 Tentative LM Studio: {api_url}")
        result = await try_endpoint(api_url, prompt, user, timeout, "lm_studio")
        if result:
            return result
        print("[ASK_UTILS] ⚠️ LM Studio indisponible, fallback...")
    
    # === PRIORITÉ 2: DeadBot FastAPI local (port 8080) ===
    deadbot_api = "http://127.0.0.1:8080/prompt"
    print(f"[ASK_UTILS] 🔗 Tentative DeadBot FastAPI: {deadbot_api}")
    result = await try_endpoint(deadbot_api, prompt, user, timeout, "deadbot")
    if result:
        return result
    print("[ASK_UTILS] ⚠️ DeadBot FastAPI indisponible, fallback...")
    
    # === PRIORITÉ 3: OpenAI API ===
    print("[ASK_UTILS] 🌐 Fallback vers OpenAI...")
    return await try_openai_fallback(prompt, config, user)


async def try_endpoint(api_url: str, prompt: str, user: str, timeout: int, endpoint_type: str) -> str:
    """Essaie un endpoint spécifique"""
    try:
        # Adapter le payload selon le type d'endpoint
        if endpoint_type == "lm_studio":
            payload = {
                "model": "local-model",
                "messages": [
                    {"role": "system", "content": "Tu es un assistant Twitch sympa et concis en français."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.7,
                "stream": False
            }
        else:
            # DeadBot FastAPI format
            payload = {"prompt": prompt}
            if user:
                payload["user"] = user

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and endpoint_type == "lm_studio":
                    result = data["choices"][0]["message"]["content"]
                elif "response" in data and endpoint_type == "deadbot":
                    result = data["response"]
                else:
                    result = data.get("response", "")
                
                print(f"[ASK_UTILS] ✅ {endpoint_type.upper()} réponse: {len(result)} chars")
                return result
            else:
                print(f"[ASK_UTILS] ❌ {endpoint_type.upper()} error: {response.status_code}")
                
    except Exception as e:
        print(f"[ASK_UTILS] ❌ {endpoint_type.upper()} failed: {type(e).__name__}")
    
    return ""


async def try_openai_fallback(prompt: str, config: dict, user: str) -> str:
    """Fallback vers OpenAI si tous les endpoints locaux échouent"""
    try:
        # Import dynamique pour éviter les erreurs si OpenAI pas installé
        from openai import AsyncOpenAI
        
        api_key = config.get('openai', {}).get('api_key')
        if not api_key or not api_key.startswith('sk-'):
            return "❌ Tous les modèles locaux indisponibles et pas de clé OpenAI"
        
        client = AsyncOpenAI(api_key=api_key)
        model = config['bot'].get('openai_model', 'gpt-3.5-turbo')
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Tu es un assistant Twitch sympa et concis en français."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"[ASK_UTILS] ✅ OPENAI fallback: {len(result)} caractères")
        return f"🌐 {result}"  # Indicateur de fallback OpenAI
        
    except Exception as e:
        print(f"[ASK_UTILS] ❌ OpenAI fallback failed: {e}")
        return "💀 SerdaBot en mode survie ! Tous mes cerveaux sont KO. Revenez dans 2 min ! 🔄"
