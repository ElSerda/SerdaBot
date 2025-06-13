from twitchio import Message
from utils.translation import detect_lang, translate


async def handle_trad_command(message: Message, config: dict, text: str, now):
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    target_lang = config["bot"].get("lang", "fr")  # par défaut vers le français

    if not text.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de fournir un message à traduire."
        )
        return

    source_lang = detect_lang(text)
    if source_lang == target_lang:
        await message.channel.send(
            f"@{user} Ton message est déjà en {target_lang.upper()}."
        )
        return

    translated = translate(text, to_lang=target_lang, from_lang=source_lang)

    if not translated:
        await message.channel.send(f"@{user} ❌ La traduction a échoué.")
        return

    await message.channel.send(
        f"📥 ({source_lang} → {target_lang}) : {translated.strip()}"
    )

    if debug:
        print(f"[TRAD] Original: {text}")
        print(f"[TRAD] Source: {source_lang}, Target: {target_lang}")
        print(f"[TRAD] Translated: {translated}")
