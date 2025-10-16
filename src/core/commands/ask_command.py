from twitchio import Message
from utils.ask_utils import build_ask_prompt, call_model


async def handle_ask_command(message: Message, config: dict, question: str, now):
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)

    if not question.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de poser ta question après `!ask`."
        )
        if debug:
            print(f"[ASK] ⚠️ Question vide reçue de @{user}")
        return

    # Message "Recherche en cours" supprimé pour économiser la limite de rate du bot non vérifié
    if debug:
        print(f"[ASK] 🔎 Traitement de la question de @{user}...")

    prompt = build_ask_prompt(user, question)
    response = await call_model(prompt, config, user=user)

    if not response:
        await message.channel.send(f"@{user} ⚠️ Erreur ou pas de réponse.")
        return

    final_response = response.strip()
    if len(final_response) > 500:
        final_response = final_response[:497] + "…"

    await message.channel.send(f"@{user} {final_response}")

    if debug:
        print(f"[ASK] ✅ Réponse envoyée à @{user}")
