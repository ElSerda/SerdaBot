import os
import time
from typing import Optional

# Import ctransformers avec gestion d'erreur (optionnel pour GGUF local)
try:
    from ctransformers import AutoModelForCausalLM
    CTRANSFORMERS_AVAILABLE = True
except ImportError:
    CTRANSFORMERS_AVAILABLE = False
    AutoModelForCausalLM = None
    print("⚠️ Module 'ctransformers' non installé. Installation avec: pip install ctransformers")

from config.config import load_config
from utils.clean import clean_response

# Import OpenAI avec gestion d'erreur
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ Module 'openai' non installé. Installation avec: pip install openai")

MODEL = None
OPENAI_CLIENT = None
CONFIG = load_config()


# === Fonction : Chargement du modèle ===
def load_model(config: Optional[dict] = None):
    global MODEL

    if not CTRANSFORMERS_AVAILABLE:
        print("❌ ctransformers non disponible. Impossible de charger un modèle GGUF local.")
        return

    if config is None:
        config = CONFIG

    try:
        model_path = config['bot']['model_path']
        model_file = config['bot']['model_file']
        use_gpu = config['bot'].get('use_gpu', False)
        gpu_layers = config['bot'].get('gpu_layers', 0)
    except KeyError as e:
        print(f'❌ [ERREUR] Clé manquante dans config.yaml : {e}')
        return

    full_path = os.path.join(model_path, os.path.basename(model_file))

    if not os.path.isfile(full_path):
        print(f'❌ Fichier modèle introuvable : {full_path}')
        return

    try:
        print(f'📥 Chargement modèle depuis : {full_path}')
        MODEL = AutoModelForCausalLM.from_pretrained(  # type: ignore
            full_path,
            model_type=config['bot'].get('model_type', 'mistral'),
            gpu_layers=gpu_layers if use_gpu else 0,
        )
        print(f'🧠 Modèle chargé localement sur : {"GPU" if use_gpu else "CPU"}')
    except Exception as e:
        print(f'❌ Erreur lors du chargement du modèle : {e}')
        MODEL = None


# === Fonction : Requête au modèle ===
async def query_model(
    prompt: str, config: Optional[dict] = None
) -> str:
    global MODEL, OPENAI_CLIENT

    if config is None:
        config = CONFIG

    # === PRIORITÉ 1: Tester endpoint externe (LM Studio) ===
    external_endpoint = config['bot'].get('model_endpoint') or config['bot'].get('api_url')
    if external_endpoint:
        try:
            import httpx

            # Test rapide LM Studio
            test_payload = {"model": "test", "messages": [{"role": "user", "content": "test"}], "max_tokens": 1}

            with httpx.Client(timeout=3) as client:
                response = client.post(external_endpoint, json=test_payload)

                if response.status_code in [200, 400]:  # 400 = pas de modèle mais endpoint ok
                    print("🔗 [LM STUDIO] Endpoint actif")

                    # Vraie requête vers LM Studio (optimisé pour Twitch)
                    real_payload = {
                        "model": "local-model",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Bot Twitch FR. Réponds en UNE phrase max (12-25 mots). "
                                    "Ton fun et complice. Pas d'auto-flatterie. 0-2 émojis max. "
                                    "Pas de listes, pas de !!!, pas de citations longues."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 60,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "presence_penalty": 0.6,
                        "frequency_penalty": 0.4,
                        "stop": ["\n", "User:", "Assistant:", "@"]
                    }

                    real_response = client.post(external_endpoint, json=real_payload)
                    if real_response.status_code == 200:
                        result = real_response.json()
                        return result['choices'][0]['message']['content'].strip()

        except Exception:
            print("⚠️ [FALLBACK] LM Studio indisponible")

    print("🌐 [FALLBACK] Utilisation d'OpenAI...")
    model_type = config['bot'].get('model_type', 'mistral')

    # === Utilisation d'OpenAI ===
    if model_type == 'openai':
        if not OPENAI_AVAILABLE:
            return '❌ OpenAI non disponible. Installez avec: pip install openai'

        if OPENAI_CLIENT is None:
            api_key = config.get('openai', {}).get('api_key')
            if not api_key or api_key == 'your_openai_api_key_here':
                return '❌ Clé OpenAI manquante dans config.yaml'
            OPENAI_CLIENT = AsyncOpenAI(api_key=api_key)

        try:
            start = time.time()
            openai_model = config['bot'].get('openai_model', 'gpt-3.5-turbo')

            # Parser le format ChatML si présent
            messages = []
            if '<|im_start|>' in prompt:
                # Format ChatML détecté
                import re
                parts = re.split(r'<\|im_start\|>(\w+)\n', prompt)
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        role = parts[i]
                        content = parts[i+1].split('<|im_end|>')[0].strip()
                        if role in ['system', 'user', 'assistant'] and content:
                            messages.append({"role": role, "content": content})
            else:
                # Format simple : prompt direct
                messages = [
                    {"role": "system", "content": "Tu es un assistant Twitch sympa et concis. Réponds en français de manière courte et engageante."},
                    {"role": "user", "content": prompt}
                ]

            if config.get('debug', False):
                print(f'[DEBUG] 📝 Messages parsés : {messages}')

            # Type cast pour satisfaire mypy/pylance
            response = await OPENAI_CLIENT.chat.completions.create(
                model=openai_model,
                messages=messages,  # type: ignore
                max_tokens=400,
                temperature=0.7
            )

            elapsed = round(time.time() - start, 2)
            result = response.choices[0].message.content
            if result is None:
                return "⚠️ Réponse vide de l'IA"
            result = result.strip()

            if config.get('debug', False):
                print(f'[DEBUG] 🤖 OpenAI ({openai_model}) réponse en {elapsed}s')
                print(f'[DEBUG] ➜ Réponse : {result}')

            return result

        except Exception as e:
            error_str = str(e).lower()
            print(f'❌ Erreur OpenAI : {e}')

            # Gestion spécifique des erreurs courantes
            if 'quota' in error_str or 'insufficient' in error_str or 'billing' in error_str:
                print('🚨 [FALLBACK] Quota OpenAI épuisé! Passage en mode local...')
                # Fallback vers modèle local si disponible
                if MODEL is not None:
                    print('🔄 [FALLBACK] Utilisation du modèle local...')
                    try:
                        raw_output = MODEL(prompt, max_new_tokens=400)
                        response = clean_response(''.join(raw_output), max_length=400)
                        return f"🧠 (Local) {response}"
                    except Exception:
                        return "⚠️ IA temporairement indisponible. Essayez plus tard !"
                else:
                    return "⚠️ Quota IA épuisé. Service temporairement indisponible !"

            elif 'rate limit' in error_str or 'too many requests' in error_str:
                return "⚠️ Trop de requêtes. Attendez quelques secondes et réessayez !"

            elif 'invalid api key' in error_str or 'authentication' in error_str:
                print('🚨 [CONFIG] Clé API OpenAI invalide!')
                return "⚠️ Problème de configuration IA. Contactez l'admin !"

            elif 'network' in error_str or 'timeout' in error_str or 'connection' in error_str:
                return "⚠️ Problème de connexion. Réessayez dans un moment !"

            else:
                import traceback
                traceback.print_exc()
                return '⚠️ Service IA temporairement indisponible !'

    # === Utilisation du modèle local (ctransformers) ===
    if MODEL is None:
        print('⚠️ Modèle non initialisé, tentative de chargement...')
        load_model(config)

    if config.get('debug', False):
        if MODEL is None:
            print('⚠️ [DEBUG] Aucun modèle chargé.')
        else:
            print('✅ [DEBUG] Modèle actif et prêt à générer.')

    if MODEL is None:
        return f'🧠 Echo: {prompt}'

    max_tokens = 400
    try:
        start = time.time()
        raw_output = MODEL(prompt, max_new_tokens=max_tokens)
        elapsed = round(time.time() - start, 2)
    except Exception as e:
        print(f'❌ Erreur génération : {e}')
        return '🧠 Erreur : le modèle ne répond pas.'

    raw_output_text = ''.join(raw_output)
    response = clean_response(raw_output_text, max_length=max_tokens)

    if config.get('debug', False):
        print(f'[DEBUG] ➜ Réponse brute générée : {raw_output_text}')
        print(f'[DEBUG] ⏱️ Réponse en {elapsed}s')
        print(f'[DEBUG] ➜ Prompt : {prompt}')
        print(f'[DEBUG] ➜ Réponse : {response}')

    return response
