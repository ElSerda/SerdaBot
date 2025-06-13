from twitchio import Message
from utils.chill_utils import build_chill_prompt, call_model, truncate_response


async def handle_chill_command(message: Message, config: dict, now):
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)

    prompt = build_chill_prompt(message, botname)
    response = await call_model(prompt, config)

    if not response:
        await message.channel.send("🤷 Réponse manquante.")
        return

    final = truncate_response(response.strip())
    await message.channel.send(final)

    if debug:
        print(f"[CHILL] Prompt: {prompt}")
        print(f"[CHILL] Final: {final}")
