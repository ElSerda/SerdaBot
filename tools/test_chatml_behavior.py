# tools/test_chatml_deep.py
# --------------------------------------
# Tests avancés pour évaluer la discipline du modèle avec prompts de type ChatML
# --------------------------------------

import asyncio

import httpx

API_URL = "http://127.0.0.1:8000/chat"

# Prompt A — Simule !ask avec réponse en une seule phrase
prompt_ask = """<|im_start|>system
Tu es un assistant IA intégré à un chat Twitch. Quand un utilisateur pose une question, tu réponds toujours :
- En une seule phrase
- Sans emojis, décor, ni relance
- En moins de 400 caractères
<|im_end|>
<|im_start|>user
À quoi sert la compétence Perception dans Baldur’s Gate 3 ?
<|im_end|>
<|im_start|>assistant
"""

# Prompt B — Simule !game avec résumé brut à nettoyer
prompt_game = """<|im_start|>system
Tu es une IA qui résume des descriptions de jeux. Tu dois :
- Ne jamais répéter le nom du jeu
- Ne pas ajouter de décor
- Nettoyer les descriptions inutiles
<|im_end|>
<|im_start|user
Cyberpunk 2077: Ultimate Edition : is an open-world RPG containing two powerful adventures: the base game of 
Cyberpunk 2077,
 taking place in the dark future of Night City, and Phantom Liberty, a spy-thriller story set in the walled-off district 
 of Dogtown. Players take on the role of V, a cyber-enhanced mercenary, and embark on a fight for survival filled with 
 story-defining decisions, action-packed gameplay, and unforgettable characters.
<|im_end|>
<|im_start|>assistant
"""

# Prompt C — Simule !trad avec consigne stricte
prompt_trad = """<|im_start|>system
Tu es un traducteur IA. Tu dois :
- Traduire fidèlement vers le français
- Ne jamais reformuler, corriger ou commenter
- Répondre uniquement avec la traduction
<|im_end|>
<|im_start|user
This game lets you explore alien worlds with your friends in co-op mode.
<|im_end|>
<|im_start|>assistant
"""


# Fonction d'envoi des prompts
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


# Fonction principale
async def main():
    await test_prompt(prompt_ask, "Prompt A — !ask (1 phrase)")
    await test_prompt(prompt_game, "Prompt B — !game (résumé à nettoyer)")
    await test_prompt(prompt_trad, "Prompt C — !trad (traduction stricte)")


if __name__ == "__main__":
    asyncio.run(main())
