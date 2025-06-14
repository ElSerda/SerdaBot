
import requests

def postprocess_translation(text: str, config: dict) -> str:
    """
    Réécrit le texte en français naturel et fluide, sans changer le sens,
    en utilisant un modèle Mistral local via un endpoint.
    """
    endpoint = config["bot"].get("model_endpoint")
    if not endpoint:
        return text

    payload = {
        "messages": [
            {"role": "system", "content": "Réécris ce texte en français naturel, fluide, sans changer le sens. Corrige les fautes de style ou répétitions."},
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("content", text).strip()
        else:
            print(f"[POSTPROCESS] ⚠️ Échec requête HTTP {response.status_code}")
    except Exception as e:
        print(f"[POSTPROCESS] ❌ Erreur : {e}")

    return text
