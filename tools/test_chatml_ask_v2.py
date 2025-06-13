# tools/test_chatml_ask_v2.py
# --------------------------------------
# Test strict pour la commande !ask (réponse en une seule phrase, pas de relance, décor ni dialogue)
# --------------------------------------

import asyncio

import httpx

API_URL = "http://127.0.0.1:8000/chat"

prompt_strict_ask = """<|im_start|>system
Tu es un assistant IA intégré dans un chat Twitch. Tu dois :
- Répondre en une seule phrase claire
- Ne jamais reformuler la question
- Ne jamais relancer ou dialoguer
- Ne jamais ajouter de décor, intro ou outro
- Ne jamais dépasser 400 caractères
- Répondre uniquement à la question de l'utilisateur
<|im_end|>
<|im_start|>user
À quoi sert la compétence Perception dans Baldur’s Gate 3 ?
<|im_end|>
<|im_start|>assistant
"""


async def test_prompt(prompt, label):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json={"prompt": prompt}, timeout=30)
            if response.status_code == 200:
                print(f"\n🧪 {label}")
                print(response.json().get("response"))
            else:
                print(f"\n⚠️ Erreur {label} : {response.status_code} - {response.text}")
        except Exception as e:
            print(f"\n❌ Exception {label} : {e}")


async def main():
    await test_prompt(prompt_strict_ask, "Prompt !ask — réponse stricte")


if __name__ == "__main__":
    asyncio.run(main())
