# tools/test_chatml_chill.py
# --------------------------------------
# Test du comportement du modèle dans une conversation type Chill (multi-tours, relances autorisées)
# --------------------------------------

import asyncio

import httpx

API_URL = "http://127.0.0.1:8000/chat"

prompt_chill = """<|im_start|>system
Tu es un assistant IA présent dans un chat Twitch. Ton rôle est d’interagir de manière naturelle, détendue et 
accessible avec les spectateurs. Tu peux :
- Poser des questions de relance
- Donner des infos utiles sur les jeux vidéo
- Blaguer un peu, mais sans dérapage
- Toujours rester bienveillant et clair
<|im_end|>
<|im_start|>user
Salut l’IA, tu joues à quoi en ce moment ?
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
    await test_prompt(prompt_chill, "Prompt Chill — style conversation Twitch")


if __name__ == "__main__":
    asyncio.run(main())
