import argparse
import json

import httpx

API_URL = "http://127.0.0.1:8000/chat"


def main(prompt: str, type_: str, debug: bool = False):
    payload = {"prompt": prompt, "type": type_}

    if debug:
        print(
            f"[DEBUG] ➜ Requête envoyée (payload JSON) :\n{json.dumps(payload, indent=2)}"
        )

    try:
        r = httpx.post(API_URL, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()

        raw_response = data.get("response", "").strip()

        print("\n=== Résultat IA ===")
        print(f'🔹 Prompt envoyé : "{prompt}" ({len(prompt)} caractères)')
        print(f"🔹 Type : {type_}")
        print("\n🔹 Réponse brute :")
        print(raw_response)
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test SerdaBot local API")
    parser.add_argument("--prompt", required=True, help="Message à envoyer")
    parser.add_argument(
        "--type", default="chill", help="Type de commande (chill/ask/game)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Afficher les détails de la requête"
    )

    args = parser.parse_args()
    main(args.prompt, args.type, args.debug)
