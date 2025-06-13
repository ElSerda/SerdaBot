import os
import time
from typing import Optional

from ctransformers import AutoModelForCausalLM

from config.config import load_config
from utils.clean import clean_response

MODEL = None
CONFIG = load_config()


# === Fonction : Chargement du modèle ===
def load_model(config: Optional[dict] = None):
    global MODEL

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
        MODEL = AutoModelForCausalLM.from_pretrained(
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
    prompt: str, config: Optional[dict] = None, user: Optional[str] = None
) -> str:
    global MODEL

    if config is None:
        config = CONFIG

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
